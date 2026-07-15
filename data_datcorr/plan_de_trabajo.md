# Plan de Trabajo — Interfaz Web (Hibridación)

## Objetivo

Replicar en la web las funcionalidades actuales de la aplicación de escritorio (PySide6),
manteniendo el backend FastAPI existente y el frontend React + Vite + MUI.

---

## FASE 0 — Diagnóstico inicial ✅

- [x] Login web funcional (JWT + refresh token)
- [x] CRUD de usuarios (listar, crear, editar, desactivar)
- [x] Sidebar con navegación básica
- [x] Dashboard placeholder
- [x] Backend conectado a PostgreSQL

---

## LIMPIEZA SQLITE ✅

Eliminado todo el código legacy de SQLite del proyecto:

| Archivos eliminados | Motivo |
|---|---|
| `migration/` (directorio completo) | Migración SQLite→PostgreSQL ya completada |
| `model/datcorr_dao_*.py` (6 archivos) | DAOs que solo funcionaban con SQLite |
| `ui/plantilla_*.py` (6 archivos) | Plantillas Qt que cargaban desde SQLite |
| `ui/plantilla_*.ui` (6 archivos) | Layouts Qt Designer de las plantillas |
| `ui/labels_png_rc.py`, `ui/base_*.png` | Recursos de las plantillas Qt |
| `controller/selector_bases.py` | Diálogo de selección de bases SQLite |
| `controller/cargador_plantillas.py` | Cargador de plantillas Qt |
| `migrate_*.py` (7 archivos) | Scripts de migración SQLite→PostgreSQL |
| `inventario_bases.py` | Inventario de bases SQLite |
| `verificar_tabla.py` | Script legacy |
| `utils.py`, `utils/rutas.py` | Funciones de ruta a `bases_g/` |
| `IPS.db`, `bases_g/` | Base SQLite y directorio |

| Archivos modificados | Cambio |
|---|---|
| `backend/services/database_service_web.py` | Eliminadas todas las funciones SQLite (quedó solo PostgreSQL) |
| `db/engines.py` | Eliminada `get_sqlite_engine()` |
| `db/registry.py` | Eliminado `set_sqlite()`, siempre usa PostgreSQL |
| `ventana_principal.py` | Eliminado `sqlite3`, SQLite en búsqueda, edición y carga de bases |
| `core/database_router.py` | `is_sqlite()` eliminado |
| `core/data_service.py` | `_fetch_sqlite()` eliminado |

---

## FASE 1 — Backend: API de consulta a bases de datos ✅

- [x] `backend/schemas/database_schema.py` — modelos Pydantic
- [x] `backend/services/database_service_web.py` — lógica para listar, consultar, buscar y actualizar (PostgreSQL + SQLite)
- [x] `backend/routers/database_router.py` — endpoints REST:
  - `GET /databases/` — lista de bases disponibles
  - `GET /databases/{base}/tables` — tablas de una base
  - `GET /databases/{base}/search?q=...` — búsqueda global
  - `GET /databases/{base}/data` — consulta completa
  - `PATCH /databases/{base}/records/{id}` — editar registro
- [x] Registrado en `backend/main.py`

---

## FASE 2 — Frontend: Página de consulta de bases ✅

- [x] `frontend/src/services/databaseService.js` — funciones API
- [x] `frontend/src/pages/DatabasePage.jsx` con:
  - Selector de base (dropdown)
  - Campo de búsqueda + botones
  - Grilla de resultados (MUI DataGrid) con paginación
  - Tabs por consulta (modo CONSULTA / BUSQUEDA)
  - Doble click para editar registro
- [x] Ruta `/database` en `AppRouter.jsx`
- [x] Ítem "Consultar Bases" en `Sidebar.jsx`

---

## FASE 3 — Frontend: Modal de edición de registros ✅

- [x] `frontend/src/components/modals/EditRecordModal.jsx` — Drawer con campos dinámicos
- [x] Guardar cambios vía API (`PATCH /databases/{base}/records/{id}`)
- [x] Refrescar grilla después de editar

---

## FASE 4 — Frontend: Carga de datos desde plantillas ✅

- [x] `POST /databases/{base}/records` — endpoint para insertar registros
- [x] `GET /databases/{base}/columns` — endpoint para obtener columnas editables
- [x] `frontend/src/pages/CargaDatosPage.jsx` — formulario dinámico generado desde las columnas de la base
- [x] Ruta `/carga-datos` en `AppRouter.jsx`
- [x] Ítem "Carga de Datos" en `Sidebar.jsx`

---

## FASE 5 — Frontend: Launcher de aplicaciones externas

- [ ] Menú de acceso rápido a aplicaciones externas (.exe/.lnk)
- [ ] Favoritos y recientes

---

## FASE 6 — Cierre de sesión y sesión expirada ✅

- [x] Botón "Cerrar sesión" en Sidebar (con llamada a `/auth/logout`)
- [x] Limpieza de tokens y redirect a login

---

> **Leyenda:** ✅ completado | [ ] pendiente | 🔄 en progreso
