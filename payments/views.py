from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.db.models import Q
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


# ============================================================================
# SELF-SERVICE PAYMENT PROCESSING VIEWS
# Allows users to process payments themselves through multiple payment methods
# ============================================================================

@login_required
def checkout(request):
    """
    Self-service checkout page where users can select payment method
    and process payment for pending orders
    """
    # Get pending payments for the user
    pending_payments = Payment.objects.filter(
        order__user=request.user,
        status=PaymentStatus.PENDING
    ).select_related('order').order_by('-created_at')
    
    # Get available payment methods
    payment_methods = PaymentMethod.choices
    
    context = {
        'pending_payments': pending_payments,
        'payment_methods': payment_methods,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def initiate_payment(request, payment_id):
    """
    User initiates payment processing for a specific payment
    Allows selection of payment method
    """
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    order = payment.order
    
    # Only allow payment initiation if payment is pending
    if payment.status != PaymentStatus.PENDING:
        messages.warning(request, 'This payment has already been processed.')
        return redirect('payments:payment_detail', payment_id=payment.id)
    
    if request.method == 'POST':
        selected_method = request.POST.get('payment_method')
        
        if selected_method not in dict(PaymentMethod.choices):
            messages.error(request, 'Invalid payment method selected.')
            return redirect('payments:initiate_payment', payment_id=payment.id)
        
        # Save selected payment method
        payment.payment_method = selected_method
        payment.status = PaymentStatus.PROCESSING
        payment.save()
        
        # Redirect to appropriate payment processor
        if selected_method == PaymentMethod.CASH_ON_DELIVERY:
            return redirect('payments:process_cash_on_delivery', payment_id=payment.id)
        elif selected_method == PaymentMethod.MTN_MOBILE_MONEY:
            return redirect('payments:process_mtn_money', payment_id=payment.id)
        elif selected_method == PaymentMethod.AIRTEL_MONEY:
            return redirect('payments:process_airtel_money', payment_id=payment.id)
        elif selected_method == PaymentMethod.BANK_TRANSFER:
            return redirect('payments:process_bank_transfer', payment_id=payment.id)
        elif selected_method == PaymentMethod.CARD:
            return redirect('payments:process_card_payment', payment_id=payment.id)
    
    context = {
        'payment': payment,
        'order': order,
        'payment_methods': PaymentMethod.choices,
    }
    return render(request, 'payments/initiate_payment.html', context)


@login_required
def process_cash_on_delivery(request, payment_id):
    """
    Process cash on delivery payment
    No transaction needed, just confirm delivery method
    """
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    
    if request.method == 'POST':
        # Mark payment as pending cash on delivery
        payment.payment_method = PaymentMethod.CASH_ON_DELIVERY
        payment.status = PaymentStatus.PENDING
        payment.save()
        
        messages.success(request, 'Order confirmed for cash on delivery. Our staff will collect payment upon delivery.')
        return redirect('payments:payment_confirmation', payment_id=payment.id)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'payments/payment_methods/cash_on_delivery.html', context)


@login_required
def process_mtn_money(request, payment_id):
    """
    Process MTN Mobile Money payment
    User enters phone number and transaction is initiated
    """
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        
        if not phone_number:
            messages.error(request, 'Phone number is required.')
            return redirect('payments:process_mtn_money', payment_id=payment.id)
        
        try:
            # Initiate payment with MTN Mobile Money gateway
            gateway_result = PaymentGatewayService.initiate_mtn_payment(
                payment=payment,
                phone_number=phone_number
            )
            
            if gateway_result.get('success'):
                payment.transaction_id = gateway_result.get('transaction_id')
                payment.status = PaymentStatus.PROCESSING
                payment.save()
                
                messages.info(
                    request,
                    f'Payment initiated. Please enter your MTN PIN on your phone to complete the transaction.'
                )
                return redirect('payments:payment_awaiting_confirmation', payment_id=payment.id)
            else:
                messages.error(
                    request,
                    gateway_result.get('error', 'Failed to initiate MTN payment.')
                )
                return redirect('payments:process_mtn_money', payment_id=payment.id)
                
        except PaymentGatewayError as e:
            logger.error(f"MTN payment initiation error: {str(e)}")
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('payments:process_mtn_money', payment_id=payment.id)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'payments/payment_methods/mtn_money.html', context)


@login_required
def process_airtel_money(request, payment_id):
    """
    Process Airtel Money payment
    User enters phone number and transaction is initiated
    """
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        
        if not phone_number:
            messages.error(request, 'Phone number is required.')
            return redirect('payments:process_airtel_money', payment_id=payment.id)
        
        try:
            # Initiate payment with Airtel Money gateway
            gateway_result = PaymentGatewayService.initiate_airtel_payment(
                payment=payment,
                phone_number=phone_number
            )
            
            if gateway_result.get('success'):
                payment.transaction_id = gateway_result.get('transaction_id')
                payment.status = PaymentStatus.PROCESSING
                payment.save()
                
                messages.info(
                    request,
                    'Payment initiated. Please check your Airtel account for a prompt and complete the transaction.'
                )
                return redirect('payments:payment_awaiting_confirmation', payment_id=payment.id)
            else:
                messages.error(
                    request,
                    gateway_result.get('error', 'Failed to initiate Airtel payment.')
                )
                return redirect('payments:process_airtel_money', payment_id=payment.id)
                
        except PaymentGatewayError as e:
            logger.error(f"Airtel payment initiation error: {str(e)}")
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('payments:process_airtel_money', payment_id=payment.id)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'payments/payment_methods/airtel_money.html', context)


