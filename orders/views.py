from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal
from menu.models import MenuItem
from delivery.models import DeliveryAddress, DeliveryZone
from payments.models import Payment, PaymentMethod, PaymentStatus
from .models import Cart, CartItem, Order, OrderItem, OrderStatus


def get_or_create_cart(user):
    """Get or create cart for user"""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def add_to_cart(request, item_id):
    """Add item to cart"""
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1:
            messages.error(request, 'Quantity must be at least 1')
            return redirect('menu:menu_detail', item_id=item_id)
        
        cart = get_or_create_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{menu_item.name} added to cart!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{menu_item.name} added to cart!',
                'cart_count': cart.get_item_count()
            })
        
        return redirect('orders:cart')
    
    return redirect('menu:menu_list')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    menu_item_name = cart_item.menu_item.name
    cart_item.delete()
    
    messages.success(request, f'{menu_item_name} removed from cart')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = get_or_create_cart(request.user)
        return JsonResponse({
            'success': True,
            'message': f'{menu_item_name} removed from cart',
            'cart_count': cart.get_item_count(),
            'cart_total': str(cart.get_total())
        })
    
    return redirect('orders:cart')


@login_required
def update_cart_item(request, item_id):
    """Update quantity of cart item"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1:
            cart_item.delete()
            messages.success(request, 'Item removed from cart')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated')
        
        cart = get_or_create_cart(request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': cart.get_item_count(),
                'cart_total': str(cart.get_total()),
                'item_subtotal': str(cart_item.get_subtotal())
            })
        
        return redirect('orders:cart')
    
    return redirect('orders:cart')


@login_required
def cart(request):
    """Display shopping cart"""
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.select_related('menu_item').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart.get_total(),
        'cart_count': cart.get_item_count(),
    }
    return render(request, 'orders/cart.html', context)


@login_required
def checkout(request):
    """Checkout page with delivery address selection and loyalty integration"""
    from accounts.validators import validate_user_can_make_payment
    from .services import OrderCalculationService
    
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.select_related('menu_item').all()
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('orders:cart')
    
    # Get user delivery addresses
    delivery_addresses = DeliveryAddress.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    default_address = delivery_addresses.filter(is_default=True).first()
    
    # Ensure user has at least one address
    if not delivery_addresses.exists():
        messages.warning(request, 'Please add a delivery address before checking out')
        return redirect('delivery:address_create')
    
    # Get user profile for default values
    profile = getattr(request.user, 'profile', None)
    
    # Get loyalty info for user
    loyalty_info = OrderCalculationService.get_user_loyalty_info(request.user)
    
    if request.method == 'POST':
        loyalty_points_to_redeem = int(request.POST.get('loyalty_points_redeem', 0))
        pricing = OrderCalculationService.calculate_order_total(cart, request.user, loyalty_points_to_redeem)
        
        payment_method = request.POST.get('payment_method', PaymentMethod.CASH_ON_DELIVERY)
        phone_number = request.POST.get('phone_number', '').strip()
        account_number = request.POST.get('account_number', '').strip()
        
        # Get selected delivery address
        saved_address_id = request.POST.get('saved_address_id')
        
        if not saved_address_id:
            messages.error(request, 'Please select a delivery address')
            context = {
                'cart': cart,
                'cart_items': cart_items,
                'delivery_addresses': delivery_addresses,
                'default_address': default_address,
                'profile': profile,
                'loyalty_info': loyalty_info,
                'pricing': pricing,
            }
            return render(request, 'orders/checkout.html', context)
        
        # Get the saved address
        try:
            delivery_address_obj = DeliveryAddress.objects.get(id=saved_address_id, user=request.user)
        except DeliveryAddress.DoesNotExist:
            messages.error(request, 'Selected address not found')
            return redirect('orders:checkout')
        
        validation_result = validate_user_can_make_payment(
            request.user,
            payment_method,
            phone_number if phone_number else None,
            account_number if account_number else None
        )
        
        for warning in validation_result.get('warnings', []):
            messages.warning(request, warning)
        
        if not validation_result['valid']:
            for error in validation_result.get('errors', []):
                messages.error(request, error)
            
            context = {
                'cart': cart,
                'cart_items': cart_items,
                'delivery_addresses': delivery_addresses,
                'default_address': default_address,
                'profile': profile,
                'loyalty_info': loyalty_info,
                'pricing': pricing,
            }
            return render(request, 'orders/checkout.html', context)
        
        # Get values from saved address
        customer_name = delivery_address_obj.full_name
        customer_phone = delivery_address_obj.phone
        delivery_instructions = delivery_address_obj.delivery_instructions
        delivery_charge = delivery_address_obj.get_delivery_charge()
        
        # Get special requests if provided
        special_requests = request.POST.get('special_requests', '').strip()
        
        # Validate cart items availability
        unavailable_items = [ci.menu_item.name for ci in cart_items if not ci.menu_item.is_available]
        if unavailable_items:
            messages.error(request, f'The following items are no longer available: {", ".join(unavailable_items)}')
            return redirect('orders:cart')
        
        if not customer_name.strip() or not customer_phone.strip():
            messages.error(request, 'Invalid delivery address information')
            return redirect('orders:checkout')
        
        subtotal = pricing['subtotal']
        total = pricing['grand_total']
        
        if subtotal <= 0:
            messages.error(request, 'Cart total must be greater than zero')
            return redirect('orders:cart')
        
        try:
            with transaction.atomic():
                cart_items_locked = list(cart.items.select_for_update().select_related('menu_item').all())
                
                for cart_item in cart_items_locked:
                    cart_item.menu_item.refresh_from_db()
                    if not cart_item.menu_item.is_available:
                        messages.error(request, f'{cart_item.menu_item.name} is no longer available')
                        return redirect('orders:cart')
                
                # Create order with delivery address reference
                order = Order.objects.create(
                    user=request.user,
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    delivery_address=delivery_address_obj,
                    delivery_instructions=delivery_instructions,
                    special_requests=special_requests,
                    payment_method=payment_method,
                    payment_notes=request.POST.get('payment_notes', '').strip(),
                    subtotal=pricing['subtotal'],
                    delivery_charge=pricing['delivery_charge'],
                    discount_amount=pricing['total_discount'],
                    loyalty_points_redeemed=pricing['loyalty_points_redeemed'],
                    loyalty_discount_amount=pricing['loyalty_discount_amount'],
                    vip_discount_amount=pricing['vip_discount_amount'],
                    corporate_discount_amount=pricing['corporate_discount_amount'],
                    referral_discount_amount=pricing['referral_discount_amount'],
                    total=pricing['grand_total'],
                    status='pending'
                )
                
                for cart_item in cart_items_locked:
                    OrderItem.objects.create(
                        order=order,
                        menu_item=cart_item.menu_item,
                        quantity=cart_item.quantity,
                        price=cart_item.menu_item.price,
                        subtotal=cart_item.get_subtotal()
                    )
                
                cart.items.all().delete()
                
                messages.success(request, f'Order {order.order_number} placed successfully!')
                return redirect('orders:order_detail', order_id=order.id)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error placing order for user {request.user.id}: {str(e)}', exc_info=True)
            messages.error(request, 'An error occurred while placing your order. Please try again or contact support.')
            return redirect('orders:checkout')
    
    pricing = OrderCalculationService.calculate_order_total(cart, request.user, 0)
    delivery_zones = DeliveryZone.objects.filter(is_active=True)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'profile': profile,
        'delivery_addresses': delivery_addresses,
        'default_address': default_address,
        'delivery_zones': delivery_zones,
        'loyalty_info': loyalty_info,
        'pricing': pricing,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.select_related('menu_item').all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).select_related('user').prefetch_related('items__menu_item').order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'orders': page_obj,
    }
    return render(request, 'orders/order_history.html', context)
