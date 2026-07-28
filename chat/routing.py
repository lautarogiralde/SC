# chat/routing.py
from django.urls import re_path

from channels.routing import URLRouter
from . import consumers

websocket_urlpatterns = [
    re_path(r"(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
