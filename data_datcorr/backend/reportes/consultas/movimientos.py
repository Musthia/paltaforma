NOMBRE = "Movimientos"
DESCRIPCION = "Ingresos, egresos, devoluciones y movimientos por fecha/usuario"
PERMISO_REQUERIDO = None

COLUMNAS = ["fecha", "usuario", "accion", "tabla", "detalle"]

FILTROS = [
    {"key": "desde", "tipo": "date", "label": "Fecha desde", "default": None},
    {"key": "hasta", "tipo": "date", "label": "Fecha hasta", "default": None},
]


def ejecutar(repo, desde=None, hasta=None, es_admin=True, usuario_actual=None):
    WHERE = "1=1"
    params = {}
    if desde:
        WHERE += " AND a.fecha >= :desde"
        params["desde"] = desde
    if hasta:
        WHERE += " AND a.fecha <= :hasta"
        params["hasta"] = hasta
    if not es_admin and usuario_actual:
        WHERE += " AND a.usuario = :usuario_actual"
        params["usuario_actual"] = usuario_actual

    sql = f"""
        SELECT a.fecha, a.usuario, a.accion, a.tabla, a.detalle
        FROM public.auditoria a
        WHERE {WHERE}
        ORDER BY a.fecha DESC
        LIMIT 500
    """
    return repo.fetchall(sql, params)
