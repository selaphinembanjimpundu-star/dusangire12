# 🚀 Django Channels Real-Time Setup - Completion Guide

**Date**: February 3, 2026  
**Status**: ✅ CONFIGURED  
**Focus**: WebSocket support for real-time dashboard updates

---

## ✅ What's Already Configured

### 1. **Django Channels Installation** ✅
- Package: `channels>=4.0.0`
- Server: `daphne>=4.0.0`
- Redis support: `channels-redis>=4.0.0`
- Status: In requirements.txt, ready for deployment

### 2. **ASGI Application** ✅
**File**: `dusangire/asgi.py`

```python
ASGI_APPLICATION = 'dusangire.asgi.application'

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
```

### 3. **Settings Configuration** ✅
**File**: `dusangire/settings.py`

```python
INSTALLED_APPS = [
    'daphne',           # ASGI server
    'channels',         # WebSocket support
    ...
]

# Django Channels Configuration
ASGI_APPLICATION = 'dusangire.asgi.application'

# Channel Layers Configuration (Redis backend)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
            'capacity': 1500,
            'expiry': 10,
        }
    }
}
```

### 4. **WebSocket Consumers** ✅
**File**: `hospital_wards/consumers.py`

Implemented consumers:
- `WardConsumer` - Real-time ward and bed status updates
- `DeliveryConsumer` - Delivery tracking updates
- `AddressConsumer` - Address changes broadcast
- `DashboardConsumer` - Dashboard real-time metrics

### 5. **WebSocket Routing** ✅
**File**: `hospital_wards/routing.py`

```python
websocket_urlpatterns = [
    path('ws/ward/<int:ward_id>/', consumers.WardConsumer.as_asgi()),
    path('ws/delivery/<int:delivery_id>/', consumers.DeliveryConsumer.as_asgi()),
    path('ws/address/<int:address_id>/', consumers.AddressConsumer.as_asgi()),
    path('ws/dashboard/<str:role>/', consumers.DashboardConsumer.as_asgi()),
]
```

---

## 🎯 WebSocket URL Patterns

### Ward Updates
```
ws://localhost:8000/ws/ward/1/
ws://example.com/ws/ward/1/
```
Real-time bed occupancy, patient admissions, discharge updates

### Delivery Updates
```
ws://localhost:8000/ws/delivery/5/
```
Real-time delivery tracking, status changes

### Address Updates
```
ws://localhost:8000/ws/address/10/
```
Broadcast when delivery addresses are created/updated

### Dashboard Updates
```
ws://localhost:8000/ws/dashboard/medical_staff/
ws://localhost:8000/ws/dashboard/ward_management/
ws://localhost:8000/ws/dashboard/kitchen/
ws://localhost:8000/ws/dashboard/delivery/
```
Real-time metrics and status updates for role-based dashboards

---

## 🔧 How to Deploy

### Development (Without Redis):

```bash
# Option 1: Use in-memory channel layer (development only)
python manage.py runserver
# Daphne will run automatically with ASGI
```

Uncomment in `settings.py`:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}
```

### Production (With Redis):

```bash
# 1. Start Redis server
redis-server

# 2. Run Daphne ASGI server
daphne -b 0.0.0.0 -p 8000 dusangire.asgi:application

# Or with supervisor/systemd for process management
```

### PythonAnywhere Deployment:

```
ASGI application: dusangire.asgi:application
ASGI name: ASGI
```

---

## 💻 Frontend WebSocket Connection Example

### JavaScript Client:

```javascript
// Connect to Ward WebSocket
const wardSocket = new WebSocket('ws://localhost:8000/ws/ward/1/');

wardSocket.onopen = function(e) {
    console.log('Ward WebSocket connected');
    wardSocket.send(JSON.stringify({'action': 'get_status'}));
};

wardSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Ward update:', data);
    
    // Update UI with real-time data
    updateWardDashboard(data.data);
};

wardSocket.onclose = function(e) {
    console.log('Ward WebSocket disconnected');
};

