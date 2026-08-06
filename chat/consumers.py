# chat/consumers.py
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Chat, Mensaje


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Validar si tiene acceso al grupo
        self.chat_uuid = self.scope["url_route"]["kwargs"]["chat_uuid"]
        tiene_acceso = await self.es_miembro(self.chat_uuid, self.user)

        if not tiene_acceso:
            await self.close()
            return

        self.nombre_canal = f"chat_{self.chat_uuid}"
        await self.channel_layer.group_add(self.nombre_canal, self.channel_name)

        await self.accept()

    @database_sync_to_async
    def es_miembro(self, chat_uuid, user):
        return Chat.objects.filter(chat_uuid=chat_uuid, miembros=user).exists()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.nombre_canal, self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        texto_mensaje = data.get("texto")

        if not texto_mensaje or not texto_mensaje.strip():
            return

        mensaje_obj = await self.crear_mensaje(
            self.chat_uuid, self.user, texto_mensaje
        )

        await self.channel_layer.group_send(
            self.nombre_canal,
            {
                "type": "chat_message",
                "mensaje_id": mensaje_obj.id,
            },
        )

    # 2. ESTE MÉTODO SE EJECUTA EN CADA NAVEGADOR CONECTADO A LA SALA
    async def chat_message(self, event):
        mensaje_id = event["mensaje_id"]
        mensaje = await self.obtener_mensaje(mensaje_id)

        html_mensaje = f"""
        <div id="mensajes-log" hx-swap-oob="beforeend">
            <div class="mb-2">
                <strong>{mensaje.usuario.username}:</strong> {mensaje.texto}
            </div>
        </div>
        """

        await self.send(text_data=html_mensaje)

    @database_sync_to_async
    def crear_mensaje(self, chat_uuid, usuario, texto):
        chat = Chat.objects.get(chat_uuid=chat_uuid)
        return Mensaje.objects.create(chat=chat, usuario=usuario, texto=texto)

    @database_sync_to_async
    def obtener_mensaje(self, mensaje_id):
        return Mensaje.objects.select_related("usuario").get(id=mensaje_id)
