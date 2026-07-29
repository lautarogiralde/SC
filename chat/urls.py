from django.urls import path

from .views import ChatDashboardView

urlpatterns = [
    path("", ChatDashboardView.as_view(), name="lista_chats"),
    path("<uuid:chat_uuid>/", ChatDashboardView.as_view(), name="detalle_chat"),
]
