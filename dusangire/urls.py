"""
URL configuration for dusangire project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from menu import views as menu_views

urlpatterns = [
    # Favicon handling - returns 204 No Content to prevent 404 errors
    path('favicon.ico', menu_views.favicon, name='favicon'),
    
    path('admin/', admin.site.urls),
    path('', menu_views.menu_list, name='home'),
    path('health/', menu_views.health_check, name='health_check'),
    
    # Allauth URLs for OAuth
    path('accounts/', include('allauth.urls')),
    
    # Apps - include without namespace parameter
    path('menu/', include('menu.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('delivery/', include('delivery.urls')),
    path('payments/', include('payments.urls')),
    path('dashboard/', include('admin_dashboard.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('loyalty/', include('loyalty.urls')),
    path('catering/', include('catering.urls')),
    path('notifications/', include('notifications.urls')),
    path('reviews/', include('reviews.urls')),
    path('support/', include('support.urls')),
    path('nutritionist/', include('nutritionist_dashboard.urls')),
    path('customer-dashboard/', include('customer_dashboard.urls')),
    path('analytics/', include('analytics.urls')),
    path('health-tracking/', include('health_tracking.urls')),
    path('health-checks/', include('health_profiles.urls')),
    path('hospital/', include('hospital_wards.urls')),
    path('patient/', include('patients.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)