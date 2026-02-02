from django.urls import path
from . import views
from . import support_views

app_name = 'support'

urlpatterns = [
    # Support Staff Dashboard
    path('staff-dashboard/', support_views.support_dashboard, name='staff_dashboard'),
    
    # Customer Support
    path('', views.ticket_list, name='ticket_list'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('staff/', views.staff_ticket_list, name='staff_ticket_list'),
    path('staff/<int:ticket_id>/', views.staff_ticket_detail, name='staff_ticket_detail'),
    path('feedback/', views.feedback, name='feedback'),
    path('faq/', views.faq_list, name='faq'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_form, name='contact_form'),
]



