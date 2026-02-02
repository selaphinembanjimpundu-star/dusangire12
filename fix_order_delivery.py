#!/usr/bin/env python
"""Fix the order delivery address foreign key issue"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from delivery.models import DeliveryAddress
from orders.models import Order

# Check existing delivery addresses
addresses = DeliveryAddress.objects.all()
print("Existing Delivery Addresses:")
for addr in addresses:
    print(f"  ID: {addr.id}, Name: {addr.name}")

# Get the problematic order
try:
    order = Order.objects.get(id=1)
    print(f"\nProblematic Order ID: 1")
    print(f"Current delivery_address_id: {order.delivery_address_id}")
    
    # If there are existing addresses, use the first one
    if addresses.exists():
        first_address = addresses.first()
        order.delivery_address = first_address
        order.save()
        print(f"\n✓ Fixed! Order 1 now references delivery address: {first_address.id} ({first_address.name})")
    else:
        print("\n✗ No delivery addresses exist. Need to create one first.")
except Order.DoesNotExist:
    print("Order 1 does not exist")
