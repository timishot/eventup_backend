"""
ASGI config for event_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# import os
#
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_backend.settings')
#
# application = get_asgi_application()


# eventup/asgi.py

# import os
# import django
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator

# Set the Django settings module
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_backend.settings')

# Initialize Django app registry
# django.setup()

# Import routing after Django setup to avoid AppRegistryNotReady
# from event.routing import websocket_urlpatterns
#
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AllowedHostsOriginValidator(
#         AuthMiddlewareStack(
#             URLRouter(websocket_urlpatterns)
#         )
#     ),
# })
# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_backend.settings')
#
#
# django_asgi_app = get_asgi_application()
#
#
# from core.token_auth import TokenAuthMiddleware
# import event.routing
#
# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AuthMiddlewareStack(
#         TokenAuthMiddleware(
#             URLRouter(
#                 event.routing.websocket_urlpatterns
#             )
#         )
#     ),
# })

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_backend.settings')
django.setup()  # Initialize Django before imports

from core.token_auth import TokenAuthMiddleware
import event.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter(
            event.routing.websocket_urlpatterns
        )
    ),
})