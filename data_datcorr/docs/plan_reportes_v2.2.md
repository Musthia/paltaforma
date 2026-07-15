# Plan de Reportes - DatCorr ERP
# v2.2 - Ejecutable y corregido

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

Instalar antes de avanzar con el frontend:

```bash
# Frontend: graficos ligeros y compatibles con MUI v9
cd frontend
npm install recharts

# Backend: solo si se implementa exportacion PDF
# pip install reportlab
```

> Nota: NO se instalan `@mui/x-charts`, `@mui/x-date-pickers`, `date-fns` ni `dayjs`.
> Los graficos se resolucion con `recharts`. Los selectores de fecha usan `<input type="date">` nativo
> (HTML5) para eliminar dependencias adicionales.

## Arquitectura
```
frontend/src/services/reportesService.js  →  backend/routers/reportes_router.py  →  PostgreSQL
                        ↕                            ↕
frontend/src/pages/ReportesPage.jsx     backend/services/reportes_service.py
```

## Backend

Crear `backend/routers/reportes_router.py` con prefix `/reportes`.

### 1. GET /reportes/kpis
KPIs principales. **"Total registros" debe venir de bases documentales, no de auditoría**.

```sql
-- KPI: Total registros en bases documentales
SELECT 'total_registros', COUNT(*) FROM (
    SELECT COUNT(*) FROM ips.Datcorr_database
    UNION ALL SELECT COUNT(*) FROM pediatrico.Datcorr_database
    UNION ALL SELECT COUNT(*) FROM igpj.Datcorr_database
    UNION ALL SELECT COUNT(*) FROM igpj_txt_listado.Datcorr_database
    UNION ALL SELECT COUNT(*) FROM igpj_listado_nuevo.Datcorr_database
    UNION ALL SELECT COUNT(*) FROM maternidad.Datcorr_database
    UNION ALL SELECT COUNT(*) FROM escribania.Datcorr_database
) AS t

-- KPI: Usuarios activos
SELECT COUNT(*) FROM public.usuarios WHERE activo = true

-- KPI: Alertas pendientes (calcularse en backend segun reglas)
-- Ver seccion de alertas
```

### 2. GET /reportes/actividad-usuarios
Top N usuarios más activos. **Backend debe filtrar por rol del usuario autenticado**.

```sql
SELECT usuario, COUNT(*) as operaciones
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY usuario
ORDER BY operaciones DESC
LIMIT :limite
```

Regla de filtrado backend:
- `es_superusuario` o `nivel_seguridad >= 10`: ve todos los usuarios.
- resto: solo ve su propia actividad.

### 3. GET /reportes/evolucion-diaria
Cantidad de operaciones por día en un rango.

```sql
SELECT DATE(fecha) as dia, COUNT(*) as operaciones
FROM public.auditoria
WHERE fecha BETWEEN :desde AND :hasta
  AND (:es_admin = true OR usuario = :usuario_actual)
GROUP BY dia
ORDER BY dia
```

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
Usuarios sin actividad en los últimos N días.

```sql
SELECT u.usuario, u.nombre, u.rol, u.ultimo_acceso
FROM public.usuarios u
WHERE u.activo = true
  AND u.usuario NOT IN (
      SELECT DISTINCT usuario
      FROM public.auditoria
      WHERE fecha >= NOW() - INTERVAL ':dias days'
  )
ORDER BY u.ultimo_acceso ASC NULLS FIRST
```

### 6. GET /reportes/actividad-bases
Cantidad de registros y variación vs. mes anterior por base documental.