@login_required
def process_bank_transfer(request, payment_id):
    """
    Process bank transfer payment
    Shows bank account details and awaits payment confirmation
    """
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    
    if request.method == 'POST':
        transaction_ref = request.POST.get('transaction_ref', '').strip()
        
        if not transaction_ref:
            messages.error(request, 'Transaction reference is required.')
            return redirect('payments:process_bank_transfer', payment_id=payment.id)
        
        # Save bank transfer reference
        payment.transaction_id = transaction_ref
        payment.status = PaymentStatus.PROCESSING
        payment.save()
        
        messages.info(
            request,
            'Bank transfer payment recorded. We will verify your payment within 24 hours.'
        )
        return redirect('payments:payment_awaiting_confirmation', payment_id=payment.id)
    
    context = {
        'payment': payment,
        'order': payment.order,
        # Bank details would be loaded from settings
    }
    return render(request, 'payments/payment_methods/bank_transfer.html', context)


@login_required
def process_card_payment(request, payment_id):
    """
    Process card payment (credit/debit card)
    Integrates with Flutterwave or other payment gateway
    """
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    
    if request.method == 'POST':
        try:
            # Initiate card payment through gateway
            gateway_result = PaymentGatewayService.initiate_card_payment(payment=payment)
            
            if gateway_result.get('success'):
                payment.transaction_id = gateway_result.get('transaction_id')
                payment.status = PaymentStatus.PROCESSING
                payment.save()
                
                # Redirect to gateway payment page
                return redirect(gateway_result.get('payment_url'))
            else:
                messages.error(
                    request,
                    gateway_result.get('error', 'Failed to initiate card payment.')
                )
                return redirect('payments:process_card_payment', payment_id=payment.id)
                
        except PaymentGatewayError as e:
            logger.error(f"Card payment initiation error: {str(e)}")
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('payments:process_card_payment', payment_id=payment.id)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'payments/payment_methods/card_payment.html', context)


@login_required
def payment_awaiting_confirmation(request, payment_id):
    """
    Page shown while awaiting payment confirmation
    Allows user to check payment status or cancel
    """
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    
    if request.method == 'POST':
        if 'check_status' in request.POST:
            # Check payment status
            try:
                result = PaymentGatewayService.verify_payment(payment)
                if result.get('status') == 'completed':
                    payment.status = PaymentStatus.COMPLETED
                    payment.save()
                    messages.success(request, 'Payment confirmed successfully!')
                    return redirect('payments:payment_detail', payment_id=payment.id)
                else:
                    messages.info(request, 'Payment status is still being verified. Please check again shortly.')
            except Exception as e:
                logger.error(f"Status check error: {str(e)}")
                messages.warning(request, 'Could not verify payment status. Please try again.')
        
        elif 'cancel' in request.POST:
            # Cancel payment
            payment.status = PaymentStatus.CANCELLED
            payment.save()
            messages.info(request, 'Payment cancelled. You can try again later.')
            return redirect('payments:checkout')
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'payments/payment_awaiting_confirmation.html', context)


@login_required
@require_http_methods(["POST"])
def retry_payment(request, payment_id):
    """
    Retry payment for a failed transaction
    User can select a different payment method
    """
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    
    if payment.status not in [PaymentStatus.FAILED, PaymentStatus.CANCELLED]:
        messages.warning(request, 'This payment cannot be retried.')
        return redirect('payments:payment_detail', payment_id=payment.id)
    
    # Reset payment status and clear transaction ID
    payment.status = PaymentStatus.PENDING
    payment.transaction_id = ''
    payment.payment_method = ''
    payment.save()
    
    messages.info(request, 'Payment reset. Please select a payment method and try again.')
    return redirect('payments:initiate_payment', payment_id=payment.id)


@login_required
def payment_methods_list(request):
    """
    Display all available payment methods for the user
    """
    payment_methods = PaymentMethod.choices
    
    # Check which payment methods are available (based on app configuration)
    available_methods = []
    for code, label in payment_methods:
        available_methods.append({
            'code': code,
            'label': label,
            'description': get_payment_method_description(code)
        })
    
    context = {
        'available_methods': available_methods,
    }
    return render(request, 'payments/payment_methods_list.html', context)


def get_payment_method_description(method_code):
    """Get description for a payment method"""
    descriptions = {
        PaymentMethod.CASH_ON_DELIVERY: 'Pay when the order is delivered to you',
        PaymentMethod.MTN_MOBILE_MONEY: 'Pay using your MTN Mobile Money account',
        PaymentMethod.AIRTEL_MONEY: 'Pay using your Airtel Money account',
        PaymentMethod.BANK_TRANSFER: 'Transfer funds to our bank account',
        PaymentMethod.CARD: 'Pay using your credit or debit card',
    }
    return descriptions.get(method_code, 'Payment method')
