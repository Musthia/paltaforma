# Plan de Reportes - DatCorr ERP
# v2.4 - Consolidado con validaciones y manejo de errores

## Estado actual
- La ruta `/reportes` existe en el sidebar pero muestra solo un placeholder
- No hay componente de página, ni servicio, ni endpoints de backend
- Todos los usuarios ven el item en el menu (sin restricción de permisos)

## Datos disponibles para reportes
| Fuente | Descripción |
|--------|-------------|
| 7 bases documentales (IPS, PEDIATRICO, IGPJ, IGPJ_TXT_LISTADO, IGPJ_LISTADO_NUEVO, MATERNIDAD, ESCRIBANIA) | Tablas `Datcorr_database` con miles de registros cada una |
| `public.usuarios` | Usuarios del sistema con rol, nivel, activo/inactivo |
| `public.auditoria` | Traza completa de todas las operaciones (login, CRUD, consultas, búsquedas) con fecha, usuario, acción, detalle, IP |
| `public.refresh_tokens` | Sesiones activas de usuarios |
| `permisos` / `usuarios_permisos` | Permisos asignados por usuario |

## Objetivo
Crear un Dashboard de Reportes que:
- Ofrezca insights en tiempo real
- Sea configurable por rol (backend + frontend)
- Permita exportación rápida (CSV MVP, PDF futuro)
- Detecte anomalías automáticamente
- Se integre con el dashboard existente sin romper diseño

## Pre-requisitos: Índices PostgreSQL

Antes de implementar, asegurar estos índices para evitar queries lentos sobre `public.auditoria`:

```sql
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON public.auditoria (fecha);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario_fecha ON public.auditoria (usuario, fecha);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion_fecha ON public.auditoria (accion, fecha);
```

## Dependencias nuevas requeridas

```bash
# Frontend: gráficos ligeros y compatibles con MUI v9
cd frontend
npm install recharts
```

> Nota: NO se instalan `@mui/x-charts`, `@mui/x-date-pickers`, `date-fns` ni `dayjs`.
> Los gráficos se resuelven con `recharts`. Los selectores de fecha usan `<input type="date">` nativo
> (HTML5) para eliminar dependencias adicionales.
> Para fecha inicial por defecto se usa: `new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)` (30 días atrás, sin librerías).

## Arquitectura
```
frontend/src/services/reportesService.js  →  backend/routers/reportes_router.py  →  PostgreSQL
                        ↕                            ↕
frontend/src/pages/ReportesPage.jsx     backend/services/reportes_service.py
```

## Backend

Crear `backend/routers/reportes_router.py` con prefix `/reportes`.

Todos los endpoints usan `Depends(obtener_usuario_actual)` para mantener consistencia con el resto del proyecto. El usuario autenticado se recibe como parámetro de la función.

### Reglas de filtrado por rol (backend)

Cada endpoint aplica estas reglas internamente:

| Rol del usuario | Datos que ve |
|----------------|--------------|
| `es_superusuario` o `nivel_seguridad >= 10` | Todos los datos de todos los usuarios |
| cualquier otro | Solo su propia actividad (`WHERE usuario = :usuario_actual`) |

### 1. GET /reportes/kpis

Tres indicadores principales. `total_registros` se calcula con consultas separadas por schema:

```sql
-- KPI: Total registros en bases documentales
SELECT 'ips' AS base, COUNT(*) AS total FROM ips.Datcorr_database
UNION ALL SELECT 'pediatrico', COUNT(*) FROM pediatrico.Datcorr_database
UNION ALL SELECT 'igpj', COUNT(*) FROM igpj.Datcorr_database
UNION ALL SELECT 'igpj_txt_listado', COUNT(*) FROM igpj_txt_listado.Datcorr_database
UNION ALL SELECT 'igpj_listado_nuevo', COUNT(*) FROM igpj_listado_nuevo.Datcorr_database
UNION ALL SELECT 'maternidad', COUNT(*) FROM maternidad.Datcorr_database
UNION ALL SELECT 'escribania', COUNT(*) FROM escribania.Datcorr_database
```

