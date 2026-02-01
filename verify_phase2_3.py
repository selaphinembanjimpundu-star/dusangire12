import os
import django
from decimal import Decimal
from datetime import date, timedelta



from django.contrib.auth.models import User
from subscriptions.models import (
    Subscription, SubscriptionPlan, VIPTier, LoyaltyPoints, 
    LoyaltyTransaction, ReferralProgram, SubscriptionAutoRenewal,
    SubscriptionStatus
)
from payments.models import Payment
from subscriptions.services import LoyaltyService, SubscriptionRenewalService

def test_vip_tier_calculation():
    print("\nTesting VIP Tier Calculation...")
    user, _ = User.objects.get_or_create(username='vip_test_user')
    
    # Clear existing data
    Payment.objects.filter(user=user).delete()
    VIPTier.objects.filter(user=user).delete()
    
    # Test Bronze (0 spending)
    tier = LoyaltyService.calculate_vip_tier(user)
    print(f"Initial Tier: {tier.tier_level} (Expected: bronze)")
    assert tier.tier_level == 'bronze'
    
    # Test Silver (500,000 spending)
    Payment.objects.create(
        user=user,
        amount=Decimal('500000'),
        status='completed',
        payment_method='mobile_money'
    )
    tier = LoyaltyService.calculate_vip_tier(user)
    print(f"Tier after 500k spending: {tier.tier_level} (Expected: silver)")
    assert tier.tier_level == 'silver'
    
    # Test Gold (2,000,000 spending)
    Payment.objects.create(
        user=user,
        amount=Decimal('1500000'), # Total 2M
        status='completed',
        payment_method='mobile_money'
    )
    tier = LoyaltyService.calculate_vip_tier(user)
    print(f"Tier after 2M spending: {tier.tier_level} (Expected: gold)")
    assert tier.tier_level == 'gold'

def test_loyalty_points():
    print("\nTesting Loyalty Points...")
    user, _ = User.objects.get_or_create(username='points_test_user')
    LoyaltyPoints.objects.filter(user=user).delete()
    LoyaltyTransaction.objects.filter(user=user).delete()
    
    # Ensure user has points record
    points, _ = LoyaltyPoints.objects.get_or_create(user=user)
    points.subscription_bonus_rate = Decimal('1.00') # Base rate
    points.save()
    
    # Award points for 10,000 RWF spending
    awarded = LoyaltyService.award_loyalty_points(user, 10000, "Test Purchase")
    print(f"Points awarded for 10k spending: {awarded} (Expected: 100)")
    assert awarded == 100
    
    points.refresh_from_db()
    print(f"User balance: {points.balance} (Expected: 100)")
    assert points.balance == 100
    
    # Test with bonus rate (Silver tier - 1.05)
    points.subscription_bonus_rate = Decimal('1.05')
    points.save()
    
    awarded = LoyaltyService.award_loyalty_points(user, 10000, "Test Purchase 2")
    print(f"Points awarded for 10k spending with 1.05 rate: {awarded} (Expected: 105)")
    assert awarded == 105

def test_referral_completion():
    print("\nTesting Referral Completion...")
    referrer, _ = User.objects.get_or_create(username='referrer_user')
    referee, _ = User.objects.get_or_create(username='referee_user')
    
    ReferralProgram.objects.filter(referrer=referrer).delete()
    LoyaltyPoints.objects.filter(user=referrer).delete()
    
    # Create referral
    referral = ReferralProgram.objects.create(
        referrer=referrer,
        referee=referee,
        status='PENDING',
        referral_code='TESTREF',
        referrer_bonus_points=100
    )
    
    # Process completion
    success = LoyaltyService.process_referral_completion(referee)
    print(f"Referral processing success: {success} (Expected: True)")
    assert success
    
    referral.refresh_from_db()
    print(f"Referral status: {referral.status} (Expected: COMPLETED)")
    assert referral.status == 'COMPLETED'
    
    points = LoyaltyPoints.objects.get(user=referrer)
    print(f"Referrer points: {points.balance} (Expected: 100)")
    assert points.balance == 100

def test_auto_renewal_process():
    print("\nTesting Auto-Renewal Process...")
    user, _ = User.objects.get_or_create(username='renewal_user')
    plan, _ = SubscriptionPlan.objects.get_or_create(
        name='Test Plan',
        defaults={'price': 1000, 'duration_days': 30, 'meals_per_cycle': 1}
    )
    
    # Create expiring subscription
    sub = Subscription.objects.create(
        user=user,
        plan=plan,
        start_date=date.today() - timedelta(days=30),
        end_date=date.today(), # Expires today
        status=SubscriptionStatus.ACTIVE,
        auto_renewal_enabled=True
    )
    
    # Auto-renewal config created by signal?
    renewal_config = SubscriptionAutoRenewal.objects.get(subscription=sub)
    renewal_config.payment_method_id = 'pm_test' # Mock payment method
    renewal_config.save()
    
    # Run process
    results = SubscriptionRenewalService.process_auto_renewals()
    print(f"Renewal results: {results}")
    
    sub.refresh_from_db()
    renewal_config.refresh_from_db()
    
    print(f"Subscription end date: {sub.end_date} (Expected: {date.today() + timedelta(days=30)})")
    assert sub.end_date == date.today() + timedelta(days=30)
    print(f"Renewal status: {renewal_config.last_renewal_status} (Expected: SUCCESS)")
    assert renewal_config.last_renewal_status == 'SUCCESS'

if __name__ == "__main__":
    try:
        test_vip_tier_calculation()
        test_loyalty_points()
        test_referral_completion()
        test_auto_renewal_process()
        print("\n✅ All Phase 2.3 tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
