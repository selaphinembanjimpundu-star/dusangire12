from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Main analytics dashboard
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    
    # Revenue analysis
    path('revenue-streams/', views.revenue_streams, name='revenue_streams'),
    
    # Customer analytics
    path('customers/', views.customer_analytics, name='customer_analytics'),
    
    # Campaigns
    path('campaigns/', views.campaigns, name='campaigns'),
    path('campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    
    # API endpoints for charts
    path('api/daily-revenue/', views.api_daily_revenue, name='api_daily_revenue'),
    path('api/customer-segments/', views.api_customer_segments, name='api_customer_segments'),
]
