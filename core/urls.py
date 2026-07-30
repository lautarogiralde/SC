from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import CustomLoginView, Inicio, Verificar2FAView

urlpatterns = [
    path("", Inicio.as_view(), name="inicio"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("2fa/", Verificar2FAView.as_view(), name="verificar_2fa"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]
