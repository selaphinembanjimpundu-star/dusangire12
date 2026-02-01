from django.urls import path
from . import views

app_name = 'health_tracking'

urlpatterns = [
    # Dashboard views
    path('dashboard/patient/', views.health_dashboard_patient, name='dashboard_patient'),
    path('dashboard/nutritionist/', views.health_dashboard_nutritionist, name='dashboard_nutritionist'),
    
    # Metric management
    path('metrics/add/', views.health_metrics_add, name='metrics_add'),
    path('metrics/trend/<int:metric_id>/', views.metric_trend_chart, name='metric_trend'),
    
    # Goal management
    path('goals/', views.health_goals_manage, name='goals_manage'),
    
    # Meal reviews
    path('meal-review/create/', views.meal_review_create, name='meal_review_create'),
    
    # Health reports
    path('reports/', views.health_reports_view, name='reports_view'),
    
    # Alerts
    path('alerts/<int:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
]
