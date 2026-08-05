import uuid

from django.conf import settings
from django.db import models

# Create your models here.


class Chat(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=128, null=True, blank=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="chats",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    conectados = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="chats_activos", blank=True
    )
    miembros = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="mis_chats", blank=True
    )
    es_privado = models.BooleanField(default=False)

    def __str__(self):
        return str(self.uuid)


class Mensaje(models.Model):
    chat = models.ForeignKey(
        Chat, related_name="mensajes", on_delete=models.CASCADE
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    texto = models.CharField(max_length=300, blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} : {self.texto}"

    class Meta:
        ordering = ["-creado"]
