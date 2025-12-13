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
]

