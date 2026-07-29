from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario,
    DispositivoAutorizado,
    Rol,
    Area,
    AplicacionHabilitada,
    AplicacionPrincipal,
)


# 1. Áreas y Roles
@admin.register(Rol)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Area)
class AreasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


# 2. Aplicaciones y Sub-aplicaciones
@admin.register(AplicacionPrincipal)
class AplicacionPrincipalAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ruta_base')
    search_fields = ('nombre', 'ruta_base')


@admin.register(AplicacionHabilitada)
class AplicacionHabilitadaAdmin(admin.ModelAdmin):
    # Coincide exactamente con tu relación ForeignKey 'aplicacionPrincipal'
    list_display = ('id', 'nombre', 'ruta', 'aplicacionPrincipal')
    list_filter = ('aplicacionPrincipal',)
    search_fields = ('nombre', 'ruta', 'aplicacionPrincipal__nombre')


# 3. Dispositivos Autorizados
@admin.register(DispositivoAutorizado)
class DispositivoAutorizadoAdmin(admin.ModelAdmin):
    # Usamos ip_registrado y fecha_creacion respetando tu modelo
    list_display = (
        'usuario',
        'nombre_dispositivo',
        'ip_registrado',
        'autorizado',
        'fecha_creacion',
        'ultimo_acceso',
    )
    list_filter = ('autorizado',)
    search_fields = (
        'usuario__username',
        'nombre_dispositivo',
        'ip_registrado',
        'device_token',
    )
    list_editable = ('autorizado',)  # Permite activar/desactivar en un clic
    readonly_fields = (
        'device_token',
        'user_agent',
        'ip_registrado',
        'fecha_creacion',
        'ultimo_acceso',
    )


# 4. Usuario Personalizado
@admin.register(Usuario)
class UsuarioPersonalizadoAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'dni',
        'rol',
        'area',
        'is_staff',
        'is_active',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'rol', 'area', 'sexo')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'dni')
    readonly_fields = ('intentos_fallidos', 'ultimo_acceso', 'fecha_creacion')

    # Controles multiselección para las aplicaciones
    filter_horizontal = (
        'aplicaciones_principales',
        'aplicaciones_habilitadas',
        'groups',
        'user_permissions',
    )

    # Formulario para editar un usuario existente
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Información Personal',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'telefono',
                    'dni',
                    'sexo',
                )
            },
        ),
        (
            'Organización y Roles',
            {
                'fields': ('rol', 'area'),
            },
        ),
        (
            'Permisos de Aplicaciones',
            {
                'fields': (
                    'aplicaciones_principales',
                    'aplicaciones_habilitadas',
                ),
            },
        ),
        (
            'Permisos del Sistema',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
        (
            'Seguridad y Control',
            {
                'fields': (
                    'intentos_fallidos',
                    'ultimo_acceso',
                    'fecha_creacion',
                ),
            },
        ),
    )

    # Formulario para crear un usuario nuevo
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                'Información Personal',
                {
                    'fields': (
                        'first_name',
                        'last_name',
                        'email',
                        'telefono',
                        'dni',
                        'sexo',
                    )
                },
            ),
            (
                'Organización y Roles',
                {
                    'fields': ('rol', 'area'),
                },
            ),
            (
                'Permisos de Aplicaciones',
                {
                    'fields': (
                        'aplicaciones_principales',
                        'aplicaciones_habilitadas',
                    ),
                },
            ),
            (
                'Permisos del Sistema',
                {
                    'fields': (
                        'is_active',
                        'is_staff',
                        'is_superuser',
                    ),
                },
            ),
            (
                'Seguridad y Control',
                {
                    'fields': (
                        'intentos_fallidos',
                        'ultimo_acceso',
                        'fecha_creacion',
                    ),
                },
            ),
        )
    )
