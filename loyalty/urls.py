from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('', views.loyalty_dashboard, name='dashboard'),
    path('history/', views.points_history, name='history'),
    path('redeem/<int:redemption_id>/', views.redeem_points, name='redeem'),
]

















