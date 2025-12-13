from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('confirmation/<int:payment_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('history/', views.payment_history, name='payment_history'),
    path('<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('<int:payment_id>/receipt/', views.receipt_pdf, name='receipt'),
    path('<int:payment_id>/update/', views.update_payment_status, name='update_status'),
]

