from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('staff/', views.staff_ticket_list, name='staff_ticket_list'),
    path('staff/<int:ticket_id>/', views.staff_ticket_detail, name='staff_ticket_detail'),
]

