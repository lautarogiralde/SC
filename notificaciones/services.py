# notificaciones/services.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.template.loader import render_to_string


class MockMessage:
    """Clase auxiliar para emular la estructura de los mensajes de Django."""

    def __init__(self, texto, tags):
        self.texto = texto
        self.tags = tags

    def __str__(self):
        return self.texto


def notificar_usuario(user_id, mensaje, tag="info"):
    """Envía un Toast en tiempo real vía WebSockets a un usuario específico.
    Tags comunes: 'success', 'error', 'info', 'warning'
    """
    channel_layer = get_channel_layer()

    html = render_to_string(
        "base.html#lista-toast",
        {"messages": [MockMessage(mensaje, tag)]},
    )

    async_to_sync(channel_layer.group_send)(
        f"notificaciones_user_{user_id}",
        {
            "type": "enviar_toast_html",
            "html": html,
        },
    )


def notificar_global(mensaje, tag="info"):
    """Envía un Toast en tiempo real a TODOS los usuarios conectados en la plataforma."""
    channel_layer = get_channel_layer()

    html = render_to_string(
        "base.html#lista-toast",
        {"messages": [MockMessage(mensaje, tag)]},
    )

    async_to_sync(channel_layer.group_send)(
        "noticias_globales",
        {
            "type": "enviar_toast_html",
            "html": html,
        },
    )
