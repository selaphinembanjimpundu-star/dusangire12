"""
Professional subscription services for meal selection, analytics, and management
"""

import random
from decimal import Decimal
from django.db.models import Q, Avg, Count, F, Sum
from django.utils import timezone
from datetime import timedelta, date
from menu.models import MenuItem, Category
from reviews.models import Review
from orders.models import Order, OrderItem
from .models import (
    VIPTier, LoyaltyPoints, LoyaltyTransaction, ReferralProgram, 
    SubscriptionAutoRenewal, Subscription, SubscriptionStatus
)
from payments.models import Payment


class MealSelectionService:
    """Smart meal selection service for subscriptions"""
    
    @staticmethod
    def select_meals_for_subscription(subscription, count=None):
        """
        Intelligently select meals for a subscription based on:
        - User's order history
        - Ratings and reviews
        - Dietary preferences
        - Meal variety
        - Plan menu items (if specified)
        """
        if count is None:
            count = subscription.plan.meals_per_cycle
        
        # Start with plan's menu items if specified
        if subscription.plan.menu_items.exists():
            available_items = subscription.plan.menu_items.filter(is_available=True)
        else:
            available_items = MenuItem.objects.filter(is_available=True)
        
        # Filter by dietary preferences if specified
        if subscription.dietary_preferences:
            dietary_keywords = subscription.dietary_preferences.lower().split()
            # Filter by dietary tags or ingredients
            dietary_query = Q()
            for keyword in dietary_keywords:
                dietary_query |= Q(dietary_tags__name__icontains=keyword) | \
                                 Q(ingredients__icontains=keyword)
            if dietary_query:
                available_items = available_items.filter(dietary_query).distinct()
        
        if not available_items.exists():
            return MenuItem.objects.filter(is_available=True)[:count]
        
        # Get user's order history for preferences
        user_orders = Order.objects.filter(
            user=subscription.user,
            status__in=['delivered', 'ready']
        ).prefetch_related('items__menu_item')
        
        # Get user's reviewed items (they liked these)
        reviewed_items = Review.objects.filter(
            user=subscription.user,
            rating__gte=4,
            is_approved=True
        ).values_list('menu_item_id', flat=True)
        
        # Get user's frequently ordered items
        frequently_ordered = OrderItem.objects.filter(
            order__user=subscription.user,
            order__status__in=['delivered', 'ready']
        ).values('menu_item').annotate(
            order_count=Count('id')
        ).order_by('-order_count')[:10].values_list('menu_item', flat=True)
        
        # Score items based on multiple factors
        scored_items = []
        for item in available_items:
            score = 0.0
            
            # Base score from ratings
            avg_rating = item.average_rating or 0
            score += float(avg_rating) * 2  # Weight ratings highly
            
            # Boost if user reviewed it positively
            if item.id in reviewed_items:
                score += 5.0
            
            # Boost if user orders it frequently
            if item.id in frequently_ordered:
                score += 3.0
            
            # Boost if featured
            if item.is_featured:
                score += 2.0
            
            # Boost if has many reviews (popular)
            review_count = item.total_reviews or 0
            score += min(review_count * 0.1, 2.0)  # Cap at 2.0
            
            scored_items.append((item, score))
        
        # Sort by score
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Select top items with variety
        selected = []
        selected_categories = set()
        
        for item, score in scored_items:
            if len(selected) >= count:
                break
            
            # Ensure variety - don't select too many from same category
            category_id = item.category_id
            category_count = sum(1 for cat in selected_categories if cat == category_id)
            
            if category_count < count // 2 or len(selected_categories) < 2:
                selected.append(item)
                selected_categories.add(category_id)
        
        # If we don't have enough, fill with random from top scored
        if len(selected) < count:
            remaining = [item for item, _ in scored_items if item not in selected]
            needed = count - len(selected)
            selected.extend(remaining[:needed])
        
        return selected[:count]
    
    @staticmethod
    def get_recommended_meals(user, count=5):
        """Get recommended meals for a user based on their preferences"""
        # Get user's order history
        user_orders = Order.objects.filter(
            user=user,
            status__in=['delivered', 'ready']
        ).prefetch_related('items__menu_item')
        
        # Get categories from user's orders
        ordered_categories = Category.objects.filter(
            menu_items__orderitem__order__user=user,
            menu_items__orderitem__order__status__in=['delivered', 'ready']
        ).distinct()
        
        # Get highly rated items from those categories
        recommended = MenuItem.objects.filter(
            category__in=ordered_categories,
            is_available=True
        ).filter(
            average_rating__gte=4.0
        ).order_by('-average_rating', '-total_reviews')[:count]
        
        return recommended


