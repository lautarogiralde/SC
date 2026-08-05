from django.urls import path

from .views import ChatDashboardView, ChatPrueba

urlpatterns = [
    path("", ChatDashboardView.as_view(), name="lista_chats"),
    path("<uuid:uuid>/", ChatDashboardView.as_view(), name="detalle_chat"),
    path("prueba", ChatPrueba.as_view(), name="prueba"),
    path(
        "prueba/<uuid:uuid>/",
        ChatPrueba.as_view(),
        name="detalle_prueba",
    ),
]
