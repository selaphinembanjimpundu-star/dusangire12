from django.urls import path
from . import views

app_name = 'nutritionist_dashboard'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('simple/', views.simple_dashboard, name='simple_dashboard'),
    
    # Profile management
    path('create-profile/', views.create_profile, name='create_profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('no-profile/', views.no_profile, name='no_profile'),
    
    # Client management
    path('clients/', views.manage_clients, name='manage_clients'),
    path('clients/<int:assignment_id>/', views.client_detail, name='client_detail'),
    
    # Consultation management
    path('consultations/', views.consultations, name='consultations'),
    path('consultations/schedule/', views.schedule_consultation, name='schedule_consultation'),
    path('consultations/schedule/<int:client_id>/', views.schedule_consultation, name='schedule_consultation_for_client'),
    
    # Meal plan management
    path('meal-plans/', views.meal_plans, name='meal_plans'),
    path('meal-plans/create/', views.create_meal_plan, name='create_meal_plan'),
    path('meal-plans/create/<int:client_id>/', views.create_meal_plan, name='create_meal_plan_for_client'),
    path('meal-plans/<int:plan_id>/', views.meal_plan_detail, name='meal_plan_detail'),
    
    # Diet recommendations
    path('recommendations/', views.diet_recommendations, name='diet_recommendations'),
    path('recommendations/create/', views.create_recommendation, name='create_recommendation'),
    path('recommendations/create/<int:client_id>/', views.create_recommendation, name='create_recommendation_for_client'),
    
    # Reports & Settings
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'),
    
    # API endpoints
    path('api/client/<int:client_id>/stats/', views.get_client_stats, name='get_client_stats'),
    
    # Booking (Customer facing)
    path('book/', views.book_consultation_list, name='book_consultation_list'),
    path('book/<int:nutritionist_id>/', views.book_consultation_detail, name='book_consultation_detail'),
]