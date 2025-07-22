from django.urls import re_path
from .consumers import EventConsumer

websocket_urlpatterns = [
    re_path(r'ws/event/(?P<event_id>[^/]+)/$', EventConsumer.as_asgi()),
]