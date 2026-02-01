from django.urls import path
from . import views, api_views

app_name = 'subscriptions'

urlpatterns = [
    #path('', views.subscription_plans, name='plans'),
    path('', views.subscription_plans, name='subscription_plans'),
    path('plans/', views.subscription_plans, name='plans'),  # Keep this for existing code
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('my-subscriptions/', views.my_subscriptions, name='my_subscriptions'),
    path('<int:subscription_id>/', views.subscription_detail, name='subscription_detail'),
    path('<int:subscription_id>/pause/', views.pause_subscription, name='pause'),
    path('<int:subscription_id>/resume/', views.resume_subscription, name='resume'),
    path('<int:subscription_id>/cancel/', views.cancel_subscription, name='cancel'),
    path('<int:subscription_id>/update/', views.update_subscription, name='update'),
    
    # API Endpoints
    path('api/loyalty/status/', api_views.LoyaltyStatusView.as_view(), name='api_loyalty_status'),
    path('api/loyalty/history/', api_views.LoyaltyHistoryView.as_view(), name='api_loyalty_history'),
    path('api/loyalty/redeem/', api_views.RedeemPointsView.as_view(), name='api_loyalty_redeem'),
    path('api/referrals/info/', api_views.ReferralInfoView.as_view(), name='api_referral_info'),
    path('api/subscriptions/<int:subscription_id>/auto-renew/', api_views.AutoRenewalView.as_view(), name='api_auto_renew'),
]

















