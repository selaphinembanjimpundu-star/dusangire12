#!/usr/bin/env python
"""
Fix PythonAnywhere database foreign key constraint issue.
This script removes orders with invalid delivery addresses.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from orders.models import Order, DeliveryAddress

print("=" * 60)
print("PythonAnywhere Database Fix - Remove Invalid Orders")
print("=" * 60)

# Get all valid delivery address IDs
valid_addresses = set(DeliveryAddress.objects.values_list('id', flat=True))
print(f"\nValid delivery address IDs: {valid_addresses}")

# Find orders with invalid delivery addresses
invalid_orders = Order.objects.exclude(delivery_address_id__in=valid_addresses)

if invalid_orders.exists():
    print(f"\nFound {invalid_orders.count()} orders with invalid delivery addresses:")
    for order in invalid_orders:
        print(f"  - Order ID {order.id}: delivery_address_id = '{order.delivery_address_id}'")
    
    # Delete them
    count = invalid_orders.count()
    invalid_orders.delete()
    print(f"\n✓ Deleted {count} invalid orders")
else:
    print("\n✓ No invalid orders found - database is clean!")

print("\n" + "=" * 60)