En el servicio se itera sobre SCHEMAS y se ejecuta COUNT(*) individualmente para evitar que un schema lento bloquee todos los resultados.

```sql
-- KPI: Usuarios activos
SELECT COUNT(*) FROM public.usuarios WHERE activo = true

-- KPI: Total de usuarios
SELECT COUNT(*) FROM public.usuarios

-- KPI: Alertas pendientes (ver endpoint /alertas)
-- Se calcula en backend según reglas definidas abajo
```

Respuesta esperada:
```json
{
    "total_registros": 123456,
    "usuarios_activos": 25,
    "total_usuarios": 30,
    "alertas_pendientes": 3
}
```

### 2. GET /reportes/actividad-usuarios

Top N usuarios más activos en un rango de fechas. Con paginación y filtro por rol.

```sql
SELECT usuario, COUNT(*) as operaciones
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY usuario
ORDER BY operaciones DESC
LIMIT :limite OFFSET :offset
```

Parámetros:
- `desde`, `hasta`: ISO date (`YYYY-MM-DD`).
- `limite`: entero, mínimo 1, máximo 100.
- `pagina`: entero, mínimo 1.

Validaciones (aplicar en router con `Query(ge=..., le=...)`):
- Rango máximo: 365 días.
- `limite > 100` → HTTP 400.
- `pagina < 1` → HTTP 400.

### 3. GET /reportes/evolucion-diaria

Cantidad de operaciones por día en un rango. Para gráfico de línea.

```sql
SELECT DATE(fecha) as dia, COUNT(*) as operaciones
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY dia
ORDER BY dia
```

Mismas validaciones de rango de fechas que `actividad-usuarios`.

### 4. GET /reportes/tipos-operacion

Distribución de acciones (CREATE, UPDATE, DELETE, LOGIN, etc.).

```sql
SELECT accion, COUNT(*) as cantidad
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY accion
ORDER BY cantidad DESC
```

### 5. GET /reportes/usuarios-inactivos

Usuarios sin actividad en los últimos N días. **Incluye filtrado por rol**.

```sql
SELECT u.usuario, u.nombre, u.rol,
       (SELECT MAX(a.fecha) FROM public.auditoria a WHERE a.usuario = u.usuario) AS ultimo_acceso
FROM public.usuarios u
WHERE u.activo = true
  AND (:es_admin = true OR u.usuario = :usuario_actual)
  AND u.usuario NOT IN (
      SELECT DISTINCT a2.usuario
      FROM public.auditoria a2
      WHERE a2.fecha >= :fecha_limite
  )
ORDER BY ultimo_acceso ASC NULLS FIRST
```

Parámetros:
- `dias`: entero, mínimo 1, máximo 365.

Validaciones:
- `fecha_limite` se calcula en Python: `datetime.utcnow() - timedelta(days=dias)`.
- No usar interpolación SQL (`:dias || ' days'`). Pasar fecha ya calculada desde Python.

### 6. GET /reportes/actividad-bases

Cantidad de registros por base documental.

```python
# Se itera sobre MAPA_BASE_SCHEMA (verificar si existe en database_router;
# si no, definir constante local en reportes_service.py)
# y se ejecuta: SELECT COUNT(*) FROM "{schema}"."Datcorr_database"
# Retorna array de { base, schema, registros }
```

Validación de schema:
- Usar lista blanca: `VALID_SCHEMAS = ["ips", "pediatrico", "igpj", "igpj_txt_listado", "igpj_listado_nuevo", "maternidad", "escribania"]`.
- Si se recibe un schema por query param, validar contra `VALID_SCHEMAS` antes de ejecutar.

### 7. GET /reportes/alertas

Alertas proactivas del sistema. Backend clasifica por severidad (baja/media/alta).

Reglas implementadas:

