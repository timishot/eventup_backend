
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_backend.settings')
django.setup()

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

# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
# from core.token_auth import TokenAuthMiddleware
# import event.routing
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_backend.settings')
#
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AllowedHostsOriginValidator(
#         TokenAuthMiddleware(
#             URLRouter(event.routing.websocket_urlpatterns)
#         )
#     ),
# })