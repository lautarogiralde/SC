# core/routing.py
from channels.routing import URLRouter
from django.urls import re_path

from chat.routing import websocket_urlpatterns as chat_urlpatterns
from notificaciones.routing import (
    websocket_urlpatterns as notificaciones_urlpatterns,
)

websocket_urlpatterns = [
    re_path(r"ws/chat/", URLRouter(chat_urlpatterns)),
    re_path(r"ws/notificaciones", URLRouter(notificaciones_urlpatterns)),
]
