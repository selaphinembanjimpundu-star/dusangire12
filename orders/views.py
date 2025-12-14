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
    """Checkout page with delivery address selection"""
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.select_related('menu_item').all()
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('orders:cart')
    
    # Get user delivery addresses
    delivery_addresses = DeliveryAddress.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    default_address = delivery_addresses.filter(is_default=True).first()
    
    # Get user profile for default values
    profile = request.user.profile if hasattr(request.user, 'profile') else None
    
    if request.method == 'POST':
        # Check if using saved address or new address
        use_saved_address = request.POST.get('use_saved_address') == 'true'
        saved_address_id = request.POST.get('saved_address_id')
        
        # Determine if using saved address (either explicitly set or if saved_address_id is provided)
        if use_saved_address or saved_address_id:
            # Use saved address
            if saved_address_id:
                try:
                    saved_address = DeliveryAddress.objects.get(id=saved_address_id, user=request.user)
                    customer_name = saved_address.full_name
                    customer_phone = saved_address.phone
                    delivery_address = saved_address.get_full_address()
                    delivery_instructions = saved_address.delivery_instructions
                    delivery_charge = saved_address.get_delivery_charge()
                except DeliveryAddress.DoesNotExist:
                    messages.error(request, 'Selected address not found')
                    return redirect('orders:checkout')
            else:
                # If use_saved_address is true but no address_id, try to use default
                default_address = delivery_addresses.filter(is_default=True).first()
                if default_address:
                    customer_name = default_address.full_name
                    customer_phone = default_address.phone
                    delivery_address = default_address.get_full_address()
                    delivery_instructions = default_address.delivery_instructions
                    delivery_charge = default_address.get_delivery_charge()
                else:
                    messages.error(request, 'Please select a delivery address or enter a new one')
                    return redirect('orders:checkout')
        else:
            # Use new address
            customer_name = request.POST.get('customer_name', request.user.get_full_name() or request.user.username)
            customer_phone = request.POST.get('customer_phone', profile.phone if profile else '')
            delivery_address = request.POST.get('delivery_address', '')
            delivery_instructions = request.POST.get('delivery_instructions', '')
            
            # Get delivery zone for charge calculation
            zone_id = request.POST.get('delivery_zone')
            if zone_id:
                try:
                    zone = DeliveryZone.objects.get(id=zone_id, is_active=True)
                    delivery_charge = zone.delivery_charge
                except DeliveryZone.DoesNotExist:
                    delivery_charge = Decimal('2000.00')  # Default in RWF
            else:
                delivery_charge = Decimal('2000.00')  # Default in RWF
            
            # Validate required fields
            if not delivery_address:
                messages.error(request, 'Delivery address is required')
                return redirect('orders:checkout')
        
        # Validate cart items are still available and in stock
        unavailable_items = []
        for cart_item in cart_items:
            # Refresh from database to get latest data
            cart_item.menu_item.refresh_from_db()
            
            if not cart_item.menu_item.is_available:
                unavailable_items.append(cart_item.menu_item.name)
        
        if unavailable_items:
            messages.error(
                request, 
                f'The following items are no longer available: {", ".join(unavailable_items)}. Please remove them from your cart.'
            )
            return redirect('orders:cart')
        
        # Re-verify cart still has items
        cart_items = cart.items.select_related('menu_item').all()
        if not cart_items.exists():
            messages.warning(request, 'Your cart is empty. Please add items before placing an order.')
            return redirect('orders:cart')
        
        # Validate required fields
        if not customer_name or not customer_name.strip():
            messages.error(request, 'Customer name is required')
            return redirect('orders:checkout')
        
        if not customer_phone or not customer_phone.strip():
            messages.error(request, 'Customer phone number is required')
            return redirect('orders:checkout')
        
        if not delivery_address or not delivery_address.strip():
            messages.error(request, 'Delivery address is required')
            return redirect('orders:checkout')
        
        # Calculate totals (recalculate to ensure accuracy)
        subtotal = cart.get_total()
        total = subtotal + delivery_charge
        
        # Validate totals are positive
        if subtotal <= 0:
            messages.error(request, 'Cart total must be greater than zero')
            return redirect('orders:cart')
        
        if total <= 0:
            messages.error(request, 'Order total must be greater than zero')
            return redirect('orders:checkout')
        
        # Create order
        try:
            with transaction.atomic():
                # Lock cart items to prevent concurrent modifications
                cart_items = list(cart.items.select_for_update().select_related('menu_item').all())
                
                # Double-check availability after lock
                for cart_item in cart_items:
                    cart_item.menu_item.refresh_from_db()
                    if not cart_item.menu_item.is_available:
                        messages.error(
                            request, 
                            f'{cart_item.menu_item.name} is no longer available. Please update your cart.'
                        )
                        return redirect('orders:cart')
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    status=OrderStatus.PENDING,
                    customer_name=customer_name.strip(),
                    customer_phone=customer_phone.strip(),
                    delivery_address=delivery_address.strip(),
                    delivery_instructions=delivery_instructions.strip() if delivery_instructions else '',
                    subtotal=subtotal,
                    delivery_charge=delivery_charge,
                    total=total
                )
                
                # Create order items with locked prices
                order_items_created = []
                for cart_item in cart_items:
                    order_item = OrderItem.objects.create(
                        order=order,
                        menu_item=cart_item.menu_item,
                        quantity=cart_item.quantity,
                        price=cart_item.menu_item.price,  # Lock price at order time
                        subtotal=cart_item.get_subtotal()
                    )
                    order_items_created.append(order_item)
                
                # Validate order items were created
                if not order_items_created:
                    raise ValueError("No order items were created")
                
                # Create payment record
                payment_method = request.POST.get('payment_method', PaymentMethod.CASH_ON_DELIVERY)
                
                # Set appropriate payment status
                if payment_method == PaymentMethod.CASH_ON_DELIVERY:
                    payment_status = PaymentStatus.PENDING
                elif payment_method in [PaymentMethod.MTN_MOBILE_MONEY, PaymentMethod.AIRTEL_MONEY, PaymentMethod.BANK_TRANSFER]:
                    # If transaction ID is provided, mark as processing, otherwise pending
                    transaction_id = request.POST.get('transaction_id', '').strip()
                    payment_status = PaymentStatus.PROCESSING if transaction_id else PaymentStatus.PENDING
                else:
                    payment_status = PaymentStatus.PENDING
                
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    status=payment_status,
                    amount=total,
                    phone_number=request.POST.get('phone_number', '').strip(),
                    account_number=request.POST.get('account_number', '').strip(),
                    transaction_id=request.POST.get('transaction_id', '').strip(),
                    notes=request.POST.get('payment_notes', '').strip()
                )
                
                # Clear cart only after successful order creation
                cart.items.all().delete()
                
                messages.success(request, f'Order {order.order_number} placed successfully!')
                return redirect('payments:payment_confirmation', payment_id=payment.id)
                
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('orders:checkout')
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error placing order for user {request.user.id}: {str(e)}', exc_info=True)
            messages.error(request, 'An error occurred while placing your order. Please try again or contact support.')
            return redirect('orders:checkout')
    
    # Calculate delivery charge for display
    if default_address:
        delivery_charge = default_address.get_delivery_charge()
    else:
        delivery_charge = Decimal('2000.00')  # Default delivery charge in RWF
    
    # Get active delivery zones
    delivery_zones = DeliveryZone.objects.filter(is_active=True)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': cart.get_total(),
        'delivery_charge': delivery_charge,
        'total': cart.get_total() + delivery_charge,
        'profile': profile,
        'delivery_addresses': delivery_addresses,
        'default_address': default_address,
        'delivery_zones': delivery_zones,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.select_related('menu_item').all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_history(request):
    """Order history page"""
    orders = Order.objects.filter(user=request.user).select_related('user', 'payment').prefetch_related('items__menu_item').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'orders': page_obj,  # For backward compatibility
    }
    return render(request, 'orders/order_history.html', context)