```sql
-- Regla 1: Borrados masivos recientes (> 50 DELETE en 24h)
-- Severidad: Alta
SELECT usuario, COUNT(*) as borrados
FROM public.auditoria
WHERE accion IN ('DELETE', 'DELETE_LOGICO')
  AND fecha >= NOW() - INTERVAL '24 hours'
GROUP BY usuario
HAVING COUNT(*) > 50
```

```sql
-- Regla 2: Usuarios sin acceso reciente (> 30 días sin actividad)
-- Severidad: Media
-- Reutiliza lógica de usuarios-inactivos con parámetro de días configurable.
```

```sql
-- Regla 3: Intentos de login fallidos (si existe LOGIN_FAILED en auditoria)
-- Severidad: Alta
SELECT usuario, COUNT(*) as intentos_fallidos
FROM public.auditoria
WHERE accion = 'LOGIN_FAILED'
  AND fecha >= NOW() - INTERVAL '24 hours'
GROUP BY usuario
HAVING COUNT(*) >= 5
```

Registro de alertas (logging):
```python
import logging

logger = logging.getLogger(__name__)

if severidad == "alta":
    logger.warning(f"Alerta de alto nivel: {detalle}")
elif severidad == "media":
    logger.info(f"Alerta de nivel medio: {detalle}")
else:
    logger.debug(f"Alerta de nivel bajo: {detalle}")
```

Respuesta esperada:
```json
[
    {
        "regla": "borrados_masivos",
        "severidad": "alta",
        "detalle": "Usuario 'jperez' realizó 87 eliminaciones en las últimas 24 horas.",
        "cantidad_afectados": 1
    }
]
```

### 8. GET /reportes/exportar?formato=csv

Exportar datos de cualquier reporte en CSV.

Contract del endpoint:
- `formato`: solo `csv` en MVP. PDF pospuesto.
- `tipo`: uno de `TIPOS_EXPORTABLES = ["actividad-usuarios", "evolucion-diaria", "tipos-operacion", "usuarios-inactivos", "actividad-bases"]`.
- `desde`, `hasta`: ISO date (opcional, dependiendo del tipo).
- `limite`: entero, mínimo 1, máximo 100.

Validaciones:
- `tipo` debe estar en `TIPOS_EXPORTABLES`.
- `formato` debe ser `csv`.

Implementación robusta:
```python
import csv
import io
import logging
from datetime import datetime, timedelta
from fastapi import HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from backend.security.jwt_bearer import obtener_usuario_actual

logger = logging.getLogger(__name__)

TIPOS_EXPORTABLES = [
    "actividad-usuarios",
    "evolucion-diaria",
    "tipos-operacion",
    "usuarios-inactivos",
    "actividad-bases"
]

def parse_fecha(fecha_str: str) -> datetime:
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Formato de fecha inválido. Use YYYY-MM-DD.")

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

@router.get("/exportar")
def exportar(
    formato: str = Query("csv", regex="^csv$"),
    tipo: str = Query(..., description="Tipo de reporte a exportar"),
    desde: str = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    hasta: str = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    limite: int = Query(100, ge=1, le=100),
    usuario_actual=Depends(obtener_usuario_actual),
):
    if tipo not in TIPOS_EXPORTABLES:
        raise HTTPException(400, f"Tipo de reporte '{tipo}' no válido.")

    if formato != "csv":
        raise HTTPException(400, "Formato no soportado. Use 'csv'.")

    fecha_desde = parse_fecha(desde) if desde else datetime.utcnow() - timedelta(days=30)
    fecha_hasta = parse_fecha(hasta) if hasta else datetime.utcnow()

    if fecha_desde > fecha_hasta:
        raise HTTPException(400, "La fecha 'desde' no puede ser posterior a 'hasta'.")

    if (fecha_hasta - fecha_desde).days > 365:
        raise HTTPException(400, "El rango de fechas no puede superar 1 año.")

    # Delegar a servicio según tipo
    datos = reportes_service.obtener_datos_exportar(tipo, fecha_desde, fecha_hasta, limite, usuario_actual)
    return generar_csv(datos, f"reporte_{tipo}_{fecha_desde.date()}")
```

### Manejo de excepciones (global en router)