```sql
-- Mes actual
SELECT schema, COUNT(*) as registros
FROM (
    SELECT 'ips' as schema, id_Datcorr_database FROM ips.Datcorr_database
    UNION ALL SELECT 'pediatrico', id_Datcorr_database FROM pediatrico.Datcorr_database
    UNION ALL SELECT 'igpj', id_Datcorr_database FROM igpj.Datcorr_database
    UNION ALL SELECT 'igpj_txt_listado', id_Datcorr_database FROM igpj_txt_listado.Datcorr_database
    UNION ALL SELECT 'igpj_listado_nuevo', id_Datcorr_database FROM igpj_listado_nuevo.Datcorr_database
    UNION ALL SELECT 'maternidad', id_Datcorr_database FROM maternidad.Datcorr_database
    UNION ALL SELECT 'escribania', id_Datcorr_database FROM escribania.Datcorr_database
) AS bases
GROUP BY schema
ORDER BY registros DESC
```

### 7. GET /reportes/alertas
Alertas proactivas del sistema. Reglas sugeridas:

- Usuarios con más de 50 operaciones DELETE en las últimas 24 horas.
- Intentos de login fallidos recientes (si `auditoria.accion = 'LOGIN_ERROR'` existe).
- Sesiones abiertas de más de 12 horas (usar `public.refresh_tokens`).

```sql
-- Regla 1: Borrados masivos recientes
SELECT usuario, COUNT(*) as borrados, 'borrados_masivos' as alerta
FROM public.auditoria
WHERE accion = 'DELETE'
  AND fecha >= NOW() - INTERVAL '24 hours'
GROUP BY usuario
HAVING COUNT(*) > 50

-- Regla 2: Ultimo acceso muy antiguo (si aplica)
SELECT usuario, MAX(fecha) as ultimo_acceso, 'acceso_antiguo' as alerta
FROM public.auditoria
GROUP BY usuario
HAVING MAX(fecha) < NOW() - INTERVAL '30 days'
```

Backend clasifica las alertas por severidad (baja/media/alta) y devuelve un array estructurado.

### 8. GET /reportes/exportar?formato=csv
Exportar datos en CSV usando `csv` (stdlib) + `StreamingResponse`.

```python
def generar_csv(datos: list[dict], nombre_archivo: str):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=datos[0].keys())
    writer.writeheader()
    writer.writerows(datos)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"}
    )
```

> Nota: No requiere dependencias adicionales.

- **PDF**: Posponer para una iteración posterior. Si se requiere, evaluar `reportlab` o `xhtml2pdf` y agregar a `requirements.txt` explícitamente.

## Permisos y seguridad (backend)

Todos los endpoints requieren autenticación y:

```python
@router.get("/kpis")
def kpis(request: Request, ...):
    usuario = request.state.user
    # lógica de filtrado por rol dentro de cada endpoint
```

Reglas por rol backend:
- **ADMIN / SUPERUSUARIO**: acceso total a todos los datos.
- **AUDITOR / GERENTE**: KPIs agregados, evolución, tipos de operación. Sin detalle por usuario individual a menos que sea su propia actividad.
- **USUARIO**: solo sus propias métricas. Queries con `WHERE usuario = current_user`.

> Importante: El `JWTMiddleware` no bloquea peticiones sin token por sí solo.
> La seguridad depende de `Depends(obtener_usuario_actual)` o `requiere_nivel()` en cada endpoint.

## Frontend

### Servicio: `frontend/src/services/reportesService.js`

```javascript
import api from "../api/axiosClient";

export const getKpis = async () => api.get("/reportes/kpis");
export const getActividadUsuarios = async (desde, hasta, limite = 10) =>
    api.get("/reportes/actividad-usuarios", { params: { desde, hasta, limite } });
export const getEvolucionDiaria = async (desde, hasta) =>
    api.get("/reportes/evolucion-diaria", { params: { desde, hasta } });
export const getTiposOperacion = async (desde, hasta) =>
    api.get("/reportes/tipos-operacion", { params: { desde, hasta } });
export const getUsuariosInactivos = async (dias) =>
    api.get("/reportes/usuarios-inactivos", { params: { dias } });
export const getActividadBases = async () => api.get("/reportes/actividad-bases");
export const getAlertas = async () => api.get("/reportes/alertas");
export const exportarReporte = async (formato = "csv") =>
    api.get("/reportes/exportar", { params: { formato }, responseType: "blob" });
```

