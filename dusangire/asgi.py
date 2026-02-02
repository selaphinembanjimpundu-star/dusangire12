"""
ASGI config for dusangire project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusangire.settings')

django_asgi_app = get_asgi_application()

# Import routing after Django is set up
from hospital_wards.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # Django's ASGI application for HTTP requests
    'http': django_asgi_app,
    
    # WebSocket chat handler with authentication
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