```python
from fastapi import HTTPException

@router.get("/kpis")
def kpis(...):
    try:
        # ... lógica ...
        return resultado
    except Exception as e:
        logger.error(f"Error calculando KPIs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor. Por favor intente nuevamente."
        )
```

> Nota: No exponer detalles del error en producción.

### Cache (servicio)

```python
from functools import lru_cache
import datetime

@lru_cache(maxsize=100, typed=True)
def get_kpis_cached(usuario_id: int, es_admin: bool):
    return get_kpis(usuario_id, es_admin)

@lru_cache(maxsize=100, typed=True)
def get_actividad_usuarios_cached(usuario_id: int, desde: str, hasta: str, limite: int):
    return get_actividad_usuarios(usuario_id, desde, hasta, limite)
```

> Nota: `lru_cache` funciona en memoria por proceso. Si hay múltiples workers (gunicorn), cada uno tiene su propia cache. El TTL debe manejarse en capa de aplicación o con Redis si se requiere cache distribuida.

## Permisos y seguridad (backend)

Todos los endpoints usan `Depends(obtener_usuario_actual)` y filtran datos según el rol:

```python
from fastapi import APIRouter, Depends, Query
from backend.security.jwt_bearer import obtener_usuario_actual
from sqlalchemy.orm import Session
from backend.dependencies import get_db

router = APIRouter(prefix="/reportes", tags=["reportes"])

@router.get("/kpis")
def kpis(
    usuario_actual=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    es_admin = usuario_actual.es_superusuario or usuario_actual.nivel_seguridad >= 10
    # ... lógica segura ...
```

Reglas:
- **SUPERUSUARIO / nivel >= 10**: acceso total a todos los datos.
- **RESTO**: solo sus propias métricas. Queries con `AND (:es_admin = true OR usuario = :usuario_actual)`.

## Frontend

### Servicio: `frontend/src/services/reportesService.js`

```javascript
import api from "../api/axiosClient";

export const getKpis = async () => api.get("/reportes/kpis");

export const getActividadUsuarios = async (desde, hasta, limite = 10, pagina = 1) =>
    api.get("/reportes/actividad-usuarios", { params: { desde, hasta, limite, pagina } });

export const getEvolucionDiaria = async (desde, hasta) =>
    api.get("/reportes/evolucion-diaria", { params: { desde, hasta } });

export const getTiposOperacion = async (desde, hasta) =>
    api.get("/reportes/tipos-operacion", { params: { desde, hasta } });

export const getUsuariosInactivos = async (dias = 30) =>
    api.get("/reportes/usuarios-inactivos", { params: { dias } });

export const getActividadBases = async () => api.get("/reportes/actividad-bases");

export const getAlertas = async () => api.get("/reportes/alertas");

export const exportarReporte = async (tipo, formato = "csv", desde, hasta, limite = 100) =>
    api.get("/reportes/exportar", {
        params: { formato, tipo, desde, hasta, limite },
        responseType: "blob"
    });
```

### Página: `frontend/src/pages/ReportesPage.jsx`

Layout por tabs, compatible con el diseño del dashboard existente.

Estado local:
```javascript
const [fechaDesde, setFechaDesde] = useState(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)  // 30 días atrás sin librerías
);
const [fechaHasta, setFechaHasta] = useState(new Date());
const [tabIndex, setTabIndex] = useState(0);
const [loading, setLoading] = useState(false);
const [kpis, setKpis] = useState(null);
const [actividad, setActividad] = useState([]);
const [evolucion, setEvolucion] = useState([]);
const [tiposOperacion, setTiposOperacion] = useState([]);
const [usuariosInactivos, setUsuariosInactivos] = useState([]);
const [actividadBases, setActividadBases] = useState([]);
const [alertas, setAlertas] = useState([]);
```

### Componente de tabs: `frontend/src/components/ReportesTabs.jsx`

Encapsula los tabs y renderiza el contenido correspondiente a cada tab:

