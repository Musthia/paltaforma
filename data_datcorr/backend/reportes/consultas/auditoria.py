NOMBRE = "Auditoría"
DESCRIPCION = "Operaciones, usuarios, fechas, IPs y detalle de actividad"
PERMISO_REQUERIDO = "admin"

COLUMNAS = ["fecha", "usuario", "accion", "tabla", "registro_id", "ip", "detalle"]

FILTROS = [
    {"key": "desde", "tipo": "date", "label": "Fecha desde", "default": None},
    {"key": "hasta", "tipo": "date", "label": "Fecha hasta", "default": None},
    {"key": "usuario", "tipo": "text", "label": "Usuario", "default": ""},
    {"key": "accion", "tipo": "select", "label": "Acción", "opciones": [
        {"valor": "", "texto": "Todas"},
        {"valor": "CREATE", "texto": "Creación"},
        {"valor": "UPDATE", "texto": "Actualización"},
        {"valor": "DELETE", "texto": "Eliminación"},
        {"valor": "LOGIN", "texto": "Inicio sesión"},
        {"valor": "LOGOUT", "texto": "Cierre sesión"},
        {"valor": "CONSULTA", "texto": "Consulta"},
        {"valor": "BUSQUEDA", "texto": "Búsqueda"},
    ], "default": ""},
]


def ejecutar(repo, desde=None, hasta=None, usuario="", accion="", es_admin=True, usuario_actual=None):
    WHERE = "1=1"
    params = {}
    if desde:
        WHERE += " AND a.fecha >= :desde"
        params["desde"] = desde
    if hasta:
        WHERE += " AND a.fecha <= :hasta"
        params["hasta"] = hasta
    if usuario:
        WHERE += " AND a.usuario ILIKE :usuario"
        params["usuario"] = f"%{usuario}%"
    if accion:
        WHERE += " AND a.accion = :accion"
        params["accion"] = accion
    if not es_admin and usuario_actual:
        WHERE += " AND a.usuario = :usuario_actual"
        params["usuario_actual"] = usuario_actual

    sql = f"""
        SELECT a.fecha, a.usuario, a.accion, a.tabla, a.registro_id, a.ip, a.detalle
        FROM public.auditoria a
        WHERE {WHERE}
        ORDER BY a.fecha DESC
        LIMIT 500
    """
    return repo.fetchall(sql, params)
