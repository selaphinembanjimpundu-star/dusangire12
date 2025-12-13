from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_create, name='address_create'),
    path('addresses/<int:address_id>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:address_id>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<int:address_id>/set-default/', views.address_set_default, name='address_set_default'),
]