- **Resumen**: KPIs en Cards MUI + DataGrid `actividad-usuarios`
- **Actividad**: Gráfico de línea `recharts` (evolución diaria) + DataGrid detalle
- **Operaciones**: Gráfico de barras `recharts` (distribución por tipo) + DataGrid
- **Bases**: DataGrid actividad por base documental
- **Alertas**: Lista de alertas agrupadas por severidad con iconos MUI

### Selector de fechas (nativo HTML)

```javascript
const toISODate = (date) => date.toISOString().split('T')[0];

<input
    type="date"
    value={toISODate(fechaDesde)}
    onChange={(e) => setFechaDesde(new Date(e.target.value))}
/>
<input
    type="date"
    value={toISODate(fechaHasta)}
    onChange={(e) => setFechaHasta(new Date(e.target.value))}
/>
```

Sin dependencias de date-pickers.

## Mejores prácticas

1. **Validaciones tempranas**: rango de fechas (max 365 días), límite (max 100), tipo de exportación (lista blanca `TIPOS_EXPORTABLES`).
2. **Paginación server-side** como en DatabasePage.
3. **Fechas**: enviar como ISO strings (`YYYY-MM-DD`). Parsear en backend con `datetime.strptime`.
4. **Permisos**: filtrar SIEMPRE en backend. El frontend solo oculta visualmente.
5. **Cache**: `lru_cache` en capa de servicio por `(usuario_id, es_admin, desde, hasta)`. TTL manejado en aplicación para MVP.
6. **Exportación**: CSV con `csv` stdlib + `StreamingResponse`. Manejo de errores con logging.
7. **Gráficos**: usar `recharts` (instalado via npm).
8. **Rendimiento**: consultas sobre `public.auditoria` usan los índices definidos en el pre-requisito.
9. **Roles**: el backend expone solo los datos permitidos; el frontend adapta la UI.
10. **Logging**: registrar alertas con nivel según severidad (`warning`, `info`, `debug`).
11. **Manejo de excepciones**: `try/except` genérico en endpoints con mensaje genérico en producción y `logger.error` con `exc_info=True`.
12. **Validación de schemas**: lista blanca `VALID_SCHEMAS` en endpoint `actividad-bases` o servicio, para evitar inyección SQL por nombre de schema.

## Resumen de archivos a crear/modificar

| Archivo | Acción |
|---------|--------|
| `backend/routers/reportes_router.py` | Crear (8 endpoints con `Depends` + validaciones) |
| `backend/services/reportes_service.py` | Crear (lógica de consultas + alertas + cache + exportación) |
| `backend/main.py` | Agregar `app.include_router(reportes_router)` |
| `frontend/src/services/reportesService.js` | Crear (8 funciones) |
| `frontend/src/pages/ReportesPage.jsx` | Crear (página completa con tabs) |
| `frontend/src/components/ReportesTabs.jsx` | Crear (componente reutilizable de tabs) |
| `frontend/src/router/AppRouter.jsx` | Reemplazar placeholder por `<ReportesPage />` |
| `frontend/src/layouts/Sidebar.jsx` | Agregar permiso adecuado al item Reportes |

## Orden sugerido de implementación

1. Ejecutar scripts SQL de índices PostgreSQL.
2. Backend: servicio + router (consultas SQL + endpoints + alertas + filtrado por rol + validaciones).
3. Registrar router en `main.py`.
4. Instalar `recharts` en frontend.
5. Frontend: servicio (`reportesService.js`).
6. Frontend: componente `ReportesTabs.jsx`.
7. Frontend: página `ReportesPage.jsx` con tabs y widgets.
8. Frontend: exportación CSV.
9. Frontend: restringir permiso en Sidebar.
10. Testing + validación de roles (probar que un USUARIO no ve datos de otros).
11. Documentación para usuarios.

## Postergado (no MVP)
- Exportación PDF (definir `reportlab` o `xhtml2pdf` e instalar, o alternativa HTML→PDF).
- Dashboard configurable por usuario.
- Drill-down desde gráficos a detalle.
- Comparativa interanual.
- Reportes programados por email.
