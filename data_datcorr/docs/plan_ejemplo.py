from fastapi import HTTPException, Query

# Validar rango de fechas
if (hasta - desde).days > 365:
    raise HTTPException(400, "El rango de fechas no puede superar 1 año.")

# Validar límite de paginación
if limite > 100:
    raise HTTPException(400, "El límite máximo de resultados es 100.")

# Validar tipo de exportación
if tipo not in TIPOS_EXPORTABLES:
    raise HTTPException(400, "Tipo de reporte no válido.")


from fastapi import HTTPException, Query

# Validar rango de fechas
if (hasta - desde).days > 365:
    raise HTTPException(400, "El rango de fechas no puede superar 1 año.")

# Validar límite de paginación
if limite > 100:
    raise HTTPException(400, "El límite máximo de resultados es 100.")

# Validar tipo de exportación
if tipo not in TIPOS_EXPORTABLES:
    raise HTTPException(400, "Tipo de reporte no válido.")


from fastapi import HTTPException

@router.get("/kpis")
def kpis(...):
    try:
        # ... lógica segura ...
    except Exception as e:
        # Mensaje genérico en producción
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor. Por favor intente nuevamente."
        )


from functools import lru_cache
import datetime

@lru_cache(maxsize=100, typed=True)
def get_kpis_cached(usuario_id: int):
    return get_kpis(usuario_id)

# Cache por 1 minuto para consultas frecuentes
@lru_cache(maxsize=100, typed=True)
def get_actividad_usuarios_cached(usuario_id: int, desde: str, hasta: str):
    return get_actividad_usuarios(usuario_id, desde, hasta)


# Validar que el schema sea de la lista definida
if schema not in SCHEMAS:
    raise HTTPException(400, f"Schema '{schema}' no válido.")

# O usar una lista blanca más estricta
VALID_SCHEMAS = ["ips", "pediatrico", "igpj", "maternidad", "escribania"]
if schema not in VALID_SCHEMAS:
    raise HTTPException(400, f"Schema '{schema}' no válido.")


import logging

logger = logging.getLogger(__name__)

# Logear alertas con nivel apropiado
if severidad == "alta":
    logger.warning(f"Alerta de alto nivel: {detalle}")
elif severidad == "media":
    logger.info(f"Alerta de nivel medio: {detalle}")
else:
    logger.debug(f"Alerta de nivel bajo: {detalle}")


from fastapi import Query

# Validar dias
dias: int = Query(ge=1, le=365, description="Días para verificar inactividad")

# Validar limite
limite: int = Query(ge=1, le=100, description="Límite de resultados")

# Validar pagina
pagina: int = Query(ge=1, description="Número de página")


from fastapi import HTTPException
from fastapi.responses import StreamingResponse

def generar_csv(datos: list[dict], nombre_archivo: str):
    try:
        if not datos:
            return StreamingResponse(io.StringIO(""), media_type="text/csv")
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=datos[0].keys())
        writer.writeheader()
        writer.writerows(datos)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={nombre_archivo}.csv"}
        )
    except Exception as e:
        logger.error(f"Error generando CSV: {e}")
        raise HTTPException(500, "Error al generar el archivo CSV")


from datetime import datetime

def parse_fecha(fecha_str: str) -> datetime:
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Formato de fecha inválido. Use YYYY-MM-DD.")

# Validar que ambas fechas sean válidas
fecha_desde = parse_fecha(fecha_desde)
fecha_hasta = parse_fecha(fecha_hasta)

if fecha_desde > fecha_hasta:
    raise HTTPException(400, "La fecha 'desde' no puede ser posterior a 'hasta'.")


# Documentar claramente cómo se calculan las alertas
# Ejemplo:
"""
Regla 1: Borrados masivos recientes
- Ventana: 24 horas
- Umbral: 50 operaciones DELETE en 24h
- Severidad: Alta
- Usuarios afectados: 1-10
"""
