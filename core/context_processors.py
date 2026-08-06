def get_navbar_items(request):
    # Si el usuario no está logueado, devolvemos una lista vacía o enlaces públicos
    if not request.user.is_authenticated:
        return {"secretarias": []}

    user = request.user
    secretarias = []

    principales = user.aplicaciones_principales.prefetch_ralted(
        "sub_aplicaciones"
    ).all()

    for principal in principales:
        secretarias.append(
            {
                "nombre": principal.nombre,
                "url": principal.ruta_base,
                "aplicaciones": [
                    {
                        "nombre": sub.nombre,
                        "url": sub.ruta,
                    }
                    for sub in principal.sub_aplicaciones.all()
                ],
            }
        )
    # 1. Módulo de Usuarios (Ejemplo: Solo si es superusuario o tiene un permiso específico)
    if user.is_superuser or user.has_perm("auth.view_user"):
        secretarias.append(
            {
                "nombre": "Gestión de Usuarios",
                "url": "/#",
                "aplicaciones": [
                    {"nombre": "Listar Usuarios", "url": "/#"},
                    {"nombre": "Crear Usuario", "url": "/#"},
                ],
            }
        )

    # 2. Módulo de Base de Datos (Ejemplo: Según pertenencia a un Grupo)
    if (
        user.groups.filter(name="Administradores de Datos").exists()
        or user.is_superuser
    ):
        secretarias.append(
            {
                "nombre": "Administración de Datos",
                "url": "/datos/",
                "aplicaciones": [
                    {"nombre": "Carga Masiva", "url": "/datos/carga/"},
                    {"nombre": "Auditoría", "url": "/datos/auditoria/"},
                ],
            }
        )

    # 3. Módulo de Reportes (Ejemplo: Disponible para cualquier usuario autenticado)
    secretarias.append(
        {
            "nombre": "Reportes y Métricas",
            "url": "/reportes/",
            "aplicaciones": [
                {"nombre": "Ver Estadísticas", "url": "/reportes/metricas/"},
            ],
        }
    )

    return {"secretarias": secretarias}
