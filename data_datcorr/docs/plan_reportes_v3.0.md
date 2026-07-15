# Plan de Reportes - DatCorr ERP
# v3.0 - Consolidado final

## Estado actual
- La ruta `/reportes` existe en el sidebar pero muestra solo un placeholder
- No hay componente de pagina, ni servicio, ni endpoints de backend
- Todos los usuarios ven el item en el menu (sin restriccion de permisos)

## Datos disponibles para reportes
| Fuente | Descripcion |
|--------|-------------|
| 7 bases documentales (IPS, PEDIATRICO, IGPJ, IGPJ_TXT_LISTADO, IGPJ_LISTADO_NUEVO, MATERNIDAD, ESCRIBANIA) | Tablas `Datcorr_database` con miles de registros cada una |
| `public.usuarios` | Usuarios del sistema con rol, nivel, activo/inactivo |
| `public.auditoria` | Traza completa de todas las operaciones (login, CRUD, consultas, busquedas) con fecha, usuario, accion, detalle, IP |
| `public.refresh_tokens` | Sesiones activas de usuarios |
| `permisos` / `usuarios_permisos` | Permisos asignados por usuario |

## Objetivo
Crear un Dashboard de Reportes que:
- Ofrezca insights en tiempo real
- Sea configurable por rol (backend + frontend)
- Permita exportacion rapida (CSV MVP, PDF futuro)
- Detecte anomalias automaticamente
- Se integre con el dashboard existente sin romper disenio

## Pre-requisitos: Indices PostgreSQL

```sql
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON public.auditoria (fecha);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario_fecha ON public.auditoria (usuario, fecha);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion_fecha ON public.auditoria (accion, fecha);
CREATE INDEX IF NOT EXISTS ON "schema"."Datcorr_database" ("id_Datcorr_database");
```

## Dependencias nuevas requeridas

```bash
cd frontend && npm install recharts
# Backend PDF: pip install reportlab (postergado)
```

> Sin `@mui/x-charts`, `@mui/x-date-pickers`, `date-fns` ni `dayjs`.
> Graficos con `recharts`. Selectores de fecha con `<input type="date">` nativo HTML5.
> Fecha inicial: `new Date(new Date().getTime() - 30 * 24 * 60 * 60 * 1000)`.
> Envio al backend: `.toLocaleDateString("en-CA")` para YYYY-MM-DD en timezone local.

## Arquitectura

```
frontend/src/services/reportesService.js  →  backend/routers/reportes_router.py  →  PostgreSQL
                        ↕                            ↕
frontend/src/pages/ReportesPage.jsx     backend/services/reportes_service.py
```

## Backend

Crear `backend/services/reportes_service.py` (logica) y `backend/routers/reportes_router.py` (endpoints).

Todos los endpoints usan `Depends(obtener_usuario_actual)` (no `request.state.user`).
`es_admin = usuario_actual.es_superusuario or usuario_actual.nivel_seguridad >= 10`.

### Patron comun de endpoint seguro

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.security.jwt_bearer import obtener_usuario_actual
from backend.dependencies import get_db

router = APIRouter(prefix="/reportes", tags=["reportes"])

