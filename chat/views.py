from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from .models import Chat, Mensaje


class ChatDashboardView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chat/dashboard.html"
    context_object_name = "chats"

    def get_queryset(self):
        return Chat.objects.filter(miembros=self.request.user)

    def get(self, request, *args, **kwargs):
        chat_uuid = kwargs.get("chat_uuid")
        if request.headers.get("HX-Request") and chat_uuid:
            chat = get_object_or_404(
                Chat, chat_uuid=chat_uuid, miembros=request.user
            )
            return render(
                request, "chat/dashboard.html#panel-chat", {"chat_activo": chat}
            )

        return super().get(request, *args, **kwargs)


class ChatPrueba(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chat/chat.html"
    context_object_name = "chats"

    def get_queryset(self):
        return Chat.objects.filter(miembros=self.request.user)

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        print(uuid)
        if request.headers.get("HX-Request") and uuid:
            chat_activo = get_object_or_404(
                Chat, uuid=uuid, miembros=request.user
            )
            return render(
                request,
                "chat/chat.html#panel-chat",
                {"chat_activo": chat_activo},
            )

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        if not uuid:
            return HttpResponseBadRequest("UUID requerido")

        chat = get_object_or_404(Chat, uuid=uuid, miembros=request.user)
        texto = request.POST.get("texto", "").strip()

        if texto:
            mensaje = Mensaje.objects.create(
                chat=chat, usuario=request.user, texto=texto
            )
            return render(
                request,
                "chat/chat.html#mensaje-chat",
                {"mensaje": mensaje},
            )

        return HttpResponseBadRequest("El mensaje no puede estar vacío")
