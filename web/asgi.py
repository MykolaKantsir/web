"""
ASGI config for web project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

# Configure Django settings FIRST, before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

# Initialize Django BEFORE importing models (must be before monitoring.routing)
import django
django.setup()

# Now safe to import Django/Channels modules
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from monitoring.routing import websocket_urlpatterns

# Get the Django ASGI application early to ensure Django is fully initialized
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
