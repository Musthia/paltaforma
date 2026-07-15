# Plan de Reportes - DatCorr ERP

## Estado actual

- La ruta `/reportes` existe en el sidebar pero muestra solo un placeholder
- No hay componente de página, ni servicio, ni endpoints de backend
- Todos los usuarios ven el item en el menu (sin restriccion de permisos)

## Datos disponibles para reportes

| Fuente | Descripcion |
|--------|-------------|
| 7 bases documentales (IPS, PEDIATRICO, IGPJ, IGPJ_TXT_LISTADO, IGPJ_LISTADO_NUEVO, MATERNIDAD, ESCRIBANIA) | Tablas `Datcorr_database` con miles de registros cada una |
| `public.usuarios` | Usuarios del sistema con rol, nivel, activo/inactivo |
| `public.auditoria` | Traza completa de todas las operaciones (login, CRUD, consultas, busquedas) con fecha, usuario, accion, detalle, IP |
| `public.refresh_tokens` | Sesiones activas de usuarios |
| `permisos` / `usuarios_permisos` | Permisos asignados por usuario |

## Arquitectura propuesta

```
frontend/src/services/reportesService.js  →  backend/routers/reportes_router.py  →  PostgreSQL
                        ↕                            ↕
frontend/src/pages/ReportesPage.jsx     backend/services/reportes_service.py
```

### Backend

Crear `backend/routers/reportes_router.py` con prefix `/reportes` y los siguientes endpoints:

#### 1. GET /reportes/resumen-bases
- Count de registros por base, con variacion respecto al mes anterior
- `SELECT schema, COUNT(*), DATE_TRUNC('month', ...) FROM ... GROUP BY schema`

#### 2. GET /reportes/actividad-usuarios
- Top N usuarios mas activos (mas operaciones en auditoria en un rango de fechas)
- `SELECT usuario, COUNT(*) as operaciones FROM public.auditoria WHERE fecha BETWEEN :desde AND :hasta GROUP BY usuario ORDER BY operaciones DESC LIMIT :limite`

#### 3. GET /reportes/evolucion-diaria
- Cantidad de operaciones por dia en un rango (para grafico de linea)
- `SELECT DATE(fecha) as dia, COUNT(*) FROM public.auditoria WHERE fecha BETWEEN :desde AND :hasta GROUP BY dia ORDER BY dia`

#### 4. GET /reportes/tipos-operacion
- Distribucion de acciones (CREATE, UPDATE, DELETE, LOGIN, etc.) en un rango
- `SELECT accion, COUNT(*) FROM public.auditoria WHERE fecha BETWEEN :desde AND :hasta GROUP BY accion ORDER BY COUNT(*) DESC`

#### 5. GET /reportes/usuarios-inactivos
- Usuarios sin actividad en los ultimos N dias
- Subquery: usuarios que no aparecen en auditoria en el periodo

#### 6. GET /reportes/exportar?formato=csv
- Exportar datos de una consulta en CSV o JSON para descarga

### Permisos
- Todos los endpoints de reportes deben requerir `nivel_seguridad >= 5` o `es_superusuario`
- Usar `Depends(requiere_nivel(5))`

### Frontend

#### Componentes sugeridos (MUI)

| Componente | Uso |
|------------|-----|
| `Card` / `Paper` | KPIs y contenedores de cada reporte |
| `DataGrid` | Tablas con datos paginados (reutilizar patron de DatabasePage) |
| `LineChart` / `BarChart` de `@mui/x-charts` | Graficos de evolucion diaria y distribucion |
| `DatePicker` de `@mui/x-date-pickers` | Selector de rango de fechas |
| `Select` / `MenuItem` | Filtro por base, usuario, accion |
| `Button` | Exportar a CSV |
| `Tabs` | Alternar entre distintos reportes (Dashboard de reportes) |

#### Layout sugerido

