
📄 PLAN DE REPORTES ACTUALIZADO - DATCORR ERP
Plan de Reportes - DatCorr ERP (v2.0 - Mejorado)
Estado actual
✅ La ruta /reportes existe en el sidebar pero muestra solo un placeholder
✅ No hay componente de página, ni servicio, ni endpoints de backend
✅ Todos los usuarios ven el item en el menu (sin restriccion de permisos)
Datos disponibles para reportes
Fuente	Descripción
7 bases documentales (IPS, PEDIATRICO, IGPJ, etc.)	Tablas Datcorr_database con miles de registros cada una
public.usuarios	Usuarios del sistema con rol, nivel, activo/inactivo
public.auditoria	Traza completa de todas las operaciones (login, CRUD, consultas, busquedas)
public.refresh_tokens	Sesiones activas de usuarios
permisos / usuarios_permisos	Permisos asignados por usuario
🎯 Objetivo
Crear un Dashboard Inteligente de Reportes que:

Ofrezca insights en tiempo real
Sea configurable por rol
Permita exportación rápida
Detecte anomalías automáticamente
Arquitectura propuesta
text

frontend/src/services/reportesService.js  →  backend/routers/reportes_router.py  →  PostgreSQL
                        ↕                            ↕
frontend/src/pages/DashboardPage.jsx     backend/services/reportes_service.py
Backend
Crear backend/routers/reportes_router.py con prefix /reportes y los siguientes endpoints:

1. GET /reportes/kpis
   KPIs principales: Total registros, usuarios activos, alertas, crecimiento
   SELECT COUNT(*) FROM public.auditoria WHERE fecha BETWEEN :desde AND :hasta
   SELECT COUNT(*) FROM public.usuarios WHERE activo = true
2. GET /reportes/actividad-usuarios
   Top N usuarios mas activos (mas operaciones en auditoria en un rango de fechas)
   SELECT usuario, COUNT(*) as operaciones FROM public.auditoria WHERE fecha BETWEEN :desde AND :hasta GROUP BY usuario ORDER BY operaciones DESC LIMIT :limite
3. GET /reportes/evolucion-diaria
   Cantidad de operaciones por dia en un rango (para grafico de linea)
   SELECT DATE(fecha) as dia, COUNT(*) FROM public.auditoria WHERE fecha BETWEEN :desde AND :hasta GROUP BY dia ORDER BY dia
4. GET /reportes/tipos-operacion
   Distribucion de acciones (CREATE, UPDATE, DELETE, LOGIN, etc.) en un rango
   SELECT accion, COUNT(*) FROM public.auditoria WHERE fecha BETWEEN :desde AND :hasta GROUP BY accion ORDER BY COUNT(*) DESC
5. GET /reportes/usuarios-inactivos
   Usuarios sin actividad en los ultimos N dias
   Subquery: usuarios que no aparecen en auditoria en el periodo
6. GET /reportes/actividad-bases
   Porcentaje de crecimiento por base documental vs mes anterior
   SELECT schema, COUNT(*), DATE_TRUNC('month', ...) FROM ... GROUP BY schema
7. GET /reportes/exportar?formato=csv
   Exportar datos de una consulta en CSV o JSON para descarga
8. GET /reportes/exportar?formato=pdf
   Exportar reporte completo en PDF con gráficos y KPIs
   Permisos
   Todos los endpoints de reportes deben requerir nivel_seguridad >= 5 o es_superusuario
   Usar Depends(requiere_nivel(5))
   Filtros por rol en frontend:
   ADMIN: Todo
   AUDITOR: Seguridad + auditoría
   GERENTE: KPIs + bases críticas
   USUARIO: Solo su actividad
   Frontend
   Componentes sugeridos (MUI)
   Componente	Uso
   Card / Paper	KPIs y contenedores de cada widget
   DataGrid	Tablas con datos paginados (reutilizar patron de DatabasePage)
   LineChart / BarChart de @mui/x-charts	Graficos de evolucion diaria y distribucion
   DatePicker de @mui/x-date-pickers	Selector de rango de fechas
   Select / MenuItem	Filtro por base, usuario, accion
   Button	Exportar a CSV/PDF
   Grid	Layout de widgets (no tabs)
   Layout sugerido (WIDGETS)
   text