@router.get("/kpis")
def kpis(
    usuario_actual=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    es_admin = usuario_actual.es_superusuario or usuario_actual.nivel_seguridad >= 10
    try:
        # ... logica segura ...
    except Exception as e:
        logger.error(f"Error en kpis: {e}")
        raise HTTPException(500, "Error interno del servidor. Intente nuevamente.")
```

### Cache con lru_cache

```python
from functools import lru_cache

@lru_cache(maxsize=100, typed=True)
def get_kpis_cached(usuario_id: int):
    return get_kpis(usuario_id)

@lru_cache(maxsize=100, typed=True)
def get_actividad_usuarios_cached(usuario_id: int, desde: str, hasta: str):
    return get_actividad_usuarios(usuario_id, desde, hasta)
```

> La cache incluye `usuario_id` en la key para evitar que un usuario reciba datos de otro.
> Invalidar con `get_kpis_cached.cache_clear()` si se necesita.

### Funcion helper para parsear fechas

```python
from datetime import datetime

def parse_fecha(fecha_str: str) -> datetime:
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Formato de fecha invalido. Use YYYY-MM-DD.")
```

### Reglas de filtrado por rol

| Rol | Datos que ve |
|-----|-------------|
| `es_superusuario` o `nivel_seguridad >= 10` | Todos los datos |
| cualquier otro | Solo su propia actividad (`WHERE usuario = :usuario_actual`) |

### 1. GET /reportes/kpis

Cuatro indicadores con `total_registros` calculado por schema individual (mas eficiente que UNION ALL):

```python
SCHEMAS = [
    ("ips","ips"), ("pediatrico","pediatrico"), ("igpj","igpj"),
    ("igpj_txt_listado","igpj_txt_listado"), ("igpj_listado_nuevo","igpj_listado_nuevo"),
    ("maternidad","maternidad"), ("escribania","escribania"),
]

def get_total_registros(db):
    total = 0
    for nombre, schema in SCHEMAS:
        count = db.execute(
            text(f'SELECT COUNT(*) FROM "{schema}"."Datcorr_database"')
        ).scalar() or 0
        total += count
    return total
```

```sql
SELECT COUNT(*) FROM public.usuarios WHERE activo = true;   -- activos
SELECT COUNT(*) FROM public.usuarios;                        -- total
```

Respuesta:
```json
{ "total_registros": 123456, "usuarios_activos": 25, "total_usuarios": 30, "alertas_pendientes": 3 }
```

### 2. GET /reportes/actividad-usuarios

```sql
SELECT usuario, COUNT(*) as operaciones
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY usuario
ORDER BY operaciones DESC
LIMIT :limite OFFSET :offset
```

Parametros: `desde`, `hasta` (YYYY-MM-DD), `limite` (default 10, max 100 via `Query(ge=1, le=100)`), `pagina` (default 1).

### 3. GET /reportes/evolucion-diaria

```sql
SELECT DATE(fecha) as dia, COUNT(*) as operaciones
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY dia ORDER BY dia
```

### 4. GET /reportes/tipos-operacion

```sql
SELECT accion, COUNT(*) as cantidad
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY accion ORDER BY cantidad DESC
```

### 5. GET /reportes/usuarios-inactivos

Solo `es_admin`. Excluye usuarios con actividad reciente. Usa `LEFT JOIN` eficiente (evita subconsulta correlacionada O(N×M)).

```python
if not es_admin:
    raise HTTPException(403, "Sin permisos para ver usuarios inactivos.")

from datetime import datetime, timedelta
fecha_limite = datetime.utcnow() - timedelta(days=dias)
```

```sql
SELECT u.usuario, u.nombre, u.rol, MAX(a.fecha) AS ultimo_acceso
FROM public.usuarios u
LEFT JOIN public.auditoria a ON a.usuario = u.usuario
WHERE u.activo = true
GROUP BY u.usuario, u.nombre, u.rol
HAVING MAX(a.fecha) IS NULL OR MAX(a.fecha) < :fecha_limite
ORDER BY ultimo_acceso ASC NULLS FIRST
```

### 6. GET /reportes/actividad-bases

```python
# SCHEMAS definido localmente (sin acoplamiento a database_router)
for nombre, schema in SCHEMAS:
    count = db.execute(text(f'SELECT COUNT(*) FROM "{schema}"."Datcorr_database"')).scalar() or 0
    resultados.append({"base": nombre, "schema": schema, "registros": count})
```

### 7. GET /reportes/alertas

Solo `es_admin`. Umbrales configurables via query params:

| Parametro | Default | FastAPI validation |
|-----------|---------|-------------------|
| `min_borrados` | 50 | `Query(ge=1)` |
| `min_intentos_fallidos` | 5 | `Query(ge=1)` |
| `ventana_horas` | 24 | `Query(ge=1, le=720)` |

```python
fecha_limite = datetime.utcnow() - timedelta(hours=ventana_horas)
```

```sql
-- Regla 1: Borrados masivos
SELECT usuario, COUNT(*) as borrados
FROM public.auditoria
WHERE accion IN ('DELETE', 'DELETE_LOGICO') AND fecha >= :fecha_limite
GROUP BY usuario HAVING COUNT(*) > :min_borrados

-- Regla 2: Login fallidos
SELECT usuario, COUNT(*) as intentos_fallidos
FROM public.auditoria
WHERE accion = 'LOGIN_FAILED' AND fecha >= :fecha_limite
GROUP BY usuario HAVING COUNT(*) >= :min_intentos_fallidos
```

Logging por severidad:
```python
import logging
logger = logging.getLogger(__name__)

if severidad == "alta":
    logger.warning(f"Alerta alta: {detalle}")
elif severidad == "media":
    logger.info(f"Alerta media: {detalle}")
else:
    logger.debug(f"Alerta baja: {detalle}")
```

> Usuarios inactivos no se duplica aqui. El frontend unifica `/alertas` + `/usuarios-inactivos`.

### 8. GET /reportes/exportar?tipo=...&formato=csv

```python
TIPOS_EXPORTABLES = {
    "actividad-usuarios": get_actividad_usuarios,
    "evolucion-diaria": get_evolucion_diaria,
    "tipos-operacion": get_tipos_operacion,
    "usuarios-inactivos": get_usuarios_inactivos,
    "actividad-bases": get_actividad_bases,
    "alertas": get_alertas,
}
```

Validacion estricta:
```python
if tipo not in TIPOS_EXPORTABLES:
    validos = ", ".join(TIPOS_EXPORTABLES.keys())
    raise HTTPException(400, f"Tipo '{tipo}' no valido. OPCIONES: {validos}")
```

Generacion CSV con manejo de errores:
```python
import csv, io
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
```

Flujo:
1. Frontend envia `GET /reportes/exportar?tipo=actividad-usuarios&desde=2026-01-01&hasta=2026-07-01`
2. Backend valida `tipo` contra `TIPOS_EXPORTABLES`
3. Llama a la funcion del servicio correspondiente con los filtros
4. Convierte resultado a CSV
5. **Registra en auditoria** con `accion = "REPORTE_EXPORT"`, usuario, tipo de reporte, filtros, timestamp
6. Devuelve `StreamingResponse` con `Content-Disposition: attachment`

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
export const getAlertas = async (params = {}) =>
    api.get("/reportes/alertas", { params });
export const exportarReporte = async (tipo, formato = "csv", filtros = {}) =>
    api.get("/reportes/exportar", { params: { tipo, formato, ...filtros }, responseType: "blob" });
```

### Pagina: `frontend/src/pages/ReportesPage.jsx`

```javascript
const [fechaDesde, setFechaDesde] = useState(
    new Date(new Date().getTime() - 30 * 24 * 60 * 60 * 1000)
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

### Selector de fechas (timezone local)

```javascript
<input
    type="date"
    value={fechaDesde.toLocaleDateString("en-CA")}
    onChange={(e) => setFechaDesde(new Date(e.target.value + "T12:00:00"))}
/>
```

> `.toLocaleDateString("en-CA")` genera YYYY-MM-DD en timezone local (no UTC).
> `new Date(e.target.value + "T12:00:00")` evita desfasaje por huso horario.

### Componente de tabs: `frontend/src/components/ReportesTabs.jsx`

- **Resumen**: KPIs en Cards MUI + DataGrid `actividad-usuarios`
- **Actividad**: Grafico de linea `recharts` (evolucion diaria) + DataGrid detalle
- **Operaciones**: Grafico de barras `recharts` (distribucion por tipo) + DataGrid
- **Bases**: DataGrid actividad por base documental
- **Alertas**: Lista de alertas agrupadas por severidad con iconos MUI

## Manejo de errores y casos borde

| Escenario | Respuesta | Detalle |
|-----------|-----------|---------|
| Token invalido/expirado | `401` | Lo maneja `JWTMiddleware` |
| Sin permisos | `403` | `if not es_admin: raise HTTPException(403)` |
| Fecha mal formateada | `400` | `parse_fecha()` atrapa `ValueError` |
| `desde` > `hasta` | `400` | Comparar objetos datetime, no strings |
| Rango > 365 dias | `400` | `if (hasta - desde).days > 365` |
| `limite` > 100 | `400` | `Query(ge=1, le=100)` |
| `pagina` < 1 | `400` | `Query(ge=1)` |
| `dias` invalido | `400` | `Query(ge=1, le=365)` |
| `tipo` inexistente en exportar | `400` | Listar tipos validos en mensaje |
| Schema no existe | `200` | Retornar 0 sin error |
| BD caida / timeout | `503` | Log interno, mensaje generico |
| Sin datos en rango | `200` | Array vacio `[]`, no error |
| Error generando CSV | `500` | `try/except` con `logger.error()` |
| Error inesperado en endpoint | `500` | `try/except` con mensaje generico |

### Validaciones via FastAPI Query

```python
dias: int = Query(default=30, ge=1, le=365, description="Dias para verificar inactividad")
limite: int = Query(default=10, ge=1, le=100, description="Maximo de resultados")
pagina: int = Query(default=1, ge=1, description="Numero de pagina")
min_borrados: int = Query(default=50, ge=1, description="Umbral de DELETE para alerta")
ventana_horas: int = Query(default=24, ge=1, le=720, description="Ventana en horas")
```

### Patron try/except en todos los endpoints

```python
@router.get("/kpis")
def kpis(usuario_actual=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        es_admin = usuario_actual.es_superusuario or usuario_actual.nivel_seguridad >= 10
        # logica del endpoint
        return resultado
    except HTTPException:
        raise  # dejar pasar las HTTPException controladas
    except Exception as e:
        logger.error(f"Error en kpis usuario={usuario_actual.usuario}: {e}")
        raise HTTPException(500, "Error interno del servidor. Intente nuevamente.")
```

## Mejores practicas

1. **Paginacion server-side** como en DatabasePage.
2. **Fechas**: enviar como YYYY-MM-DD en timezone local. Frontend usa `.toLocaleDateString("en-CA")`. Backend parsea con `datetime.strptime()`.
3. **Permisos**: filtrar SIEMPRE en backend. Frontend solo oculta visualmente.
4. **Cache**: `@lru_cache` con `usuario_id` en la key. `Cache-Control: private` en respuestas HTTP.
5. **Exportacion**: CSV con `csv` stdlib + `StreamingResponse`. Auditoria obligatoria.
6. **Graficos**: `recharts` instalado via npm.
7. **Rendimiento**: indices en `public.auditoria` (fecha, usuario, accion). LEFT JOIN en lugar de subconsultas correlacionadas.
8. **Roles**: backend filtra datos; frontend adapta UI.
9. **Alertas**: umbrales configurables como query parameters. Logging por nivel de severidad.
10. **Auditoria de reportes (OBLIGATORIO)**: cada exportacion registra en `public.auditoria` con `accion = "REPORTE_EXPORT"`, usuario, tipo, filtros, timestamp.
11. **Schema whitelist**: validar contra `SCHEMAS` definido localmente. Nunca usar valores del usuario directamente en SQL.
12. **try/except en todos los endpoints**: capturar `Exception`, loguear, devolver `500` generico.

## Resumen de archivos a crear/modificar

| Archivo | Accion |
|---------|--------|
| `backend/services/reportes_service.py` | Crear (SCHEMAS, alertas, cache, parse_fecha, todas las queries) |
| `backend/routers/reportes_router.py` | Crear (8 endpoints con try/except, Depends, validaciones Query) |
| `backend/main.py` | Agregar `app.include_router(reportes_router)` |
| `frontend/src/services/reportesService.js` | Crear (8 funciones) |
| `frontend/src/pages/ReportesPage.jsx` | Crear (pagina con tabs, date inputs nativos) |
| `frontend/src/components/ReportesTabs.jsx` | Crear (tabs con DataGrids + recharts) |
| `frontend/src/router/AppRouter.jsx` | Reemplazar placeholder por `<ReportesPage />` |
| `frontend/src/layouts/Sidebar.jsx` | Agregar permiso `canViewUsers` al item Reportes |

## Orden de implementacion

1. Ejecutar scripts SQL de indices PostgreSQL.
2. Backend: `reportes_service.py` (SCHEMAS, funciones de query, parse_fecha, cache, alertas).
3. Backend: `reportes_router.py` (8 endpoints con try/except, validaciones, Depends).
4. Registrar router en `main.py`.
5. Instalar `recharts` en frontend.
6. Frontend: `reportesService.js`.
7. Frontend: `ReportesTabs.jsx`.
8. Frontend: `ReportesPage.jsx`.
9. Frontend: exportacion CSV con descarga.
10. Frontend: restringir permiso en Sidebar.
11. Testing de roles: verificar que un USUARIO no ve datos de otros.
12. Testing de casos borde: fechas invertidas, rango > 365d, limite > 100, schema invalido, timeout.
13. Documentacion para usuarios.

## Postergado (no MVP)
- Exportacion PDF (`reportlab` o `xhtml2pdf`).
- Dashboard configurable por usuario.
- Drill-down desde graficos a detalle.
- Comparativa interanual.
- Reportes programados por email.

---

### Fortalezas incorporadas desde plan_ejemplo.py

| Feature | Ubicacion en v3.0 |
|---------|-------------------|
| Validacion `(hasta - desde).days > 365` | Manejo de errores + patron Query |
| `@lru_cache` con `usuario_id` en key | Seccion Backend > Cache |
| Schema whitelist (`if schema not in SCHEMAS`) | Schema definido localmente |
| `try/except` con mensaje generico + `logger.error` | Patron en todos los endpoints |
| Logging por severidad (warning/info/debug) | Endpoint /alertas |
| `Query(ge=1, le=100)` en parametros | Validaciones FastAPI Query |
| CSV con `try/except` y logging | Endpoint /exportar |
| `parse_fecha()` con validacion de formato | Funcion helper |
| Documentacion clara de reglas de alerta | Endpoint /alertas + docstring sugerido |
