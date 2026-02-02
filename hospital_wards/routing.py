"""
WebSocket URL routing for real-time hospital ward updates
"""

from django.urls import path
from . import consumers

# WebSocket URL patterns
websocket_urlpatterns = [
    # Ward real-time updates
    path('ws/ward/<int:ward_id>/', consumers.WardConsumer.as_asgi()),
    
    # Delivery/Address real-time updates
    path('ws/delivery/<int:delivery_id>/', consumers.DeliveryConsumer.as_asgi()),
    path('ws/address/<int:address_id>/', consumers.AddressConsumer.as_asgi()),
    
    # Dashboard real-time updates
    path('ws/dashboard/<str:role>/', consumers.DashboardConsumer.as_asgi()),
]
