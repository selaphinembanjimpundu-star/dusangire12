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
    path('admin/', admin.site.urls),
    path('', menu_views.menu_list, name='home'),
    path('menu/', include('menu.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('delivery/', include('delivery.urls')),
    path('payments/', include('payments.urls')),
    path('dashboard/', include('admin_dashboard.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('loyalty/', include('loyalty.urls')),
    path('notifications/', include('notifications.urls')),
    path('reviews/', include('reviews.urls')),
    path('support/', include('support.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
