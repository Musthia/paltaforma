NOMBRE = "Inventario"
DESCRIPCION = "Cantidad de expedientes, cajas, estado, organismo y localidad"
PERMISO_REQUERIDO = None

COLUMNAS = ["schema", "base", "registros"]

FILTROS = []

def ejecutar(repo):
    schemas = [
        ("ips", "IPS"), ("pediatrico", "PEDIATRICO"), ("igpj", "IGPJ"),
        ("igpj_txt_listado", "IGPJ TXT LISTADO"), ("igpj_listado_nuevo", "IGPJ_LISTADO_NUEVO"),
        ("maternidad", "MATERNIDAD"), ("escribania", "ESCRIBANIA"),
    ]
    resultados = []
    for schema, nombre in schemas:
        cnt = repo.scalar(f'SELECT COUNT(*) FROM "{schema}"."Datcorr_database"') or 0
        resultados.append({"schema": schema, "base": nombre, "registros": cnt})
    return resultados
