from django.urls import path
from . import views
from .webhooks import FlutterwaveWebhookView, mtn_momo_webhook, airtel_money_webhook

app_name = 'payments'

urlpatterns = [
    # Payment history and details
    path('confirmation/<int:payment_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('history/', views.payment_history, name='payment_history'),
    path('<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('<int:payment_id>/receipt/', views.receipt_pdf, name='receipt'),
    path('<int:payment_id>/update/', views.update_payment_status, name='update_status'),
    path('<int:payment_id>/verify/', views.verify_payment, name='verify_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
    
    # Self-service payment processing
    path('checkout/', views.checkout, name='checkout'),
    path('<int:payment_id>/initiate/', views.initiate_payment, name='initiate_payment'),
    path('<int:payment_id>/process/cash-on-delivery/', views.process_cash_on_delivery, name='process_cash_on_delivery'),
    path('<int:payment_id>/process/mtn-money/', views.process_mtn_money, name='process_mtn_money'),
    path('<int:payment_id>/process/airtel-money/', views.process_airtel_money, name='process_airtel_money'),
    path('<int:payment_id>/process/bank-transfer/', views.process_bank_transfer, name='process_bank_transfer'),
    path('<int:payment_id>/process/card/', views.process_card_payment, name='process_card_payment'),
    path('<int:payment_id>/awaiting-confirmation/', views.payment_awaiting_confirmation, name='payment_awaiting_confirmation'),
    path('<int:payment_id>/retry/', views.retry_payment, name='retry_payment'),
    path('methods/', views.payment_methods_list, name='payment_methods_list'),
    
    # Webhook endpoints
    path('webhooks/flutterwave/', FlutterwaveWebhookView.as_view(), name='flutterwave_webhook'),
    path('webhooks/mtn-momo/', mtn_momo_webhook, name='mtn_momo_webhook'),
    path('webhooks/airtel-money/', airtel_money_webhook, name='airtel_money_webhook'),
]

















