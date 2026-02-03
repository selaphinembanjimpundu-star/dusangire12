#!/usr/bin/env python
"""
Test script to verify Django Channels setup is correct
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

# Check Channels configuration
from django.conf import settings
from django.apps import apps

print("\n📋 Django Channels Configuration Check:\n")

# 1. Check ASGI Application
print(f"1. ASGI_APPLICATION: {settings.ASGI_APPLICATION}")
if settings.ASGI_APPLICATION == 'dusangire.asgi.application':
    print("   ✅ ASGI app correctly configured")
else:
    print("   ❌ ASGI app not correctly configured")

# 2. Check Installed Apps
print(f"\n2. Daphne in INSTALLED_APPS: {'daphne' in settings.INSTALLED_APPS}")
print(f"   Channels in INSTALLED_APPS: {'channels' in settings.INSTALLED_APPS}")
if 'daphne' in settings.INSTALLED_APPS and 'channels' in settings.INSTALLED_APPS:
    print("   ✅ Both Daphne and Channels are installed")
else:
    print("   ❌ Missing Daphne or Channels in INSTALLED_APPS")

# 3. Check Channel Layers
print(f"\n3. CHANNEL_LAYERS configured: {bool(settings.CHANNEL_LAYERS)}")
if settings.CHANNEL_LAYERS:
    print(f"   Backend: {settings.CHANNEL_LAYERS['default']['BACKEND']}")
    print("   ✅ Channel layers configured")
else:
    print("   ❌ Channel layers not configured")

# 4. Check consumers exist
print("\n4. WebSocket Consumers:")
try:
    from hospital_wards.consumers import WardConsumer, DeliveryConsumer, AddressConsumer, DashboardConsumer
    print("   ✅ WardConsumer imported")
    print("   ✅ DeliveryConsumer imported")
    print("   ✅ AddressConsumer imported")
    print("   ✅ DashboardConsumer imported")
except ImportError as e:
    print(f"   ❌ Error importing consumers: {e}")

# 5. Check routing
print("\n5. WebSocket Routing:")
try:
    from hospital_wards.routing import websocket_urlpatterns
    print(f"   ✅ Routing imported successfully")
    print(f"   Number of WebSocket patterns: {len(websocket_urlpatterns)}")
    for pattern in websocket_urlpatterns:
        print(f"      - {pattern.pattern}")
except ImportError as e:
    print(f"   ❌ Error importing routing: {e}")

# 6. Check ASGI application
print("\n6. ASGI Application:")
try:
    from dusangire.asgi import application
    print("   ✅ ASGI application imported successfully")
    print(f"   Application type: {type(application)}")
except Exception as e:
    print(f"   ❌ Error importing ASGI application: {e}")

print("\n" + "="*60)
print("✅ Django Channels setup verification complete!")
print("="*60)
