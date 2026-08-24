import uuid
from collections import defaultdict

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from simple_history.models import HistoricalRecords

# Create your models here.


class Area(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"


class AplicacionPrincipal(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ruta_base = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Aplicacion Principal"
        verbose_name_plural = "Aplicaciones Principales"


class AplicacionHabilitada(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    ruta = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    aplicacionPrincipal = models.ForeignKey(
        AplicacionPrincipal,
        on_delete=models.PROTECT,
        related_name="sub_aplicaciones",
    )

    def __str__(self):
        return f"{self.aplicacionPrincipal.nombre} - {self.nombre}"

    class Meta:
        verbose_name = "Aplicación Habilitada"
        verbose_name_plural = "Aplicaciones Habilitadas"


class Rol(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"


class Usuario(AbstractUser):
    rol = models.ForeignKey(
        Rol, on_delete=models.SET_NULL, null=True, blank=True
    )
    telefono = models.CharField(max_length=10)
    dni_validator = RegexValidator(
        regex=r"^\d{7,8}$",
        message="El DNI debe contener 7 u 8 dígitos sin puntos ni guiones.",
    )
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[dni_validator],
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Area",
    )
    SEXO_CHOICES = (
        ("M", "Masculino"),
        ("F", "Femenino"),
        ("O", "Otro"),
    )
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Sexo",
    )
    aplicaciones_principales = models.ManyToManyField(
        AplicacionPrincipal,
        blank=True,
        related_name="usuarios_con_acceso_completo",
    )
    aplicaciones_habilitadas = models.ManyToManyField(
        AplicacionHabilitada, blank=True
    )
    ultimo_acceso = models.DateTimeField(
        null=True, blank=True, verbose_name="Último Acceso"
    )
    fecha_creacion = models.DateTimeField(
        verbose_name="Fecha de Creación", default=timezone.now
    )
    intentos_fallidos = models.IntegerField(default=0)
    history = HistoricalRecords()

    def get_aplicaciones_habilitadas(self):
        conjunto = defaultdict(list)
        if (
            self.is_superuser
            or self.groups.filter(name="Administradores").exists()
        ):
            principales = AplicacionPrincipal.objects.prefetch_related(
                "sub_aplicaciones"
            ).order_by("nombre")

            for principal in principales:
                sub_aplicaciones = principal.sub_aplicaciones.all().order_by(
                    "nombre"
                )

                if sub_aplicaciones.exists():
                    for sub_aplicacion in sub_aplicaciones:
                        ruta_base = "/" + principal.ruta_base.strip("/")
                        ruta_sub = sub_aplicacion.ruta.lstrip("/")
                        url = (
                            f"{ruta_base}/{ruta_sub}" if ruta_sub else ruta_base
                        )

                        conjunto[principal].append(
                            {
                                "nombre": sub_aplicacion.nombre,
                                "url": url,
                            }
                        )
                else:
                    conjunto[principal] = []

        else:
            sub_aplicaciones = (
                AplicacionHabilitada.objects.filter(
                    Q(
                        aplicacionPrincipal__in=self.aplicaciones_principales.all()
                    )
                    | Q(id__in=self.aplicaciones_habilitadas.all())
                )
                .select_related("aplicacionPrincipal")
                .order_by("aplicacionPrincipal__nombre", "nombre")
                .distinct()
            )

        for aplicacion in sub_aplicaciones:
            ruta_base = "/" + aplicacion.aplicacionPrincipal.ruta_base.strip(
                "/"
            )
            ruta_sub = aplicacion.ruta.lstrip("/")
            url = f"{ruta_base}/{ruta_sub}" if ruta_sub else ruta_base
            conjunto[aplicacion.aplicacionPrincipal].append(
                {
                    "nombre": aplicacion.nombre,
                    "url": url,
                }
            )

        return [
            {
                "nombre": principal.nombre,
                "url": principal.ruta_base,
                "aplicaciones": subs,
            }
            for principal, subs in conjunto.items()
        ]

    def tiene_acceso(self, nombre_aplicacion):
        if (
            self.is_superuser
            or self.groups.filter(name="Administradores").exists()
        ):
            return True
        return self.aplicaciones_habilitadas.filter(
            nombre="nombre_aplicacion"
        ).exists()

    def save(self, *args, **kwargs):
        if not self.rol:
            rol_defecto, _ = Rol.objects.get_or_create(nombre="Invitado")
            self.rol = rol_defecto
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class DispositivoAutorizado(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dispositivos",
    )
    nombre_dispositivo = models.CharField(max_length=100)
    device_token = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False
    )
    user_agent = models.TextField()
    ip_registrado = models.GenericIPAddressField()
    autorizado = models.BooleanField(default=True)
    fecha_creacion = models.TimeField(auto_now_add=True)
    ultimo_acceso = models.TimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.first_name}, {self.usuario.last_name} - {self.nombre_dispositivo} ({'Autorizado' if self.autorizado else 'Denegado'})"
