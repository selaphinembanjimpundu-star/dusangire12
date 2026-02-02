from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_portal, name='portal'),  # Main unified portal
    path('dashboard/', views.patient_dashboard, name='dashboard'),  # Legacy redirect
]