class SubscriptionAnalytics:
    """Analytics and statistics for subscriptions"""
    
    @staticmethod
    def get_subscription_stats(subscription):
        """Get statistics for a subscription"""
        from .models import SubscriptionOrder
        
        # Get subscription orders
        subscription_orders = SubscriptionOrder.objects.filter(
            subscription=subscription
        ).select_related('order')
        
        # Calculate stats
        total_orders = subscription_orders.count()
        completed_orders = subscription_orders.filter(
            order__status='delivered'
        ).count()
        
        total_spent = sum(
            so.order.total for so in subscription_orders
            if so.order.status == 'delivered'
        )
        
        # Average order value
        avg_order_value = total_spent / completed_orders if completed_orders > 0 else Decimal('0.00')
        
        # Meals delivered
        meals_delivered = sum(
            so.order.items.count() for so in subscription_orders
            if so.order.status == 'delivered'
        )
        
        return {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_spent': total_spent,
            'avg_order_value': avg_order_value,
            'meals_delivered': meals_delivered,
            'days_active': subscription.days_remaining() + (timezone.now().date() - subscription.start_date).days,
        }
    
    @staticmethod
    def get_plan_popularity_stats():
        """Get popularity statistics for all plans"""
        from .models import SubscriptionPlan, Subscription, SubscriptionStatus
        
        plans = SubscriptionPlan.objects.filter(is_active=True).annotate(
            active_subscribers=Count(
                'user_subscriptions',
                filter=Q(user_subscriptions__status=SubscriptionStatus.ACTIVE)
            ),
            total_subscribers=Count('user_subscriptions'),
            total_revenue=Count('user_subscriptions')  # Simplified - would need order data
        )
        
        return plans


class SubscriptionRenewalService:
    """Handle subscription renewals and auto-renewal"""
    
    @staticmethod
    def check_and_renew_subscriptions():
        """Check for subscriptions that need renewal"""
        from .models import Subscription, SubscriptionStatus
        from datetime import date
        
        today = date.today()
        
        # Find subscriptions ending soon (within 3 days)
        expiring_soon = Subscription.objects.filter(
            status=SubscriptionStatus.ACTIVE,
            end_date__lte=today + timedelta(days=3),
            end_date__gte=today
        )
        
        renewed = 0
        expired = 0
        
        for subscription in expiring_soon:
            # Check if auto-renewal is enabled (would need to add this field)
            # For now, we'll just mark as expired
            if subscription.end_date < today:
                subscription.status = SubscriptionStatus.EXPIRED
                subscription.save()
                expired += 1
            # Auto-renewal logic would go here
        
        return {
            'expiring_soon': expiring_soon.count(),
            'renewed': renewed,
            'expired': expired
        }
    
    @staticmethod
    def renew_subscription(subscription):
        """Renew a subscription for another period"""
        if subscription.status != SubscriptionStatus.ACTIVE:
            raise ValueError("Can only renew active subscriptions")
        
        # Extend end date by plan duration
        new_end_date = subscription.end_date + timedelta(days=subscription.plan.duration_days)
        subscription.end_date = new_end_date
        subscription.next_billing_date = new_end_date
        subscription.save()
        
        return subscription

    @staticmethod
    def process_auto_renewals():
        """
        Process auto-renewals for subscriptions due today.
        This should be called by a daily cron job/management command.
        """
        today = date.today()
        
        # Find active auto-renewals due today or in the past (retries)
        renewals_due = SubscriptionAutoRenewal.objects.filter(
            auto_renew_enabled=True,
            renewal_date__lte=today,
            subscription__status=SubscriptionStatus.ACTIVE
        ).select_related('subscription', 'subscription__user')
        
        results = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'retried': 0
        }
        
        for renewal in renewals_due:
            results['processed'] += 1
            
            # Check if max retries exceeded
            if renewal.failure_count >= renewal.max_retries:
                # Disable auto-renewal and notify user
                renewal.auto_renew_enabled = False
                renewal.last_renewal_status = 'FAILED'
                renewal.save()
                
                # Notify user (implementation depends on notification system)
                # NotificationService.send_renewal_failed(renewal.subscription.user)
                results['failed'] += 1
                continue
            
            try:
                # Attempt payment logic here
                # For now, we simulate success if payment method exists
                if renewal.payment_method_id:
                    # Simulate payment processing
                    # payment_result = PaymentGateway.charge(...)
                    payment_success = True # Placeholder
                    
                    if payment_success:
                        # Extend subscription
                        SubscriptionRenewalService.renew_subscription(renewal.subscription)
                        
                        # Update renewal record
                        renewal.last_renewal_at = timezone.now()
                        renewal.last_renewal_status = 'SUCCESS'
                        renewal.renewal_date = today + timedelta(days=renewal.renewal_interval_days)
                        renewal.failure_count = 0
                        renewal.save()
                        
                        results['success'] += 1
                    else:
                        raise Exception("Payment failed")
                else:
                    raise Exception("No payment method")
                    
            except Exception as e:
                # Handle failure
                renewal.failure_count += 1
                renewal.last_renewal_status = 'FAILED'
                # Schedule retry for tomorrow
                renewal.next_retry_at = timezone.now() + timedelta(days=1)
                renewal.save()
                results['retried'] += 1
                
        return results