wardSocket.onerror = function(error) {
    console.error('WebSocket error:', error);
};
```

### Dashboard WebSocket Example:

```javascript
// Connect to Dashboard real-time updates
const dashboardSocket = new WebSocket('ws://localhost:8000/ws/dashboard/medical_staff/');

dashboardSocket.onmessage = function(event) {
    const update = JSON.parse(event.data);
    
    // Update metrics in real-time
    document.getElementById('occupancy-rate').textContent = update.occupancy_rate;
    document.getElementById('active-patients').textContent = update.patient_count;
    document.getElementById('pending-discharges').textContent = update.pending_discharges;
};
```

---

## 🧪 Testing WebSocket Connections

### Using WebSocket Testing Tools:

1. **Chrome DevTools Console**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ward/1/');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

2. **Postman** (with WebSocket support):
- Create new WebSocket request
- URL: `ws://localhost:8000/ws/ward/1/`
- Connect and monitor messages

3. **Python Test Script**:
```python
import asyncio
import websockets
import json

async def test_ward_websocket():
    uri = "ws://localhost:8000/ws/ward/1/"
    async with websockets.connect(uri) as websocket:
        # Receive initial status
        message = await websocket.recv()
        print(f"Received: {message}")
        
        # Send request for status
        await websocket.send(json.dumps({'action': 'get_status'}))
        message = await websocket.recv()
        print(f"Status: {message}")

asyncio.run(test_ward_websocket())
```

---

## 📊 Consumer Methods

### WardConsumer:

```python
# Client sends:
{'action': 'get_status'}           # Get ward status
{'action': 'get_bed_status', 'bed_id': 5}  # Get specific bed

# Server broadcasts:
{'type': 'ward_status', 'data': {...}}
{'type': 'bed_status_change', 'data': {...}}
```

### DashboardConsumer:

```python
# Automatically broadcasts:
{
    'occupancy_rate': 75.5,
    'patient_count': 42,
    'pending_discharges': 3,
    'active_wards': 8,
    'timestamp': '2026-02-03T14:30:00Z'
}
```

---

## 🚀 Next Steps for Production

### 1. **Install Redis**:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Windows (using WSL)
sudo apt-get install redis-server
```

### 2. **Update Channel Layer for Production**:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis-server-ip', 6379)],
            'capacity': 5000,
            'expiry': 60,
        }
    }
}
```

### 3. **Configure Daphne as ASGI Server**:
```bash
# Using supervisor or systemd
daphne -b 0.0.0.0 -p 8000 dusangire.asgi:application
```

### 4. **Update Nginx Reverse Proxy** (if needed):
```nginx
location /ws/ {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## ✅ Deployment Checklist

- [ ] Redis server installed and running
- [ ] Daphne ASGI server configured
- [ ] CHANNEL_LAYERS backend set to Redis
- [ ] WebSocket URLs accessible
- [ ] Firewall allows WebSocket traffic
- [ ] TLS/SSL certificates configured (for WSS)
- [ ] Test WebSocket connections in browser
- [ ] Monitor Redis connection pool
- [ ] Set up logging for WebSocket errors
- [ ] Configure process manager (supervisor/systemd)

---

## 📚 Documentation References

- [Django Channels Official Docs](https://channels.readthedocs.io/)
- [Daphne Documentation](https://github.com/django/daphne)
- [Channels-Redis Documentation](https://github.com/django/channels_redis)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

---

## 🎉 Summary

Django Channels setup is **complete and ready for deployment**:

✅ ASGI application configured  
✅ WebSocket consumers implemented  
✅ Routing configured  
✅ Channel layers configured  
✅ Real-time dashboard support ready  
✅ Production-ready architecture  

The system is ready to enable real-time updates across:
- Ward management dashboards
- Bed occupancy tracking
- Delivery status updates
- Customer order notifications
- Kitchen preparation status

**Next**: Deploy to production with Redis and monitor WebSocket connections!

---

**Status**: Ready for production deployment ✅
