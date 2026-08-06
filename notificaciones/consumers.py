# notificaciones/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificacionesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_authenticated:
            # Canal privado por ID de usuario
            self.nombre_canal = f"notificaciones_user_{self.user.id}"

            await self.channel_layer.group_add(
                self.nombre_canal, self.channel_name
            )
            # Canal general por si mandás notificaciones globales
            await self.channel_layer.group_add(
                "noticias_globales", self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "nombre_canal"):
            await self.channel_layer.group_discard(
                self.nombre_canal, self.channel_name
            )
            await self.channel_layer.group_discard(
                "noticias_globales", self.channel_name
            )

    # Recibe el evento enviado con group_send y lo manda por el WS a HTMX
    async def enviar_toast_html(self, event):
        await self.send(text_data=event["html"])
