# Plan de Reportes - DatCorr ERP
# v2.3 - Consolidado y corregido

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

Antes de implementar, asegurar estos indices para evitar queries lentos sobre `public.auditoria`:

```sql
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON public.auditoria (fecha);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario_fecha ON public.auditoria (usuario, fecha);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion_fecha ON public.auditoria (accion, fecha);
```

## Dependencias nuevas requeridas

```bash
# Frontend: graficos ligeros y compatibles con MUI v9
cd frontend
npm install recharts

# Backend: solo si se implementa exportacion PDF
# pip install reportlab
```

> Nota: NO se instalan `@mui/x-charts`, `@mui/x-date-pickers`, `date-fns` ni `dayjs`.
> Los graficos se resuelven con `recharts`. Los selectores de fecha usan `<input type="date">` nativo
> (HTML5) para eliminar dependencias adicionales.
> Para fecha inicial por defecto: restar 30 dias a la fecha local del usuario.
> En el frontend se usa: `new Date(new Date().getTime() - 30 * 24 * 60 * 60 * 1000)` y al enviar al backend
> se transforma con: `fecha.toLocaleDateString("en-CA")` que devuelve `YYYY-MM-DD` en timezone local,
> evitando el desfasaje UTC que produce `.toISOString().split('T')[0]`.

## Arquitectura
```
frontend/src/services/reportesService.js  →  backend/routers/reportes_router.py  →  PostgreSQL
                        ↕                            ↕
frontend/src/pages/ReportesPage.jsx     backend/services/reportes_service.py
```

## Backend

Crear `backend/routers/reportes_router.py` con prefix `/reportes`.

Todos los endpoints usan `Depends(obtener_usuario_actual)` (no `request.state.user`) para mantener
consistencia con el resto del proyecto. El usuario autenticado se recibe como parametro de la funcion.

### Reglas de filtrado por rol (backend)

Cada endpoint aplica estas reglas internamente:

| Rol del usuario | Datos que ve |
|----------------|--------------|
| `es_superusuario` o `nivel_seguridad >= 10` | Todos los datos de todos los usuarios |
| cualquier otro | Solo su propia actividad (`WHERE usuario = :usuario_actual`) |

### 1. GET /reportes/kpis

Cuatro indicadores principales. `total_registros` se calcula con una consulta por schema (mas eficiente que UNION ALL):

```python
# SCHEMAS definido localmente en reportes_service.py (no depende de database_router)
SCHEMAS = [
    ("ips", "ips"),
    ("pediatrico", "pediatrico"),
    ("igpj", "igpj"),
    ("igpj_txt_listado", "igpj_txt_listado"),
    ("igpj_listado_nuevo", "igpj_listado_nuevo"),
    ("maternidad", "maternidad"),
    ("escribania", "escribania"),
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
-- KPI: Usuarios activos
SELECT COUNT(*) FROM public.usuarios WHERE activo = true
```

```sql
-- KPI: Total usuarios registrados
SELECT COUNT(*) FROM public.usuarios
```

```sql
-- KPI: Alertas pendientes (ver endpoint /alertas)
-- Se calcula en backend segun reglas definidas abajo
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

Top N usuarios mas activos en un rango de fechas. Con paginacion y filtro por rol.

```sql
SELECT usuario, COUNT(*) as operaciones
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY usuario
ORDER BY operaciones DESC
LIMIT :limite OFFSET :offset
```

Parametros: `desde`, `hasta` (ISO date), `limite` (default 10, max 100), `pagina` (default 1).

### 3. GET /reportes/evolucion-diaria

Cantidad de operaciones por dia en un rango. Para grafico de linea.

```sql
SELECT DATE(fecha) as dia, COUNT(*) as operaciones
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY dia
ORDER BY dia
```

### 4. GET /reportes/tipos-operacion

Distribucion de acciones (CREATE, UPDATE, DELETE, LOGIN, etc.).

```sql
SELECT accion, COUNT(*) as cantidad
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY accion
ORDER BY cantidad DESC
```

### 5. GET /reportes/usuarios-inactivos

Usuarios sin actividad en los ultimos N dias. El campo `ultimo_acceso` se calcula desde `public.auditoria`
ya que la tabla `usuarios` no tiene ese campo.

**Riesgo de seguridad**: este endpoint expone nombres y roles de usuarios. Solo usuarios con
`es_superusuario` o `nivel_seguridad >= 10` pueden acceder. Cualquier otro recibe 403.

```python
# Backend: validar permiso antes de ejecutar query
if not es_admin:
    raise HTTPException(status_code=403, detail="Sin permisos para ver usuarios inactivos.")

