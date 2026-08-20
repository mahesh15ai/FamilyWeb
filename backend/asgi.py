"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

Handles both standard HTTP requests and WebSocket connections via Django Channels.
"""

import os
from django.core.asgi import get_asgi_application

# 1. Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from apps.chat.middleware import JwtAuthMiddleware
import apps.chat.routing

# 2. Main Protocol Router
application = ProtocolTypeRouter({
    # Standard HTTP requests
    "http": django_asgi_app,

    # WebSocket requests authenticated via JWT token
    "websocket": JwtAuthMiddleware(
        URLRouter(apps.chat.routing.websocket_urlpatterns)
    ),
})