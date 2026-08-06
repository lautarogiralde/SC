import random
import uuid

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView

from notificaciones.services import notificar_usuario

from .forms import CustomLoginForm, Verificacion2FAForm
from .models import DispositivoAutorizado, Usuario


def enviar_codigo(codigo):
    # Implementar el envio de mensajes
    print(
        f"Mensaje enviado a los administradores: Tu codigo de verificacion es {codigo}"
    )


class CustomLoginView(LoginView):
    """
    Verifica que el dispositivo este en la white-list de dispositivos y en caso de
    no estarlo envia un codigo a los administradores para que lo validen
    """

    template_name = "core/login.html"
    form_class = CustomLoginForm

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return redirect('inicio')
    #     return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        token_cookie = self.request.COOKIES.get("device_token")

        if token_cookie:
            es_confiable = DispositivoAutorizado.objects.filter(
                usuario=user, device_token=token_cookie, autorizado=True
            ).exists()

            if es_confiable:
                user.ultimo_acceso = timezone.now()
                user.intentos_fallidos = 0
                user.save(update_fields=["ultimo_acceso", "intentos_fallidos"])
                return super().form_valid(form)

        codigo_otp = str(random.randint(100000, 999999))

        self.request.session["pre_2fa_user_id"] = user.id
        self.request.session["otp_code"] = codigo_otp
        self.request.session["otp_created_at"] = int(timezone.now().timestamp())

        enviar_codigo(codigo_otp)
        notificar_usuario(
            user_id=user.id,
            mensaje="Se envió el código de verificación a los administradores.",
            tag="info",
        )
        return redirect("verificar_2fa")

    def form_invalid(self, form):
        username = form.cleaned_data.get("username")

        try:
            user = Usuario.objects.get(username=username)
            if user.is_active:
                user.intentos_fallidos += 1
                if user.intentos_fallidos >= 5:
                    user.is_active = False
            user.save(update_fields=["intentos_fallidos", "is_active"])

        except Usuario.DoesNotExist:
            pass
        return super().form_invalid(form)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "0.0.0.0")
    return ip


class Verificar2FAView(FormView):
    template_name = "core/verificar_2fa.html"
    form_class = Verificacion2FAForm
    success_url = reverse_lazy("inicio")

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("pre_2fa_user_id"):
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Le pasa la sesión actual al Formulario para que pueda validar."""
        kwargs = super().get_form_kwargs()
        kwargs["session"] = self.request.session
        return kwargs

    def form_valid(self, form):
        user_id = self.request.session.get("pre_2fa_user_id")
        try:
            user = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            self._limpiar_sesion_temp()
            messages.error(self.request, "El usuario no existe")
            return redirect("login")

        self._limpiar_sesion_temp()
        login(self.request, user)

        nuevo_token = str(uuid.uuid4())
        user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        ip = get_client_ip(self.request)

        DispositivoAutorizado.objects.create(
            usuario=user,
            nombre_dispositivo=f"Navegador ({user_agent[:25]})...",
            device_token=nuevo_token,
            ip_registrado=ip,
            autorizado=True,
        )

        user.ultimo_acceso = timezone.now()
        user.intentos_fallidos = 0
        user.save(update_fields=["ultimo_acceso", "intentos_fallidos"])

        response = redirect(self.get_success_url())
        response.set_cookie(
            key="device_token",
            value=nuevo_token,
            max_age=365 * 24 * 60 * 60,
            httponly=True,
            samesite="Lax",
        )
        return response

    def form_invalid(self, form):
        # Si el error fue por expiración o sesión nula
        if any("EXPIRED" in error for error in form.non_field_errors()):
            self._limpiar_sesion_temp()
            user_id = self.request.session.get("pre_2fa_user_id")
            if user_id:
                notificar_usuario(
                    user_id=user_id,
                    mensaje="El código expiró. Vuelva a iniciar sesión.",
                    tag="error",
                )
            return redirect("login")

        # Si fue un error normal (código incorrecto / < 6 dígitos),
        # vuelve a cargar la pantalla de 2FA mostrando el error en el input.
        return super().form_invalid(form)

    def _limpiar_sesion_temp(self):
        self.request.session.pop("pre_2fa_user_id", None)
        self.request.session.pop("otp_code", None)
        self.request.session.pop("otp_created_at", None)


@login_required
def notificaciones_iniciales(request):
    notificar_usuario(
        user_id=request.user.id,
        mensaje="¡Esta es una notificación de éxito!",
        tag="success",
    )
    notificar_usuario(
        user_id=request.user.id,
        mensaje="Aviso informativo del sistema.",
        tag="info",
    )
    notificar_usuario(
        user_id=request.user.id,
        mensaje="Ocurrió un error grave al procesar la solicitud.",
        tag="error",
    )
    return HttpResponse("")


class Inicio(LoginRequiredMixin, TemplateView):
    template_name = "core/inicio.html"
    login_url = "/login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["username"] = user.first_name or user.username
        return context