class LoyaltyService:
    """Service for handling loyalty points, VIP tiers, and referrals"""
    
    TIER_THRESHOLDS = {
        'bronze': 0,
        'silver': 500000,
        'gold': 2000000,
        'platinum': 5000000
    }
    
    TIER_BENEFITS = {
        'bronze': {'bonus_rate': Decimal('1.02'), 'discount': 0},
        'silver': {'bonus_rate': Decimal('1.05'), 'discount': 5},
        'gold': {'bonus_rate': Decimal('1.10'), 'discount': 10},
        'platinum': {'bonus_rate': Decimal('1.15'), 'discount': 15}
    }

    @staticmethod
    def calculate_vip_tier(user):
        """
        Calculate and update user's VIP tier based on lifetime spending.
        """
        # Get or create VIP tier record
        vip_tier, created = VIPTier.objects.get_or_create(user=user)
        
        # Calculate total spending from completed payments
        total_spending = Payment.objects.filter(
            user=user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        vip_tier.spending_total = total_spending
        
        # Determine new tier
        new_tier = 'bronze'
        for tier, threshold in sorted(LoyaltyService.TIER_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
            if total_spending >= threshold:
                new_tier = tier
                break
        
        # Update if tier changed
        if vip_tier.tier_level != new_tier:
            vip_tier.tier_level = new_tier
            vip_tier.achieved_at = date.today()
            
            # Update benefits
            benefits = LoyaltyService.TIER_BENEFITS.get(new_tier, {})
            vip_tier.promotion_percentage = benefits.get('bonus_rate', Decimal('1.00')) * 100 - 100
            vip_tier.benefits_list = benefits
            
            # Update loyalty points bonus rate
            loyalty_points, _ = LoyaltyPoints.objects.get_or_create(user=user)
            loyalty_points.subscription_bonus_rate = benefits.get('bonus_rate', Decimal('1.00'))
            loyalty_points.save()
            
        vip_tier.save()
        return vip_tier

    @staticmethod
    def award_loyalty_points(user, amount, reason, related_object=None):
        """
        Award loyalty points to a user.
        amount: Amount spent in RWF (to calculate points) OR direct points amount if reason implies bonus
        """
        loyalty_points, _ = LoyaltyPoints.objects.get_or_create(user=user)
        
        # Calculate points: 1 point per 100 RWF * bonus rate
        points_to_award = int((amount / 100) * loyalty_points.subscription_bonus_rate)
        
        if points_to_award > 0:
            loyalty_points.add_points(points_to_award, reason)
            
            # Create transaction record
            transaction = LoyaltyTransaction.objects.create(
                user=user,
                transaction_type='EARN',
                points_amount=points_to_award,
                description=reason,
                balance_before=loyalty_points.balance - points_to_award,
                balance_after=loyalty_points.balance
            )
            
            if isinstance(related_object, Order):
                # Link to order if possible (need to add field to model first or use generic relation)
                pass 
            elif isinstance(related_object, Payment):
                transaction.related_payment = related_object
                transaction.save()
                
            return points_to_award
        return 0

    @staticmethod
    def process_referral_completion(referee_user):
        """
        Process referral rewards when a referee completes their first purchase.
        """
        try:
            referral = ReferralProgram.objects.get(referee=referee_user, status='PENDING')
            
            # Award referrer
            referrer_bonus_points = referral.referrer_bonus_points
            LoyaltyService.award_loyalty_points(
                referral.referrer, 
                referrer_bonus_points * 100, # Hack to pass points directly if logic assumes spending
                "Referral Bonus"
            )
            # Note: Direct point award logic in award_loyalty_points assumes spending. 
            # We might need a direct award method or adjust logic.
            # Let's adjust award_loyalty_points to handle direct points in a future iteration or separate method.
            # For now, let's manually add points for clarity.
            
            referrer_points, _ = LoyaltyPoints.objects.get_or_create(user=referral.referrer)
            referrer_points.add_points(referrer_bonus_points, f"Referral Bonus for {referee_user.username}")
            
            LoyaltyTransaction.objects.create(
                user=referral.referrer,
                transaction_type='BONUS',
                points_amount=referrer_bonus_points,
                description=f"Referral Bonus for {referee_user.username}",
                balance_before=referrer_points.balance - referrer_bonus_points,
                balance_after=referrer_points.balance
            )

            # Mark referral as completed
            referral.status = 'COMPLETED'
            referral.completed_at = timezone.now()
            referral.save()
            
            return True
        except ReferralProgram.DoesNotExist:
            return False













