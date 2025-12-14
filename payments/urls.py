from django.urls import path
from . import views
from .webhooks import FlutterwaveWebhookView, mtn_momo_webhook, airtel_money_webhook

app_name = 'payments'

urlpatterns = [
    path('confirmation/<int:payment_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('history/', views.payment_history, name='payment_history'),
    path('<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('<int:payment_id>/receipt/', views.receipt_pdf, name='receipt'),
    path('<int:payment_id>/update/', views.update_payment_status, name='update_status'),
    path('<int:payment_id>/verify/', views.verify_payment, name='verify_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
    
    # Webhook endpoints
    path('webhooks/flutterwave/', FlutterwaveWebhookView.as_view(), name='flutterwave_webhook'),
    path('webhooks/mtn-momo/', mtn_momo_webhook, name='mtn_momo_webhook'),
    path('webhooks/airtel-money/', airtel_money_webhook, name='airtel_money_webhook'),
]



