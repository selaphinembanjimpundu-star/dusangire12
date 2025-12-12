from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def cart(request):
    """Shopping cart view - Phase 3"""
    return render(request, 'orders/cart.html', {
        'message': 'Shopping cart will be available in Phase 3'
    })


@login_required
def order_history(request):
    """Order history view - Phase 3"""
    return render(request, 'orders/order_history.html', {
        'message': 'Order history will be available in Phase 3'
    })
