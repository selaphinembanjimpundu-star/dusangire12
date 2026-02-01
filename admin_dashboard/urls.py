from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_management, name='order_management'),
    path('orders/<int:order_id>/', views.order_detail_admin, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('kitchen/', views.kitchen_dashboard, name='kitchen_dashboard'),
    path('reports/', views.reports, name='reports'),
    path('bi-dashboard/', views.bi_dashboard, name='bi_dashboard'),
    
    # Admin Logging URLs
    path('logs/', views.view_admin_logs, name='view_logs'),
    path('logs/<int:log_id>/', views.log_detail, name='log_detail'),
    path('activity-summary/', views.admin_activity_summary, name='activity_summary'),
    path('logs/export/', views.export_logs, name='export_logs'),
]

