# Calcular la fecha limite en Python (evita interpolacion SQL)
from datetime import datetime, timedelta
fecha_limite = datetime.utcnow() - timedelta(days=dias)
```

```sql
-- LEFT JOIN + GROUP BY: evita la subconsulta correlacionada O(N×M)
-- que ejecutaria un SELECT por cada usuario.
SELECT u.usuario, u.nombre, u.rol,
       MAX(a.fecha) AS ultimo_acceso
FROM public.usuarios u
LEFT JOIN public.auditoria a ON a.usuario = u.usuario
WHERE u.activo = true
GROUP BY u.usuario, u.nombre, u.rol
HAVING MAX(a.fecha) IS NULL
    OR MAX(a.fecha) < :fecha_limite   -- parametro datetime desde Python
ORDER BY ultimo_acceso ASC NULLS FIRST
```

### 6. GET /reportes/actividad-bases

Cantidad de registros por base documental.

```python
# SCHEMAS se define localmente en reportes_service.py (no importa desde database_router)
# para evitar acoplamiento entre modulos.
#
# SCHEMAS = [("ips","ips"), ("pediatrico","pediatrico"), ...]
#
# Se itera y se ejecuta:
#   SELECT COUNT(*) FROM "{schema}"."Datcorr_database"
# Retorna array de { base: nombre, schema: schema, registros: count }
```

### 7. GET /reportes/alertas

Alertas proactivas del sistema. Solo visible para `es_superusuario` o `nivel_seguridad >= 10`.

Los umbrales se reciben como query parameters opcionales con valores por defecto,
evitando valores hardcoded y permitiendo ajuste sin cambiar codigo:

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `min_borrados` | 50 | Minimo de DELETE/DELETE_LOGICO en 24h para alertar |
| `min_intentos_fallidos` | 5 | Minimo de LOGIN_FAILED en 24h para alertar |
| `ventana_horas` | 24 | Ventana de tiempo en horas para las reglas |

```python
# Calcular la ventana en Python y pasar como parametro timestamp
from datetime import datetime, timedelta
fecha_limite = datetime.utcnow() - timedelta(hours=ventana_horas)
```

```sql
-- Regla 1: Borrados masivos recientes
-- ATENCION: validar los valores exactos de accion contra la BD real.
-- Ejecutar: SELECT DISTINCT accion FROM public.auditoria para conocer los valores reales.
SELECT usuario, COUNT(*) as borrados
FROM public.auditoria
WHERE accion IN ('DELETE', 'DELETE_LOGICO')
  AND fecha >= :fecha_limite   -- parametro datetime desde Python
GROUP BY usuario
HAVING COUNT(*) > :min_borrados
```

```sql
-- Regla 2: Intentos de login fallidos (solo si LOGIN_FAILED existe en la BD)
-- Verificar con: SELECT DISTINCT accion FROM public.auditoria WHERE accion LIKE '%LOGIN%'
SELECT usuario, COUNT(*) as intentos_fallidos
FROM public.auditoria
WHERE accion = 'LOGIN_FAILED'
  AND fecha >= :fecha_limite   -- parametro datetime desde Python
GROUP BY usuario
HAVING COUNT(*) >= :min_intentos_fallidos
```

> Nota: La deteccion de usuarios inactivos NO se duplica aqui. Usar el endpoint `/reportes/usuarios-inactivos`
> que ya implementa esa logica. Si se necesita en alertas, el frontend puede llamar a ambos endpoints y
> unificarlos en la UI.

Backend clasifica las alertas por severidad (baja/media/alta) y devuelve un array estructurado:

```json
[
    {
        "tipo": "borrados_masivos",
        "severidad": "alta",
        "usuario": "jperez",
        "valor": 57,
        "detalle": "57 operaciones DELETE en 24 horas"
    }
]
```

### 8. GET /reportes/exportar?tipo=actividad-usuarios&formato=csv

Exportar datos en CSV usando `csv` (stdlib) + `StreamingResponse`.
Requiere un parametro `tipo` que indica que reporte exportar (los mismos nombres de los endpoints),
mas los filtros correspondientes (`desde`, `hasta`, `limite`, etc.).

Flujo:
1. Frontend envia `GET /reportes/exportar?tipo=actividad-usuarios&desde=2026-01-01&hasta=2026-07-01`
2. Backend llama internamente a la misma funcion del servicio que genera los datos
3. Convierte el resultado a CSV con `csv.DictWriter`
4. Devuelve `StreamingResponse` con `Content-Disposition: attachment`

```python
import csv, io
from fastapi.responses import StreamingResponse

