from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.subscription_plans, name='plans'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('my-subscriptions/', views.my_subscriptions, name='my_subscriptions'),
    path('<int:subscription_id>/', views.subscription_detail, name='subscription_detail'),
    path('<int:subscription_id>/pause/', views.pause_subscription, name='pause'),
    path('<int:subscription_id>/resume/', views.resume_subscription, name='resume'),
    path('<int:subscription_id>/cancel/', views.cancel_subscription, name='cancel'),
    path('<int:subscription_id>/update/', views.update_subscription, name='update'),
]