```
┌─────────────────────────────────────────────────┐
│  Reportes                                        │
│  [Desde: ██] [Hasta: ██] [Filtrar] [Exportar]   │
├──────────────────┬──────────────────────────────┤
│  Tarjeta KPI 1   │  Tarjeta KPI 2               │
│  Total registros  │  Usuarios activos            │
├──────────────────┴──────────────────────────────┤
│  Tabs: [Resumen] [Actividad] [Usuarios] [Bases] │
├─────────────────────────────────────────────────┤
│  Tab content (DataGrid / grafico)               │
│                                                  │
└─────────────────────────────────────────────────┘
```

#### Pagina sugerida: `frontend/src/pages/ReportesPage.jsx`

Estado local:
```js
const [fechaDesde, setFechaDesde] = useState(subDays(new Date(), 30));
const [fechaHasta, setFechaHasta] = useState(new Date());
const [tabIndex, setTabIndex] = useState(0);
const [loading, setLoading] = useState(false);
const [resumen, setResumen] = useState(null);
const [actividad, setActividad] = useState([]);
const [evolucion, setEvolucion] = useState([]);
```

### Servicio frontend

Crear `frontend/src/services/reportesService.js`:

```js
import api from "../api/axiosClient";

export const getResumenBases = async () => api.get("/reportes/resumen-bases");
export const getActividadUsuarios = async (desde, hasta, limite = 10) =>
    api.get("/reportes/actividad-usuarios", { params: { desde, hasta, limite } });
export const getEvolucionDiaria = async (desde, hasta) =>
    api.get("/reportes/evolucion-diaria", { params: { desde, hasta } });
export const getTiposOperacion = async (desde, hasta) =>
    api.get("/reportes/tipos-operacion", { params: { desde, hasta } });
export const exportarReporte = async (formato = "csv") =>
    api.get("/reportes/exportar", { params: { formato }, responseType: "blob" });
```

### Mejores practicas a seguir

1. **Paginacion server-side** como en DatabasePage (no cargar todo en memoria)
2. **Fechas**: enviar como ISO strings (`YYYY-MM-DD`), parsear con `date-fns` o `dayjs` en frontend
3. **Permisos**: proteger cada endpoint con `Depends(requiere_nivel(5))` (backend) y `canViewUsers` (frontend)
4. **Cache**: respuestas de reportes pueden cachearse 30-60 segundos si los datos no cambian frecuentemente
5. **Exportacion**: generar CSV en backend con `csv.writer` o `pandas`, devolver `StreamingResponse` con media type `text/csv`
6. **Graficos**: usar `@mui/x-charts` (ya disponible como dependencia del ecosistema MUI) o `recharts` para visualizaciones
7. **Rendimiento**: las consultas sobre `public.auditoria` deben usar indice en `fecha`; las consultas sobre schemas documentales deben usar indice en `id_Datcorr_database`

### Posibles mejoras futuras

- Reportes programados via cron/scheduler (enviar por email)
- Dashboard de reportes con widgets configurables por usuario
- Drill-down: hacer clic en un grafico para ir al detalle
- Comparativa interanual (mismo mes del ano anterior)

## Resumen de archivos a crear/modificar

| Archivo | Accion |
|---------|--------|
| `backend/routers/reportes_router.py` | Crear (6 endpoints) |
| `backend/services/reportes_service.py` | Crear (logica de consultas) |
| `backend/main.py` | Agregar `app.include_router(reportes_router)` |
| `frontend/src/services/reportesService.js` | Crear (5 funciones) |
| `frontend/src/pages/ReportesPage.jsx` | Crear (pagina completa) |
| `frontend/src/router/AppRouter.jsx` | Reemplazar placeholder por `<ReportesPage />` |
| `frontend/src/layouts/Sidebar.jsx` | Agregar permiso `canViewUsers` al item Reportes |

## Orden sugerido de implementacion

1. Backend: servicio + router (consultas SQL + endpoints)
2. Registrar router en `main.py`
3. Frontend: servicio (`reportesService.js`)
4. Frontend: pagina (`ReportesPage.jsx`) con DataGrids
5. Frontend: agregar graficos con `@mui/x-charts`
6. Frontend: exportacion CSV
7. Frontend: restringir permiso en Sidebar
