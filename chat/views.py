from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render
from .models import Chat


class ChatDashboardView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chat/dashboard.html"
    context_object_name = "chats"

    def get_queryset(self):
        # Listamos solo las salas del usuario autenticado
        return Chat.objects.filter(miembros=self.request.user)

    def get(self, request, *args, **kwargs):
        # Si la petición es de HTMX y viene con una sala_uuid en la URL
        chat_uuid = kwargs.get("chat_uuid")

        if request.headers.get("HX-Request") and chat_uuid:
            chat = get_object_or_404(Chat, chat_uuid=chat_uuid, miembros=request.user)
            # Renderizamos SOLAMENTE el partial del chat seleccionado
            return render(
                request, "chat/dashboard.html#panel-chat", {"chat_activo": chat}
            )

        return super().get(request, *args, **kwargs)
