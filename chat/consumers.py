# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
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

        self.room_group_name = f"chat_{self.chat_uuid}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    @database_sync_to_async
    def es_miembro(self, chat_uuid, user):
        return Chat.objects.filter(chat_uuid=chat_uuid, miembros=user).exists()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)

        # HTMX envía los inputs usando su atributo 'name'.
        # Si en tu HTML pones <input name="cuerpo">, acá lees data.get("cuerpo")
        texto_mensaje = data.get("texto")

        if not texto_mensaje or not texto_mensaje.strip():
            return

        # Guardamos el mensaje en la base de datos de forma asíncrona
        mensaje_obj = await self.crear_mensaje(self.chat_uuid, self.user, texto_mensaje)

        # Emitimos un evento a TODOS los integrantes suscritos a este grupo de WebSocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",  # Llama al método 'chat_message' de abajo
                "mensaje_id": mensaje_obj.id,
            },
        )

    # 2. ESTE MÉTODO SE EJECUTA EN CADA NAVEGADOR CONECTADO A LA SALA
    async def chat_message(self, event):
        mensaje_id = event["mensaje_id"]
        mensaje = await self.obtener_mensaje(mensaje_id)

        # Renderizamos el fragmento HTML del mensaje
        # (puedes usar un snippet/partial o un string formateado)
        html_mensaje = f'''
        <div id="mensajes-log" hx-swap-oob="beforeend">
            <div class="mb-2">
                <strong>{mensaje.usuario.username}:</strong> {mensaje.texto}
            </div>
        </div>
        '''

        # HTMX intercepta este HTML enviado por el socket y lo inserta en el DOM
        await self.send(text_data=html_mensaje)

    # --- Consultas ORM asíncronas ---

    @database_sync_to_async
    def crear_mensaje(self, chat_uuid, usuario, texto):
        chat = Chat.objects.get(chat_uuid=chat_uuid)
        return Mensaje.objects.create(chat=chat, usuario=usuario, texto=texto)

    @database_sync_to_async
    def obtener_mensaje(self, mensaje_id):
        return Mensaje.objects.select_related("usuario").get(id=mensaje_id)
