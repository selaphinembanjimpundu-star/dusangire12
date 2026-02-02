#!/bin/bash
# PythonAnywhere Database Fix Script
# Fixes the foreign key integrity error for orders_order.delivery_address_id

echo "================================"
echo "PythonAnywhere Database Fix"
echo "================================"

# Navigate to project directory
cd ~/dusangire12

# Activate virtual environment
source ../../../virtualenvs/dusangire_env/bin/activate

echo ""
echo "1. Creating Python fix script..."

python << 'PYTHON_EOF'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
django.setup()

from delivery.models import DeliveryAddress
from orders.models import Order
import sqlite3

print("\n2. Checking existing delivery addresses...")
addresses = DeliveryAddress.objects.all()
for addr in addresses:
    print(f"   ✓ ID: {addr.id}, Name: {addr.name}")

print("\n3. Checking for problematic orders...")
# Check if the problematic order exists
try:
    problem_order = Order.objects.get(id=1)
    print(f"   Found problematic Order ID: 1")
    print(f"   Current delivery_address_id: {problem_order.delivery_address_id}")
    
    if addresses.exists():
        first_address = addresses.first()
        problem_order.delivery_address = first_address
        problem_order.save()
        print(f"   ✓ Fixed! Order 1 now references: {first_address.id} ({first_address.name})")
    else:
        print("   ✗ ERROR: No delivery addresses exist!")
        
except Order.DoesNotExist:
    print("   ✓ No problematic orders found (Order 1 doesn't exist)")

print("\n4. Running makemigrations...")
import subprocess
subprocess.run(['python', 'manage.py', 'makemigrations'], check=False)

print("\n5. Running migrate...")
subprocess.run(['python', 'manage.py', 'migrate', '--noinput'], check=False)

print("\n6. Running system check...")
subprocess.run(['python', 'manage.py', 'check'], check=False)

print("\n✓ Database fix complete!")
PYTHON_EOF

echo ""
echo "7. Restarting PythonAnywhere web app..."
# Uncomment if you want to reload the web app:
# You can do this manually from PythonAnywhere dashboard or:
# curl -X POST https://www.pythonanywhere.com/api/v0/user/YOUR_USERNAME/webapps/YOUR_DOMAIN/reload/ -H "Authorization: Token YOUR_API_TOKEN"

echo ""
echo "================================"
echo "Done! Database should now be fixed."
echo "================================"
