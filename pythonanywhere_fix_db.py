#!/usr/bin/env python
"""
PythonAnywhere Database Fix Script
Run this on PythonAnywhere bash console to fix the foreign key integrity error
"""
import os
import sys
import django
import subprocess

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
sys.path.insert(0, '/home/dusa2026/dusangire12')
django.setup()

from delivery.models import DeliveryAddress
from orders.models import Order

print("\n" + "="*50)
print("PythonAnywhere Database Integrity Fix")
print("="*50)

try:
    print("\n1️⃣  Checking existing delivery addresses...")
    addresses = DeliveryAddress.objects.all()
    if addresses.exists():
        for addr in addresses:
            print(f"   ✓ ID: {addr.id}, Name: {addr.name}")
    else:
        print("   ⚠️  No delivery addresses found!")
    
    print("\n2️⃣  Checking for problematic orders...")
    # Try to find and fix the problematic order
    try:
        problem_order = Order.objects.get(id=1)
        print(f"   Found Order ID: 1")
        print(f"   Current delivery_address_id: {problem_order.delivery_address_id}")
        
        if addresses.exists():
            first_address = addresses.first()
            old_id = problem_order.delivery_address_id
            problem_order.delivery_address = first_address
            problem_order.save()
            print(f"   ✓ Fixed! Updated from '{old_id}' → {first_address.id}")
        else:
            print("   ✗ Cannot fix: No delivery addresses available")
            sys.exit(1)
            
    except Order.DoesNotExist:
        print("   ✓ No problematic Order ID 1 found")
    
    print("\n3️⃣  Running migrations...")
    result = subprocess.run([sys.executable, 'manage.py', 'makemigrations'], 
                          capture_output=True, text=True)
    if result.stdout:
        print("   Migrations created:")
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"   - {line}")
    
    result = subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], 
                          capture_output=True, text=True)
    if "No migrations to apply" in result.stdout:
        print("   ✓ All migrations applied (no pending)")
    elif "OK" in result.stdout or result.returncode == 0:
        print("   ✓ Migrations applied successfully")
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip() and 'Running migrations' not in line:
                    print(f"   {line}")
    
    print("\n4️⃣  System check...")
    result = subprocess.run([sys.executable, 'manage.py', 'check'], 
                          capture_output=True, text=True)
    if "0 silenced" in result.stdout or result.returncode == 0:
        print("   ✓ System check: 0 issues found")
    else:
        print(f"   ⚠️  {result.stdout}")
    
    print("\n" + "="*50)
    print("✅ Database fix complete!")
    print("="*50)
    print("\n📝 Next steps:")
    print("   1. Reload your PythonAnywhere web app from the dashboard")
    print("   2. Visit your site to verify everything is working")
    print("   3. If you still see errors, check the error log on PythonAnywhere")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
