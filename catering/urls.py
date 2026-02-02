from django.urls import path
from . import views
from . import kitchen_views

app_name = 'catering'

urlpatterns = [
    # Kitchen Staff Dashboards
    path('kitchen/dashboard/', kitchen_views.kitchen_dashboard, name='kitchen_dashboard'),
    path('kitchen/preparation/', kitchen_views.meal_preparation_list, name='meal_preparation_list'),
    
    # Catering Packages
    path('', views.package_list, name='package_list'),
    path('book/', views.book_catering, name='book_catering'),
    path('book/<int:package_id>/', views.book_catering, name='book_catering_package'),
]