TIPOS_EXPORTABLES = {
    "actividad-usuarios": get_actividad_usuarios,
    "evolucion-diaria": get_evolucion_diaria,
    "tipos-operacion": get_tipos_operacion,
    "usuarios-inactivos": get_usuarios_inactivos,
    "actividad-bases": get_actividad_bases,
    "alertas": get_alertas,
}

def generar_csv(datos: list[dict], nombre_archivo: str):
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
```

Parametros: `tipo` (requerido, valores en `TIPOS_EXPORTABLES`), `formato` (default "csv"),
mas los filtros de cada tipo (`desde`, `hasta`, `limite`, `dias`, etc.).

> Nota: No requiere dependencias adicionales (csv es stdlib).
> PDF: Posponer para una iteracion posterior. Evaluar `reportlab` o `xhtml2pdf`.

## Permisos y seguridad (backend)

Todos los endpoints usan `Depends(obtener_usuario_actual)` y filtran datos segun el rol:

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
    # ... logica segura ...
```

Reglas:
- **SUPERUSUARIO / nivel >= 10**: acceso total a todos los datos.
- **RESTO**: solo sus propias metricas. Queries con `AND (:es_admin = true OR usuario = :usuario_actual)`.

Todas las queries con ventanas de tiempo (`NOW() - INTERVAL`) deben calcular el timestamp
en Python con `datetime.utcnow() - timedelta(...)` y pasarlo como parametro `:fecha_limite`,
evitando interpolacion de strings SQL en el servidor.

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
export const exportarReporte = async (tipo, formato = "csv", filtros = {}) =>
    api.get("/reportes/exportar", { params: { tipo, formato, ...filtros }, responseType: "blob" });
