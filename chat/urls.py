from django.urls import path

from .views import index, room, chat

urlpatterns = [
    path("", index, name="index"),
    path("chat", chat, name="chat"),
    path("<str:room_name>/", room, name="room"),
]
