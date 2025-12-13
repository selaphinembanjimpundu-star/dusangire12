from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta
from decimal import Decimal

from subscriptions.models import UserSubscription, SubscriptionStatus, SubscriptionOrder
from orders.models import Order, OrderItem, OrderStatus
from payments.models import Payment, PaymentMethod, PaymentStatus
from menu.models import MenuItem


class Command(BaseCommand):
    help = 'Generate orders for active subscriptions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating orders',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()
        
        # Get active subscriptions with auto-order enabled
        active_subscriptions = UserSubscription.objects.filter(
            status=SubscriptionStatus.ACTIVE,
            auto_order_enabled=True,
            start_date__lte=today,
            end_date__gte=today
        ).select_related('plan', 'user').prefetch_related('plan__menu_items')
        
        self.stdout.write(f'Found {active_subscriptions.count()} active subscriptions')
        
        orders_created = 0
        
        for subscription in active_subscriptions:
            # Determine if order should be created today based on plan type
            should_create = False
            
            if subscription.plan.plan_type == 'daily':
                # Check if order already exists for today
                existing_order = SubscriptionOrder.objects.filter(
                    subscription=subscription,
                    scheduled_date=today
                ).exists()
                should_create = not existing_order
                
            elif subscription.plan.plan_type == 'weekly':
                # Create order once per week (e.g., every Monday)
                days_since_start = (today - subscription.start_date).days
                if days_since_start % 7 == 0:
                    existing_order = SubscriptionOrder.objects.filter(
                        subscription=subscription,
                        scheduled_date=today
                    ).exists()
                    should_create = not existing_order
                    
            elif subscription.plan.plan_type == 'monthly':
                # Create order once per month
                days_since_start = (today - subscription.start_date).days
                if days_since_start % 30 == 0:
                    existing_order = SubscriptionOrder.objects.filter(
                        subscription=subscription,
                        scheduled_date=today
                    ).exists()
                    should_create = not existing_order
            
            if should_create:
                try:
                    if not dry_run:
                        with transaction.atomic():
                            # Get menu items for this subscription
                            if subscription.plan.menu_items.exists():
                                menu_items = subscription.plan.menu_items.filter(is_available=True)
                            else:
                                # Use all available items or random selection
                                menu_items = MenuItem.objects.filter(is_available=True)[:subscription.plan.meals_per_cycle]
                            
                            if not menu_items.exists():
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'No available menu items for subscription {subscription.id}'
                                    )
                                )
                                continue
                            
                            # Get user's default delivery address
                            from delivery.models import DeliveryAddress
                            delivery_address = DeliveryAddress.objects.filter(
                                user=subscription.user,
                                is_default=True
                            ).first()
                            
                            if not delivery_address:
                                delivery_addresses = DeliveryAddress.objects.filter(user=subscription.user)
                                if delivery_addresses.exists():
                                    delivery_address = delivery_addresses.first()
                                else:
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f'No delivery address for user {subscription.user.username}'
                                        )
                                    )
                                    continue
                            
                            # Calculate totals
                            subtotal = sum(item.price for item in menu_items)
                            delivery_charge = delivery_address.get_delivery_charge()
                            total = subtotal + delivery_charge
                            
                            # Create order
                            order = Order.objects.create(
                                user=subscription.user,
                                status=OrderStatus.PENDING,
                                customer_name=subscription.user.get_full_name() or subscription.user.username,
                                customer_phone=delivery_address.phone,
                                delivery_address=delivery_address.get_full_address(),
                                delivery_instructions=subscription.dietary_preferences or '',
                                subtotal=subtotal,
                                delivery_charge=delivery_charge,
                                total=total
                            )
                            
                            # Create order items
                            for menu_item in menu_items:
                                OrderItem.objects.create(
                                    order=order,
                                    menu_item=menu_item,
                                    quantity=1,
                                    price=menu_item.price,
                                    subtotal=menu_item.price
                                )
                            
                            # Create payment record
                            Payment.objects.create(
                                order=order,
                                payment_method=PaymentMethod.CASH_ON_DELIVERY,
                                status=PaymentStatus.PENDING,
                                amount=total
                            )
                            
                            # Create subscription order link
                            SubscriptionOrder.objects.create(
                                subscription=subscription,
                                order=order,
                                scheduled_date=today
                            )
                            
                            orders_created += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Created order {order.order_number} for subscription {subscription.id}'
                                )
                            )
                    else:
                        self.stdout.write(
                            f'[DRY RUN] Would create order for subscription {subscription.id}'
                        )
                        orders_created += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error creating order for subscription {subscription.id}: {str(e)}'
                        )
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'[DRY RUN] Would create {orders_created} orders'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {orders_created} subscription orders'
                )
            )

