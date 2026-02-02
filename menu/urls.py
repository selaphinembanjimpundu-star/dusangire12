from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('item/<int:item_id>/', views.menu_detail, name='menu_detail'),
    path('my-meal-plan/', views.patient_meal_plan_guide, name='patient_meal_plan_guide'),
    path('how-to-order/', views.meal_ordering_guide, name='meal_ordering_guide'),
    path('health/', views.health_check, name='health_check'),
]
