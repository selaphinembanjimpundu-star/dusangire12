from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('item/<int:item_id>/', views.item_reviews, name='item_reviews'),
    path('item/<int:item_id>/add/', views.add_review, name='add_review'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('<int:review_id>/helpful/', views.mark_helpful, name='mark_helpful'),
]

