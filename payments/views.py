from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Payment, PaymentMethod, PaymentStatus
from orders.models import Order


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
            messages.success(request, 'Payment status updated. We will verify your payment.')
        else:
            messages.error(request, 'Transaction ID is required')
    
    return redirect('payments:payment_detail', payment_id=payment.id)
