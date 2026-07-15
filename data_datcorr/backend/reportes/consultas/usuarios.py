NOMBRE = "Usuarios"
DESCRIPCION = "Altas, bajas, modificaciones, roles y permisos de usuarios"
PERMISO_REQUERIDO = "admin"

COLUMNAS = ["usuario", "nombre", "rol", "activo", "es_superusuario", "nivel_seguridad"]

FILTROS = [
    {"key": "activo", "tipo": "select", "label": "Estado", "opciones": [{"valor": "", "texto": "Todos"}, {"valor": "true", "texto": "Activos"}, {"valor": "false", "texto": "Inactivos"}], "default": ""},
]


def ejecutar(repo, activo=None):
    WHERE = "1=1"
    params = {}
    if activo == "true":
        WHERE += " AND u.activo = true"
    elif activo == "false":
        WHERE += " AND u.activo = false"

    sql = f"""
        SELECT u.usuario, u.nombre, u.rol, u.activo, u.es_superusuario, u.nivel_seguridad
        FROM public.usuarios u
        WHERE {WHERE}
        ORDER BY u.id
    """
    return repo.fetchall(sql, params)
