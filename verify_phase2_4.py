import os
import django
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import Subscription, SubscriptionPlan, VIPTier, LoyaltyPoints, SubscriptionAutoRenewal
from subscriptions.api_views import LoyaltyStatusView, RedeemPointsView, AutoRenewalView
from datetime import date, timedelta

def verify_api():
    print("\nTesting Phase 2.4 APIs...")
    factory = APIRequestFactory()
    user, _ = User.objects.get_or_create(username='api_test_user')
    
    # Setup data
    LoyaltyPoints.objects.filter(user=user).delete()
    points = LoyaltyPoints.objects.create(user=user, balance=500)
    
    # 1. Test Loyalty Status
    print("\n1. Testing GET /api/loyalty/status/")
    view = LoyaltyStatusView.as_view()
    request = factory.get('/subscriptions/api/loyalty/status/')
    force_authenticate(request, user=user)
    response = view(request)
    print(f"Status Code: {response.status_code}")
    print(f"Data: {response.data}")
    assert response.status_code == 200
    assert response.data['points']['balance'] == 500
    
    # 2. Test Redeem Points
    print("\n2. Testing POST /api/loyalty/redeem/")
    view = RedeemPointsView.as_view()
    request = factory.post('/subscriptions/api/loyalty/redeem/', {'points': 100}, format='json')
    force_authenticate(request, user=user)
    response = view(request)
    print(f"Status Code: {response.status_code}")
    print(f"Data: {response.data}")
    assert response.status_code == 200
    assert response.data['success'] == True
    
    points.refresh_from_db()
    assert points.balance == 400
    
    # 3. Test Auto-Renewal
    print("\n3. Testing Auto-Renewal API")
    plan, _ = SubscriptionPlan.objects.get_or_create(name='API Plan', defaults={'price': 100, 'duration_days': 30})
    sub = Subscription.objects.create(
        user=user, plan=plan, start_date=date.today(), end_date=date.today()+timedelta(days=30)
    )
    # Ensure auto-renewal exists (signal should have created it)
    auto_renewal = SubscriptionAutoRenewal.objects.get(subscription=sub)
    
    view = AutoRenewalView.as_view()
    
    # Toggle ON
    print("Enabling auto-renewal...")
    request = factory.post(f'/subscriptions/api/subscriptions/{sub.id}/auto-renew/', {'enabled': True}, format='json')
    force_authenticate(request, user=user)
    response = view(request, subscription_id=sub.id)
    print(f"Status Code: {response.status_code}")
    print(f"Data: {response.data}")
    assert response.status_code == 200
    assert response.data['auto_renew_enabled'] == True
    
    sub.refresh_from_db()
    assert sub.auto_renewal_enabled == True

if __name__ == "__main__":
    try:
        verify_api()
        print("\n✅ All Phase 2.4 API tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
