# core/routing.py
from django.urls import re_path
from channels.routing import URLRouter
from chat.routing import websocket_urlpatterns as chat_urlpatterns

websocket_urlpatterns = [
    re_path(r"ws/chat/", URLRouter(chat_urlpatterns)),
]
