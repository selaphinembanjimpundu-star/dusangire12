"""
Hospital Wards URL Configuration
"""

from django.urls import path
from . import views

app_name = 'hospital_wards'

urlpatterns = [
    # Main Dashboard - Entry Point
    path('', views.hospital_dashboard, name='dashboard'),
    
    # Role-Based Dashboards
    path('dashboards/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboards/caregiver/', views.caregiver_dashboard, name='caregiver_dashboard'),
    path('dashboards/nutritionist/', views.nutritionist_dashboard, name='nutritionist_dashboard'),
    path('dashboards/medical-staff/', views.medical_staff_dashboard, name='medical_staff_dashboard'),
    path('dashboards/chef/', views.chef_dashboard, name='chef_dashboard'),
    path('dashboards/kitchen-staff/', views.kitchen_staff_dashboard, name='kitchen_staff_dashboard'),
    path('dashboards/delivery-person/', views.delivery_person_dashboard, name='delivery_person_dashboard'),
    path('dashboards/support-staff/', views.support_staff_dashboard, name='support_staff_dashboard'),
    path('dashboards/hospital-manager/', views.hospital_manager_dashboard, name='hospital_manager_dashboard'),
    path('dashboards/admin/', views.admin_dashboard, name='admin_dashboard'),
    
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
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    
    # AJAX Endpoints - Dashboard Actions
    path('api/meals/<int:meal_id>/complete/', views.mark_meal_complete, name='mark_meal_complete'),
    path('api/orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('api/routes/<int:route_id>/start/', views.start_delivery_route, name='start_delivery_route'),
    path('api/orders/<int:order_id>/mark-delivered/', views.mark_order_delivered, name='mark_order_delivered'),
    path('api/beds/<int:bed_id>/discharge/', views.discharge_bed, name='discharge_bed'),
    path('api/users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    
    # Patient Admission & Discharge Workflow
    path('patients/admit/', views.patient_admission, name='patient_admission'),
    path('patients/<int:admission_id>/discharge/', views.patient_discharge, name='patient_discharge'),
    path('patients/transfer-bed/', views.transfer_patient_bed, name='transfer_patient_bed'),
    path('api/patient/<int:patient_id>/current-bed/', views.get_patient_current_bed, name='get_patient_current_bed'),
    path('reports/occupancy/', views.occupancy_report, name='occupancy_report'),
    
    # Bulk Operations
    path('bulk/operations/', views.bulk_operations_list, name='bulk_operations_list'),
    path('bulk/import-patients/', views.bulk_import_patients, name='bulk_import_patients'),
    path('bulk/assign-patients/', views.bulk_assign_patients, name='bulk_assign_patients'),
    path('bulk/discharge/', views.bulk_discharge, name='bulk_discharge'),
    path('bulk/export-report/', views.export_report, name='export_report'),
    path('bulk/export/patients/', views.export_patients_csv, name='export_patients_csv'),
    
    # Patient Notifications
    path('patient-notifications/', views.patient_notifications, name='patient_notifications'),
    path('patient-notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_patient_notification_read'),
    path('api/notifications/unread-count/', views.notification_count, name='notification_count'),
    
    # Notification Management
    path('notifications/', views.notifications_dashboard, name='notifications_dashboard'),
    path('notifications/preferences/', views.notification_preferences, name='notification_preferences'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
    path('api/notifications/stats/', views.notification_stats, name='notification_stats'),
]
