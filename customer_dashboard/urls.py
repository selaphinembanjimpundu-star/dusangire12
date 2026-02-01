# customer_dashboard/urls.py
from django.urls import path
from . import views

app_name = 'customer_dashboard'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Orders
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Subscriptions
    path('subscriptions/', views.my_subscriptions, name='my_subscriptions'),
    
    # Profile
    path('profile/', views.my_profile, name='my_profile'),
    
    # Meal Plans
    path('meal-plans/', views.my_meal_plans, name='my_meal_plans'),
    
    # Consultations
    path('consultations/', views.my_consultations, name='my_consultations'),
    
    # Additional views from updated views.py
    path('no-access/', views.no_access, name='no_access'),
    path('activity/', views.activity_log, name='activity_log'),
    path('preferences/', views.preferences, name='preferences'),
    path('help/', views.help_center, name='help_center'),
    path('notifications/', views.notifications_view, name='notifications'),
    
    # Order actions
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<int:order_id>/repeat/', views.repeat_order, name='repeat_order'),
    
    # Subscription actions
    path('subscriptions/<int:subscription_id>/pause/', views.pause_subscription, name='pause_subscription'),
    path('subscriptions/<int:subscription_id>/resume/', views.resume_subscription, name='resume_subscription'),
    path('subscriptions/<int:subscription_id>/cancel/', views.cancel_subscription, name='cancel_subscription'),
    
    # Profile actions
    path('profile/update-dietary/', views.update_dietary_preferences, name='update_dietary_preferences'),
    path('profile/update-address/', views.update_address, name='update_address'),
    path('profile/update-password/', views.update_password, name='update_password'),
    
    # Meal Plan actions
    path('meal-plans/<int:plan_id>/view/', views.view_meal_plan, name='view_meal_plan'),
    path('meal-plans/<int:plan_id>/feedback/', views.submit_meal_feedback, name='submit_meal_feedback'),
    
    # Consultation actions
    path('consultations/<int:consultation_id>/reschedule/', views.reschedule_consultation, name='reschedule_consultation'),
    path('consultations/<int:consultation_id>/cancel/', views.cancel_consultation, name='cancel_consultation'),
    path('consultations/book-new/', views.book_consultation, name='book_consultation'),
    
    # Payment and billing
    path('payments/', views.payment_history, name='payment_history'),
    path('payments/<int:payment_id>/receipt/', views.payment_receipt, name='payment_receipt'),
    path('billing/', views.billing_info, name='billing_info'),
    path('billing/update/', views.update_billing_info, name='update_billing_info'),
    path('loyalty/', views.loyalty_dashboard, name='loyalty'),
    
    # Support
    path('support/tickets/', views.support_tickets, name='support_tickets'),
    path('support/tickets/new/', views.new_support_ticket, name='new_support_ticket'),
    path('support/tickets/<int:ticket_id>/', views.view_support_ticket, name='view_support_ticket'),
    
    # Analytics and reports
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('reports/orders/', views.order_reports, name='order_reports'),
    path('reports/health/', views.health_reports, name='health_reports'),
    path('reports/health/update/', views.update_health_profile, name='update_health_profile'),
    
    # Quick actions
    path('quick-order/', views.quick_order, name='quick_order'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('favorites/<int:item_id>/add/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/<int:item_id>/remove/', views.remove_from_favorites, name='remove_from_favorites'),
    
    # Settings
    path('settings/', views.account_settings, name='account_settings'),
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
    path('settings/privacy/', views.privacy_settings, name='privacy_settings'),
    
    # Emergency/important
    path('emergency-contact/', views.emergency_contact, name='emergency_contact'),
    path('dietary-emergency/', views.dietary_emergency, name='dietary_emergency'),
    path('medical-alerts/', views.medical_alerts, name='medical_alerts'),
    
    # API endpoints for AJAX
    path('api/update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('api/mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/get-recent-activity/', views.get_recent_activity, name='get_recent_activity'),
    path('api/check-order-status/<int:order_id>/', views.check_order_status, name='check_order_status'),
]