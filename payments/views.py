from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
import logging
from .models import Payment, PaymentMethod, PaymentStatus
from .gateways import PaymentGatewayService, PaymentGatewayError
from orders.models import Order

logger = logging.getLogger(__name__)


@login_required
def payment_confirmation(request, payment_id):
    """Payment confirmation page after order placement"""
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    order = payment.order
    
    context = {
        'payment': payment,
        'order': order,
    }
    return render(request, 'payments/payment_confirmation.html', context)


@login_required
def payment_history(request):
    """Payment history for user"""
    from django.core.paginator import Paginator
    
    payments = Payment.objects.filter(order__user=request.user).select_related('order').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(payments, 20)  # 20 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'payments': page_obj,  # For backward compatibility
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
def payment_detail(request, payment_id):
    """Payment detail page"""
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    order = payment.order
    order_items = order.items.select_related('menu_item').all()
    
    context = {
        'payment': payment,
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'payments/payment_detail.html', context)


@login_required
def receipt_pdf(request, payment_id):
    """Generate receipt/invoice as PDF (or HTML for now)"""
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    order = payment.order
    order_items = order.items.select_related('menu_item').all()
    
    context = {
        'payment': payment,
        'order': order,
        'order_items': order_items,
    }
    
    # For now, return HTML receipt (can be converted to PDF later)
    html = render_to_string('payments/receipt.html', context)
    response = HttpResponse(html)
    response['Content-Type'] = 'text/html'
    return response


@login_required
def update_payment_status(request, payment_id):
    """Update payment status (for mobile money, bank transfer confirmations)"""
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id', '')
        if transaction_id:
            payment.transaction_id = transaction_id
            payment.status = PaymentStatus.PROCESSING
            payment.save()
            
            # Verify payment with gateway if applicable
            if payment.payment_method in [PaymentMethod.MTN_MOBILE_MONEY, PaymentMethod.AIRTEL_MONEY]:
                try:
                    result = PaymentGatewayService.verify_payment(payment, transaction_id)
                    if result.get('status') == 'completed':
                        messages.success(request, 'Payment verified and completed!')
                    else:
                        messages.info(request, 'Payment status updated. We will verify your payment.')
                except Exception as e:
                    logger.error(f"Payment verification error: {str(e)}")
                    messages.info(request, 'Payment status updated. We will verify your payment.')
            else:
                messages.success(request, 'Payment status updated. We will verify your payment.')
        else:
            messages.error(request, 'Transaction ID is required')
    
    return redirect('payments:payment_detail', payment_id=payment.id)


@login_required
@require_http_methods(["POST"])
def verify_payment(request, payment_id):
    """Verify payment status with payment gateway"""
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    
    # Only verify if payment method uses a gateway
    if payment.payment_method == PaymentMethod.CASH_ON_DELIVERY:
        return JsonResponse({'error': 'Cash on delivery does not require verification'}, status=400)
    
    try:
        result = PaymentGatewayService.verify_payment(payment)
        
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'status': result.get('status'),
                'message': 'Payment verified successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'status': result.get('status'),
                'message': result.get('error', 'Payment verification failed')
            })
            
    except PaymentGatewayError as e:
        logger.error(f"Payment verification error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Unexpected verification error: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred during verification'}, status=500)


@login_required
def payment_callback(request):
    """Handle payment callback from payment gateway"""
    transaction_id = request.GET.get('tx_ref') or request.GET.get('transaction_id')
    status = request.GET.get('status', '').lower()
    
    if not transaction_id:
        messages.error(request, 'Invalid payment callback')
        return redirect('payments:payment_history')
    
    # Extract payment ID from transaction reference
    # Format: ORDER_ORDER_NUMBER_PAYMENT_ID
    try:
        if transaction_id.startswith('ORDER_'):
            parts = transaction_id.split('_')
            if len(parts) >= 3:
                payment_id = parts[-1]
                payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
                
                # Verify payment status
                if status == 'successful' or status == 'success':
                    try:
                        result = PaymentGatewayService.verify_payment(payment, transaction_id)
                        if result.get('status') == 'completed':
                            messages.success(request, 'Payment completed successfully!')
                            return redirect('payments:payment_detail', payment_id=payment.id)
                    except Exception as e:
                        logger.error(f"Callback verification error: {str(e)}")
                
                return redirect('payments:payment_detail', payment_id=payment.id)
    except (ValueError, Payment.DoesNotExist):
        pass
    
    messages.error(request, 'Payment not found')
    return redirect('payments:payment_history')