┌─────────────────────────────────────────────────────────────┐
│  Reportes Dashboard                                         │
│  [Desde: ██] [Hasta: ██] [Filtrar por Rol] [Exportar PDF]  │
├──────────────────┬───────────────────────────────────────────┤
│  KPI 1: Total     │  KPI 2: Usuarios Activos                 │
│  Registros: 1.2k │  Usuarios Activos: 456                   │
├──────────────────┴───────────────────────────────────────────┤
│  Widget: Gráfico de Evolución (Linea)                        │
│  Widget: Top Usuarios Activos (Bar)                          │
├─────────────────────────────────────────────────────────────┤
│  Widget: Alertas (Lista)                                     │
│  Widget: Usuarios Inactivos (Lista)                          │
└─────────────────────────────────────────────────────────────┘
Pagina sugerida: frontend/src/pages/DashboardPage.jsx
Estado local:

js

const [fechaDesde, setFechaDesde] = useState(subDays(new Date(), 30));
const [fechaHasta, setFechaHasta] = useState(new Date());
const [filtroRol, setFiltroRol] = useState('ADMIN');
const [loading, setLoading] = useState(false);
const [kpis, setKpis] = useState(null);
const [actividad, setActividad] = useState([]);
const [evolucion, setEvolucion] = useState([]);
const [usuariosInactivos, setUsuariosInactivos] = useState([]);
const [alertas, setAlertas] = useState([]);
Servicio frontend
Crear frontend/src/services/reportesService.js:

js

import api from "../api/axiosClient";

// KPIs principales
export const getKpis = async () => api.get("/reportes/kpis");

// Actividad por usuario
export const getActividadUsuarios = async (desde, hasta, limite = 10) =>
    api.get("/reportes/actividad-usuarios", { params: { desde, hasta, limite } });

// Evolución diaria
export const getEvolucionDiaria = async (desde, hasta) =>
    api.get("/reportes/evolucion-diaria", { params: { desde, hasta } });

// Tipos de operación
export const getTiposOperacion = async (desde, hasta) =>
    api.get("/reportes/tipos-operacion", { params: { desde, hasta } });

// Usuarios inactivos
export const getUsuariosInactivos = async (dias) =>
    api.get("/reportes/usuarios-inactivos", { params: { dias } });

// Alertas del sistema
export const getAlertas = async () => api.get("/reportes/alertas");

// Exportación
export const exportarReporte = async (formato = "csv") =>
    api.get("/reportes/exportar", { params: { formato }, responseType: "blob" });
Mejores practicas a seguir
Paginación server-side como en DatabasePage (no cargar todo en memoria)
Fechas: enviar como ISO strings (YYYY-MM-DD), parsear con date-fns o dayjs en frontend
Permisos: proteger cada endpoint con Depends(requiere_nivel(5)) (backend) y canViewUsers (frontend)
Cache: respuestas de reportes pueden cachearse 30-60 segundos si los datos no cambian frecuentemente
Exportación: generar CSV en backend con csv.writer o pandas, devolver StreamingResponse con media type text/csv; PDF con reportlab
Gráficos: usar @mui/x-charts (ya disponible como dependencia del ecosistema MUI) o recharts para visualizaciones
Rendimiento: las consultas sobre public.auditoria deben usar indice en fecha; las consultas sobre schemas documentales deben usar indice en id_Datcorr_database
Roles: filtrar widgets según rol del usuario en frontend
Alertas: detectar anomalías automáticamente y mostrar en dashboard
Posibles mejoras futuras
Reportes programados via cron/scheduler (enviar por email)
Dashboard de reportes con widgets configurables por usuario
Drill-down: hacer clic en un grafico para ir al detalle
Comparativa interanual (mismo mes del ano anterior)
Validación de calidad de datos
Logs de auditoría de reportes
Resumen de archivos a crear/modificar
Archivo	Acción
backend/routers/reportes_router.py	Crear (8 endpoints)
backend/services/reportes_service.py	Crear (logica de consultas + alertas)
backend/main.py	Agregar app.include_router(reportes_router)
frontend/src/services/reportesService.js	Crear (8 funciones)
frontend/src/pages/DashboardPage.jsx	Crear (pagina completa con widgets)
frontend/src/router/AppRouter.jsx	Reemplazar placeholder por 
frontend/src/layouts/Sidebar.jsx	Agregar permiso canViewUsers al item Reportes
frontend/src/components/DashboardWidgets.jsx	Crear (componente reutilizable de widgets)
Orden sugerido de implementación
Backend: servicio + router (consultas SQL + endpoints + alertas)
Registrar router en main.py
Frontend: servicio (reportesService.js)
Frontend: componentes de widgets
Frontend: pagina (DashboardPage.jsx) con Grid de widgets
Frontend: agregar graficos con @mui/x-charts
Frontend: exportación CSV/PDF
Frontend: restringir permiso en Sidebar
Testing + validación de roles
Documentación + training para usuarios
Nota: Este plan v2.0 elimina los tabs en favor de widgets, agrega alertas proactivas, exportación PDF, y permite personalización por rol. Es más flexible, escalable y profesional.