export const getActividadBases = async () => api.get("/reportes/actividad-bases");
export const getAlertas = async () => api.get("/reportes/alertas");
```

### Pagina: `frontend/src/pages/ReportesPage.jsx`

Layout por tabs, compatible con el disenio del dashboard existente.

Estado local:
```javascript
const [fechaDesde, setFechaDesde] = useState(
    new Date(new Date().getTime() - 30 * 24 * 60 * 60 * 1000)  // 30 dias atras, hora local
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
- **Actividad**: Grafico de linea `recharts` (evolucion diaria) + DataGrid detalle
- **Operaciones**: Grafico de barras `recharts` (distribucion por tipo) + DataGrid
- **Bases**: DataGrid actividad por base documental
- **Alertas**: Lista de alertas agrupadas por severidad con iconos MUI

### Selector de fechas

```javascript
// .toLocaleDateString("en-CA") genera YYYY-MM-DD en timezone local
// NO usar .toISOString().split('T')[0] porque devuelve fecha UTC
// que puede diferir un dia de la fecha local del usuario.

<input
    type="date"
    value={fechaDesde.toLocaleDateString("en-CA")}
    onChange={(e) => setFechaDesde(new Date(e.target.value + "T12:00:00"))}
/>
```

> `new Date(e.target.value + "T12:00:00")` evita que el parser de JavaScript interprete la fecha
> como UTC y la desfase un dia en husos horarios negativos. Al fijar mediodia, se garantiza
> que la fecha local se conserve correctamente.

Sin dependencias de date-pickers.

## Manejo de errores y casos borde

Cada endpoint debe manejar estos escenarios:

| Escenario | Respuesta esperada |
|-----------|--------------------|
| Token invalido/expirado | `401 Unauthorized` (lo maneja `JWTMiddleware`) |
| Usuario sin permisos (`nivel < 10` y no superuser) | `403 Forbidden` con detalle claro |
| `desde` > `hasta` (fechas invertidas) | `400 Bad Request` - Swappear fechas o rechazar |
| Rango de fechas > 1 anio | `400 Bad Request` - Limitar a 365 dias |
| `limite` > 100 | Cap a 100 sin error (o devolver 400) |
| `pagina` < 1 | Default a 1 |
| Schema documental no existe (actividad-bases) | Retornar 0 en lugar de error |
| `tipo` invalido en `/exportar` | `400 Bad Request` - Listar tipos validos en mensaje |
| BD caida / timeout | `503 Service Unavailable` + log interno |
| Sin datos en el rango | Array vacio `[]`, no error |
| `dias` <= 0 en usuarios-inactivos | Default a 30 |

Patron sugerido para validacion de parametros:

```python
from fastapi import HTTPException, Query

@router.get("/ejemplo")
def ejemplo(
    desde: str = Query(...),
    hasta: str = Query(...),
    limite: int = Query(10, ge=1, le=100),
    pagina: int = Query(1, ge=1),
):
    if desde > hasta:
        raise HTTPException(400, "La fecha 'desde' no puede ser posterior a 'hasta'.")
```

## Mejores practicas

1. **Paginacion server-side** como en DatabasePage.
2. **Fechas**: enviar como strings ISO en timezone local (`YYYY-MM-DD`). El frontend debe usar `.toLocaleDateString("en-CA")` en lugar de `.toISOString().split('T')[0]` para evitar desfasaje UTC. El backend recibe la fecha como string y puede parsearla con `datetime.strptime()` sin timezone.
3. **Permisos**: filtrar SIEMPRE en backend. El frontend solo oculta visualmente.
4. **Cache**: si se implementa, usar `Cache-Control: private` para evitar que un usuario reciba datos cacheados de otro. No cachear por URL sola; incluir `usuario_id` en la key si se usa cache interno.
5. **Exportacion**: CSV con `csv` stdlib + `StreamingResponse`.
6. **Graficos**: usar `recharts` (instalado via npm).
7. **Rendimiento**: consultas sobre `public.auditoria` usan los indices definidos en el pre-requisito.
8. **Roles**: el backend expone solo los datos permitidos; el frontend adapta la UI.
9. **Indices por schema**: `CREATE INDEX IF NOT EXISTS ON "schema"."Datcorr_database" ("id_Datcorr_database")` si no existe.
10. **Auditoria de reportes (OBLIGATORIO)**: cada exportacion CSV debe registrar en `public.auditoria` con accion `REPORTE_EXPORT`, incluyendo usuario, tipo de reporte, filtros aplicados, y timestamp. Esto es parte del flujo del endpoint `/exportar` y se ejecuta automaticamente despues de generar el CSV.

## Resumen de archivos a crear/modificar

| Archivo | Accion |
|---------|--------|
| `backend/routers/reportes_router.py` | Crear (8 endpoints con `Depends`) |
| `backend/services/reportes_service.py` | Crear (logica de consultas + alertas) |
| `backend/main.py` | Agregar `app.include_router(reportes_router)` |
| `frontend/src/services/reportesService.js` | Crear (8 funciones) |
| `frontend/src/pages/ReportesPage.jsx` | Crear (pagina completa con tabs) |
| `frontend/src/components/ReportesTabs.jsx` | Crear (componente reutilizable de tabs) |
| `frontend/src/router/AppRouter.jsx` | Reemplazar placeholder por `<ReportesPage />` |
| `frontend/src/layouts/Sidebar.jsx` | Agregar permiso adecuado al item Reportes |

## Orden sugerido de implementacion

1. Ejecutar scripts SQL de indices PostgreSQL.
2. Backend: servicio + router (consultas SQL + endpoints + alertas + filtrado por rol).
3. Registrar router en `main.py`.
4. Instalar `recharts` en frontend.
5. Frontend: servicio (`reportesService.js`).
6. Frontend: componente `ReportesTabs.jsx`.
7. Frontend: pagina `ReportesPage.jsx` con tabs y widgets.
8. Frontend: exportacion CSV.
9. Frontend: restringir permiso en Sidebar.
10. Testing + validacion de roles (probar que un USUARIO no ve datos de otros).
11. Testing de casos borde: fechas invertidas, rangos largos, schemas vacios, timeout simulado.
12. Documentacion para usuarios.

## Postergado (no MVP)
- Exportacion PDF (definir `reportlab` o `xhtml2pdf` e instalar).
- Dashboard configurable por usuario.
- Drill-down desde graficos a detalle.
- Comparativa interanual.
- Reportes programados por email.
