from django.urls import path
from . import views

app_name = 'health_checks'

urlpatterns = [
    # Patient views
    path('', views.health_checks_list, name='health_checks_list'),
    path('request/', views.request_health_check, name='request_health_check'),
    path('<int:pk>/', views.health_check_detail, name='health_check_detail'),
    path('<int:pk>/cancel/', views.cancel_health_check, name='cancel_health_check'),
    
    # Consultant views
    path('<int:pk>/start/', views.start_consultation, name='start_consultation'),
    path('<int:pk>/complete/', views.complete_consultation, name='complete_consultation'),
    path('availability/update/', views.update_availability, name='update_availability'),
    
    # Manager/Admin views
    path('analytics/', views.health_check_analytics, name='health_check_analytics'),
    path('logs/', views.assignment_logs, name='assignment_logs'),
]