### Página: `frontend/src/pages/ReportesPage.jsx`

Layout por tabs, compatible con el diseño del dashboard existente.

Estado local:
```javascript
const [fechaDesde, setFechaDesde] = useState(subDays(new Date(), 30)); // subDays requiere dayjs/date-fns
const [fechaHasta, setFechaHasta] = useState(new Date());
const [tabIndex, setTabIndex] = useState(0);
const [loading, setLoading] = useState(false);
const [kpis, setKpis] = useState(null);
const [actividad, setActividad] = useState([]);
const [evolucion, setEvolucion] = useState([]);
const [usuariosInactivos, setUsuariosInactivos] = useState([]);
const [actividadBases, setActividadBases] = useState([]);
const [alertas, setAlertas] = useState([]);
```

> Nota sobre fechas: si `subDays` de `dayjs` no está disponible, reemplazar por `date-fns/subDays`
> o calcular manualmente: `new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)`.

### Componente de tabs: `frontend/src/components/ReportesTabs.jsx`
Encapsula los tabs y renderiza el contenido correspondiente a cada tab según el índice activo.

Dentro de cada tab:
- **Resumen**: KPIs en Cards + DataGrid con `getActividadUsuarios`.
- **Actividad**: Gráfico de línea con `recharts` (evolución diaria) + DataGrid detalle.
- **Usuarios**: DataGrid `usuarios-inactivos`.
- **Bases**: Gráfico de barra con `recharts` (actividad por base) + tabla.
- **Alertas**: Lista de alertas agrupadas por severidad con iconos de MUI.

### Selector de fechas
Usar inputs nativos HTML:
```javascript
<input
    type="date"
    value={fechaDesde.toISOString().split('T')[0]}
    onChange={(e) => setFechaDesde(new Date(e.target.value))}
/>
```

Sin dependencias de date-pickers.

## Mejores prácticas

1. **Paginación server-side** como en DatabasePage.
2. **Fechas**: enviar como ISO strings (`YYYY-MM-DD`). No requiere parseo complejo.
3. **Permisos**: filtrar SIEMPRE en backend. El frontend solo oculta visualmente.
4. **Cache**: respuestas pueden cachearse 30-60 segundos con headers `Cache-Control` en el router.
5. **Exportación**: CSV con `csv` stdlib + `StreamingResponse`.
6. **Gráficos**: usar `recharts` (instalado via npm).
7. **Rendimiento**: consultas sobre `public.auditoria` usan los índices definidos en el pre-requisito.
8. **Roles**: el backend expone solo los datos permitidos; el frontend adapta la UI (oculta tabs/widgets que no correspondan).

## Resumen de archivos a crear/modificar

| Archivo | Acción |
|---------|--------|
| `backend/routers/reportes_router.py` | Crear (8 endpoints) |
| `backend/services/reportes_service.py` | Crear (lógica de consultas + alertas) |
| `backend/main.py` | Agregar `app.include_router(reportes_router)` |
| `frontend/src/services/reportesService.js` | Crear (8 funciones) |
| `frontend/src/pages/ReportesPage.jsx` | Crear (página completa con tabs) |
| `frontend/src/components/ReportesTabs.jsx` | Crear (componente reutilizable de tabs) |
| `frontend/src/router/AppRouter.jsx` | Reemplazar placeholder por `<ReportesPage />` |
| `frontend/src/layouts/Sidebar.jsx` | Agregar permiso adecuado al item Reportes |

## Orden sugerido de implementación

1. Ejecutar scripts SQL de índices PostgreSQL.
2. Backend: servicio + router (consultas SQL + endpoints + alertas + filtrado por rol).
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
- Exportación PDF (definir `reportlab` o `xhtml2pdf` e instalar).
- Dashboard configurable por usuario.
- Drill-down desde gráficos a detalle.
- Comparativa interanual.
- Reportes programados por email.
- Logs de auditoría de reportes.
