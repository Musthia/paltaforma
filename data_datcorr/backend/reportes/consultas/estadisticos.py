NOMBRE = "Estadísticos"
DESCRIPCION = "Crecimiento histórico, operaciones por mes, tendencias"
PERMISO_REQUERIDO = "admin"

COLUMNAS = ["periodo", "tipo", "cantidad"]

FILTROS = [
    {"key": "desde", "tipo": "date", "label": "Desde", "default": None},
    {"key": "hasta", "tipo": "date", "label": "Hasta", "default": None},
]


def ejecutar(repo, desde=None, hasta=None, es_admin=True, usuario_actual=""):
    WHERE = "1=1"
    params = {}
    if desde:
        WHERE += " AND fecha >= :desde"
        params["desde"] = desde
    if hasta:
        WHERE += " AND fecha <= :hasta"
        params["hasta"] = hasta

    # Crecimiento historico: operaciones por mes
    sql = f"""
        SELECT TO_CHAR(DATE_TRUNC('month', fecha), 'YYYY-MM') as periodo,
               'total_operaciones' as tipo,
               COUNT(*) as cantidad
        FROM public.auditoria
        WHERE {WHERE}
        GROUP BY DATE_TRUNC('month', fecha)
        ORDER BY periodo
    """
    resultados = repo.fetchall(sql, params)

    # Altas (CREATE) por mes
    sql = f"""
        SELECT TO_CHAR(DATE_TRUNC('month', fecha), 'YYYY-MM') as periodo,
               'altas' as tipo,
               COUNT(*) as cantidad
        FROM public.auditoria
        WHERE accion = 'CREATE' AND {WHERE}
        GROUP BY DATE_TRUNC('month', fecha)
        ORDER BY periodo
    """
    resultados += repo.fetchall(sql, params)

    # Consultas por mes
    sql = f"""
        SELECT TO_CHAR(DATE_TRUNC('month', fecha), 'YYYY-MM') as periodo,
               'consultas' as tipo,
               COUNT(*) as cantidad
        FROM public.auditoria
        WHERE accion = 'CONSULTA' AND {WHERE}
        GROUP BY DATE_TRUNC('month', fecha)
        ORDER BY periodo
    """
    resultados += repo.fetchall(sql, params)

    # Ocupación por base (total registros)
    schemas = [
        ("ips", "IPS"), ("pediatrico", "PEDIATRICO"), ("igpj", "IGPJ"),
        ("igpj_txt_listado", "IGPJ TXT LISTADO"), ("igpj_listado_nuevo", "IGPJ_LISTADO_NUEVO"),
        ("maternidad", "MATERNIDAD"), ("escribania", "ESCRIBANIA"),
    ]
    for schema, nombre in schemas:
        cnt = repo.scalar(f'SELECT COUNT(*) FROM "{schema}"."Datcorr_database"') or 0
        resultados.append({"periodo": "actual", "tipo": f"ocupacion_{nombre.lower().replace(' ','_')}", "cantidad": cnt})

    return resultados
