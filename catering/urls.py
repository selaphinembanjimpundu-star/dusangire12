from django.urls import path
from . import views

app_name = 'catering'

urlpatterns = [
    path('', views.package_list, name='package_list'),
    path('book/', views.book_catering, name='book_catering'),
    path('book/<int:package_id>/', views.book_catering, name='book_catering_package'),
]
