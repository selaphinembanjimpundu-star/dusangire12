"""
Hospital Wards URL Configuration
"""

from django.urls import path
from . import views

app_name = 'hospital_wards'

urlpatterns = [
    # Dashboard
    path('', views.hospital_dashboard, name='dashboard'),
    
    # Ward Management
    path('wards/', views.ward_list, name='ward_list'),
    path('wards/<int:ward_id>/', views.ward_detail, name='ward_detail'),
    path('beds/<int:bed_id>/', views.ward_bed_detail, name='bed_detail'),
    
    # Delivery Scheduling
    path('delivery-schedule/', views.delivery_schedule, name='delivery_schedule'),
    path('delivery-schedule/ward/<int:ward_id>/', views.delivery_schedule, name='delivery_schedule_ward'),
    path('delivery-slots/<int:slot_id>/book/', views.book_delivery_slot, name='book_delivery_slot'),
    
    # Patient Education
    path('education/', views.education_hub, name='education_hub'),
    path('education/<int:content_id>/', views.education_content_detail, name='education_detail'),
    path('education/<int:content_id>/complete/', views.mark_education_complete, name='mark_education_complete'),
    
    # Nutrition Information
    path('nutrition/', views.nutrition_info, name='nutrition_info'),
    path('nutrition/<int:nutrition_id>/', views.meal_detail, name='meal_detail'),
    
    # Caregiver Notifications
    path('notifications/', views.caregiver_notifications, name='notifications'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
]
