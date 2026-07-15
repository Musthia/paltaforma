# Plan de Reportes — DatCorr ERP

# v4.0 — Definitivo (unificado, auditado, test-gated)

---

## 1. Análisis comparativo: v2.4 vs v3.0

### Fortalezas de v2.4 (incorporadas)

| Fortaleza                                         | ¿En v3.0?                   |
| ------------------------------------------------- | ---------------------------- |
| `exc_info=True` en logger.warning/error         | No — se agrega              |
| Cache incluye`es_admin` (multi-rol)             | No — se agrega              |
| `regex="^csv$"` valida formato estricto         | No — se agrega              |
| UNION ALL como alternativa a loops                | No — se agrega como opción |
| Advertencia sobre workers múltiples y lru_cache  | No — se agrega              |
| Detail del endpoint exportar más completo        | No — se agrega              |
| `logger.info` para severidad media (no warning) | Sí, equivalente             |
| Tabla clara de filtrado por rol                   | Sí                          |

### Fortalezas de v3.0 (incorporadas)

| Fortaleza                                                | ¿En v2.4?                                                  |
| -------------------------------------------------------- | ----------------------------------------------------------- |
| `toLocaleDateString("en-CA")` evita timezone bug       | No — v2.4 usa`toISOString()` que desplaza -1 día        |
| `new Date(e.target.value + "T12:00:00")` sin drift     | No — v2.4 usa`new Date(e.target.value)` que deriva a UTC |
| LEFT JOIN en usuarios-inactivos (evita O(N×M))          | No — v2.4 usa`NOT IN (SELECT DISTINCT ...)`              |
| Alertas en exportable types                              | No                                                          |
| Umbrales de alerta configurables por query param         | No                                                          |
| Re-lanza HTTPException, captura solo Exception genérica | No — v2.4 captura todo con generic handler                 |
| `Cache-Control: private` en respuestas                 | No                                                          |
| Auditoría obligatoria en exportación (paso explícito) | Mencionado pero sin detalle                                 |
| Tabla de casos borde completa (14 escenarios)            | No — solo 4                                                |
| SCHEMAS definido localmente sin acoplamiento             | No                                                          |

### Vulnerabilidades detectadas en ambos planes

| #   | Vulnerabilidad                                                      | Severidad          | Afecta proyecto actual                                     |
| --- | ------------------------------------------------------------------- | ------------------ | ---------------------------------------------------------- |
| V1  | `table` param sin validación contra whitelist (SQLi potencial)   | **CRÍTICA** | Sí —`database_router.py` y `database_service_web.py` |
| V2  | `LASTVAL()` no session-safe (race condition)                      | **CRÍTICA** | Sí —`database_service_web.py:155`                      |
| V3  | `database_router.py` expone `str(e)` en 6 endpoints (info leak) | **ALTA**     | Sí — líneas 102,131,148,172,194,213                     |
| V4  | `/dashboard/stats` sin `Depends()` (solo JWT global)            | **MEDIA**    | Sí —`dashboard_router.py:16`                           |
| V5  | Sin paginación en`/alertas` — DoS potencial                     | **MEDIA**    | Futuro                                                     |
| V6  | `lru_cache` sin TTL — datos obsoletos                            | **MEDIA**    | Futuro                                                     |
| V7  | Sin rate limiting en`/exportar` — abuso de descarga              | **MEDIA**    | Futuro                                                     |
| V8  | `auditoria` sin particionamiento/archivo — crecimiento infinito  | **BAJA**     | Sí                                                        |
| V9  | `nivel` vs `nivel_seguridad` — mezcla de nombres en planes     | **BAJA**     | Sí — el campo es`nivel_seguridad`                      |
| V10 | Planes no definen tests ejecutables — solo mención genérica      | **MEDIA**    | Ambos                                                      |

### VULNERABILIDADES PREEXISTENTES (proyecto actual, fuera de los planes)

> **Deben corregirse ANTES de implementar reportes, o al menos en paralelo.**

| #  | Archivo                     | Línea                  | Problema                                                                               | Severidad          |
| -- | --------------------------- | ----------------------- | -------------------------------------------------------------------------------------- | ------------------ |
| P1 | `database_service_web.py` | 52,55,89,94,113,137,151 | `f'...{tabla}...'` — tabla sin validar contra whitelist                             | **CRÍTICA** |
| P2 | `database_service_web.py` | 155                     | `SELECT LASTVAL()` no es session-safe; usar `RETURNING`                            | **CRÍTICA** |
| P3 | `database_router.py`      | 102,131,148,172,194,213 | `raise HTTPException(500, detail=str(e))` expone ruta, driver, etc.                  | **ALTA**     |
| P4 | `dashboard_router.py`     | 17                      | `dashboard_stats()` sin `Depends()`                                                | **MEDIA**    |
| P5 | `database_service_web.py` | 94                      | `f'...{id_col}...'` — id_col de information_schema, bajo riesgo pero mala práctica | **BAJA**     |
| P6 | `database_conexion.py`    | 45                      | `engine` sin `pool_size`/`max_overflow` — pool por defecto                      | **BAJA**     |

---

## 2. Plan unificado de Reportes — v4.0

### Datos disponibles

7 schemas documentales (`ips`, `pediatrico`, `igpj`, `igpj_txt_listado`, `igpj_listado_nuevo`, `maternidad`, `escribania`), tabla `Datcorr_database` en cada uno.
Tablas relacionales: `public.usuarios`, `public.auditoria`, `public.refresh_tokens`.

### Stack

- **Backend**: FastAPI + SQLAlchemy core (`text()`) + psycopg2
- **Frontend**: React + MUI v9 + recharts
- **Fechas**: `<input type="date">` nativo (sin date-pickers)
- **Exportación**: CSV con stdlib `csv` + `StreamingResponse`
- **Auth**: `Depends(obtener_usuario_actual)` en todos los endpoints

### Rol admin

```python
es_admin = usuario_actual.es_superusuario or usuario_actual.nivel_seguridad >= 10
```

### 8 Endpoints

| # | Endpoint                             | Admin ve           | User ve                | Paginación          |
| - | ------------------------------------ | ------------------ | ---------------------- | -------------------- |
| 1 | `GET /reportes/kpis`               | Todo               | Todo (es global)       | No                   |
| 2 | `GET /reportes/actividad-usuarios` | Todos los usuarios | Solo sí mismo         | Sí (limit+página)  |
| 3 | `GET /reportes/evolucion-diaria`   | Todos              | Solo sí mismo         | No                   |
| 4 | `GET /reportes/tipos-operacion`    | Todos              | Solo sí mismo         | No                   |
| 5 | `GET /reportes/usuarios-inactivos` | Solo admin         | 403                    | No                   |
| 6 | `GET /reportes/actividad-bases`    | Todo               | Todo (datos públicos) | No                   |
| 7 | `GET /reportes/alertas`            | Solo admin         | 403                    | Sí (limit)          |
| 8 | `GET /reportes/exportar`           | Según tipo        | Según tipo            | No (descarga única) |

### Validaciones comunes (FastAPI Query)

```python
desde: str = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$")
hasta: str = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$")
limite: int = Query(10, ge=1, le=100, description="Resultados por página")
pagina: int = Query(1, ge=1, description="Número de página")
dias: int = Query(30, ge=1, le=365, description="Ventana de inactividad")
```

### Parseo de fechas (helper)

```python
def parse_fecha(f: str) -> datetime:
    try:
        return datetime.strptime(f, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise HTTPException(400, "Formato inválido. Use YYYY-MM-DD.")
```

### Validación de rango (después de parsear)

```python
if fecha_desde > fecha_hasta:
    raise HTTPException(400, "'desde' no puede ser posterior a 'hasta'.")
if (fecha_hasta - fecha_desde).days > 365:
    raise HTTPException(400, "Rango máximo 365 días.")
```

### Cache (capa servicio)

```python
from functools import lru_cache

@lru_cache(maxsize=128, typed=True)
def get_kpis_cached(usuario_id: int, es_admin: bool):
    """Cache por (usuario_id, es_admin). TTL manejado en app."""
    return compute_kpis(usuario_id, es_admin)
```

> **Advertencia**: `lru_cache` es por proceso. Con gunicorn multi-worker cada worker tiene su propia cache. Para el MVP es aceptable. Para invalidación se puede exponer `cache_clear()` vía endpoint admin o usar Redis.

### Patrón try/except en todos los endpoints

```python
@router.get("/kpis")
def kpis(
    usuario_actual=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        es_admin = usuario_actual.es_superusuario or usuario_actual.nivel_seguridad >= 10
        return compute_kpis(db, es_admin)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en kpis usuario={usuario_actual.usuario}: {e}", exc_info=True)
        raise HTTPException(500, "Error interno del servidor.")
```

### Filtrado por rol (backend, no confiar en frontend)

```sql
WHERE (:es_admin = true OR auditoria.usuario = :usuario_actual)
```

### 1. GET /reportes/kpis

```python
def compute_kpis(db, es_admin):
    schemas = ["ips","pediatrico","igpj","igpj_txt_listado","igpj_listado_nuevo","maternidad","escribania"]
    total_registros = 0
    for s in schemas:
        cnt = db.execute(text(f'SELECT COUNT(*) FROM "{s}"."Datcorr_database"')).scalar() or 0
        total_registros += cnt
    activos = db.execute(text("SELECT COUNT(*) FROM public.usuarios WHERE activo = true")).scalar() or 0
    total_usuarios = db.execute(text("SELECT COUNT(*) FROM public.usuarios")).scalar() or 0
    # alertas_pendientes se calcula aquí (mismas reglas que /alertas pero count total)
    return {
        "total_registros": total_registros,
        "usuarios_activos": activos,
        "total_usuarios": total_usuarios,
        "alertas_pendientes": contar_alertas(db)  # función compartida
    }
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

```python
if not es_admin:
    raise HTTPException(403, "Sin permisos.")
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
schemas = {"ips":"IPS","pediatrico":"PEDIATRICO","igpj":"IGPJ","igpj_txt_listado":"IGPJ TXT LISTADO",
           "igpj_listado_nuevo":"IGPJ_LISTADO_NUEVO","maternidad":"MATERNIDAD","escribania":"ESCRIBANIA"}
resultados = []
for s, nombre in schemas.items():
    cnt = db.execute(text(f'SELECT COUNT(*) FROM "{s}"."Datcorr_database"')).scalar() or 0
    resultados.append({"base": nombre, "schema": s, "registros": cnt})
return resultados
```

### 7. GET /reportes/alertas

Solo admin. Parámetros configurables:

- `min_borrados: int = Query(50, ge=1)` — umbral DELETE
- `min_login_fallidos: int = Query(5, ge=1)` — umbral LOGIN_FAILED
- `ventana_horas: int = Query(24, ge=1, le=720)` — ventana de tiempo

Con paginación: `limite: int = Query(20, ge=1, le=200)`.

```sql
-- Borrados masivos (severidad: alta)
SELECT usuario, COUNT(*) as cantidad
FROM public.auditoria
WHERE accion IN ('DELETE','DELETE_LOGICO') AND fecha >= NOW() - :ventana::interval
GROUP BY usuario HAVING COUNT(*) > :min_borrados

-- Login fallidos (severidad: alta)
SELECT usuario, COUNT(*) as cantidad
FROM public.auditoria
WHERE accion = 'LOGIN_FAILED' AND fecha >= NOW() - :ventana::interval
GROUP BY usuario HAVING COUNT(*) >= :min_login_fallidos
```

Logging por severidad:

```python
if severidad == "alta":
    logger.warning(f"ALERTA [alta] {detalle}")
elif severidad == "media":
    logger.info(f"ALERTA [media] {detalle}")
else:
    logger.debug(f"ALERTA [baja] {detalle}")
```

### 8. GET /reportes/exportar

```python
TIPOS_EXPORTABLES = {
    "actividad-usuarios": obtener_actividad_usuarios,
    "evolucion-diaria": obtener_evolucion_diaria,
    "tipos-operacion": obtener_tipos_operacion,
    "usuarios-inactivos": obtener_usuarios_inactivos,
    "actividad-bases": obtener_actividad_bases,
    "alertas": obtener_alertas,
}
```

Validaciones:

```python
if tipo not in TIPOS_EXPORTABLES:
    raise HTTPException(400, f"Tipo no válido. Opciones: {', '.join(TIPOS_EXPORTABLES.keys())}")

if formato != "csv":
    raise HTTPException(400, "Formato no soportado. Use 'csv'.")
```

Generación CSV:

```python
def generar_csv(datos, nombre_archivo):
    try:
        if not datos:
            return StreamingResponse(io.StringIO(""), media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={nombre_archivo}.csv"})
        output = io.StringIO()
        w = csv.DictWriter(output, fieldnames=datos[0].keys())
        w.writeheader(); w.writerows(datos); output.seek(0)
        return StreamingResponse(output, media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={nombre_archivo}.csv"})
    except Exception as e:
        logger.error(f"Error generando CSV: {e}", exc_info=True)
        raise HTTPException(500, "Error al generar el archivo CSV")
```

**Registro obligatorio en auditoría** (cada exportación):

```python
registrar_auditoria(db=db, usuario=usuario_actual.usuario, accion="REPORTE_EXPORT",
    tabla="reportes", detalle=f"Exportó {tipo} en formato {formato} [{desde} → {hasta}]")
```

### Frontend: servicio (`frontend/src/services/reportesService.js`)

```javascript
import api from "../api/axiosClient";
export const getKpis = () => api.get("/reportes/kpis");
export const getActividadUsuarios = (desde, hasta, limite, pagina) =>
    api.get("/reportes/actividad-usuarios", { params: { desde, hasta, limite, pagina } });
export const getEvolucionDiaria = (desde, hasta) =>
    api.get("/reportes/evolucion-diaria", { params: { desde, hasta } });
export const getTiposOperacion = (desde, hasta) =>
    api.get("/reportes/tipos-operacion", { params: { desde, hasta } });
export const getUsuariosInactivos = (dias) =>
    api.get("/reportes/usuarios-inactivos", { params: { dias } });
export const getActividadBases = () => api.get("/reportes/actividad-bases");
export const getAlertas = (params) => api.get("/reportes/alertas", { params });
export const exportarReporte = (tipo, formato, filtros) =>
    api.get("/reportes/exportar", { params: { tipo, formato, ...filtros }, responseType: "blob" });
```

### Frontend: fechas (timezone local — CORREGIDO)

```javascript
// ✅ Correcto (v3.0): timezone local
<input
    type="date"
    value={fechaDesde.toLocaleDateString("en-CA")}
    onChange={(e) => setFechaDesde(new Date(e.target.value + "T12:00:00"))}
/>

// ❌ Incorrecto (v2.4): desplaza -1 día
// value={fechaDesde.toISOString().split('T')[0]}  ← NO USAR
```

### Frontend: pages y componentes

- `frontend/src/pages/ReportesPage.jsx` — layout con tabs, date inputs, estado global
- `frontend/src/components/ReportesTabs.jsx` — 5 tabs: Resumen (cards KPIs), Actividad (recharts Line), Operaciones (recharts Bar), Bases (DataGrid), Alertas (lista agrupada por severidad)
- `frontend/src/router/AppRouter.jsx` — reemplazar placeholder por `<ReportesPage />`
- `frontend/src/layouts/Sidebar.jsx` — agregar `canViewReportes: isAdmin` en usePermissions; ocultar item si no tiene permiso

---

## 3. Checklist de implementación (test-gated)

> **Regla**: cada paso debe pasar su test ANTES de comenzar el siguiente.
> Si un paso falla, se detiene y se corrige antes de continuar.

### Fase 0 — CORRECCIÓN DE VULNERABILIDADES PREEXISTENTES

(No bloquear reportes, pero ejecutar en paralelo antes del paso 4)

- [ ] **P1**: Agregar `_validar_tabla(tabla)` en `database_service_web.py` con whitelist `["Datcorr_database"]`
- [ ] **P1 test**: Enviar `?table=Datcorr_database;DROP+TABLE+public.usuarios` → 400, no ejecución
- [ ] **P2**: Reemplazar `LASTVAL()` por `RETURNING id_Datcorr_database` en `insertar_registro`
- [ ] **P2 test**: Insertar registro, verificar que devuelve ID correcto sin race condition
- [ ] **P3**: Reemplazar `str(e)` por `"Error interno del servidor"` en database_router.py
- [ ] **P3 test**: Forzar error interno → respuesta 500 sin detalles del sistema
- [ ] **P4**: Agregar `Depends(obtener_usuario_actual)` a `dashboard_stats()` (o al menos verificar que JWT middleware lo cubre)

### Fase 1 — SQL + BACKEND (día 1)

- [ ] **1.1**: Ejecutar índices PostgreSQL

  ```sql
  CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON public.auditoria (fecha);
  CREATE INDEX IF NOT EXISTS idx_auditoria_usuario_fecha ON public.auditoria (usuario, fecha);
  CREATE INDEX IF NOT EXISTS idx_auditoria_accion_fecha ON public.auditoria (accion, fecha);
  ```
- [ ] **1.1 test**: `EXPLAIN ANALYZE SELECT ... WHERE fecha BETWEEN ... AND ...` verifica seq scan → index scan
- [ ] **1.2**: Crear `backend/services/reportes_service.py`

  - [ ] Constantes: `SCHEMAS`, `TIPOS_EXPORTABLES`
  - [ ] Helpers: `parse_fecha()`, `generar_csv()`
  - [ ] Funciones: `compute_kpis()`, `get_actividad_usuarios()`, `get_evolucion_diaria()`, `get_tipos_operacion()`, `get_usuarios_inactivos()`, `get_actividad_bases()`, `get_alertas()`, `contar_alertas()`
  - [ ] Cache: `@lru_cache` en funciones pesadas con `(usuario_id, es_admin)` como key
- [ ] **1.2 test**: Importar módulo desde shell Python y probar `parse_fecha("2026-07-01")` → datetime; `parse_fecha("mal")` → HTTPException(400)
- [ ] **1.3**: Crear `backend/routers/reportes_router.py`

  - [ ] 8 endpoints con `Depends(obtener_usuario_actual)`, `Depends(get_db)`
  - [ ] Patrón try/except en cada uno
  - [ ] Validaciones Query (ge, le, regex)
  - [ ] `/alertas` con paginación (limit)
  - [ ] `/exportar` con registro obligatorio en auditoría
  - [ ] `/usuarios-inactivos` y `/alertas` con check `es_admin`
- [ ] **1.3 test**: `curl -H "Authorization: Bearer $TOKEN" localhost:8000/reportes/kpis` → 200 con JSON
- [ ] **1.4**: Agregar `app.include_router(reportes_router)` en `backend/main.py`
- [ ] **1.4 test**: `curl localhost:8000/reportes/kpis` sin token → 401; con token admin → 200

### Fase 2 — FRONTEND (día 2)

- [ ] **2.1**: `npm install recharts`
- [ ] **2.1 test**: `import { LineChart } from "recharts"` no tira error
- [ ] **2.2**: Crear `frontend/src/services/reportesService.js` (8 funciones)
- [ ] **2.2 test**: Consola del navegador: `const {getKpis} = await import('./services/reportesService'); await getKpis()` → 200
- [ ] **2.3**: Crear `frontend/src/components/ReportesTabs.jsx`

  - [ ] Tab Resumen: 4 Cards MUI (total_registros, usuarios_activos, total_usuarios, alertas_pendientes) + DataGrid actividad-usuarios
  - [ ] Tab Actividad: recharts `<LineChart>` evolución diaria + DataGrid paginado
  - [ ] Tab Operaciones: recharts `<BarChart>` distribución + DataGrid
  - [ ] Tab Bases: DataGrid actividad-bases
  - [ ] Tab Alertas: Lista agrupada por severidad con iconos (ErrorOutline=alta, WarningAmber=media, Info=baja)
- [ ] **2.3 test**: Renderizar componente con datos mock → sin errores en consola
- [ ] **2.4**: Crear `frontend/src/pages/ReportesPage.jsx`

  - [ ] State local con fechas (inicio: 30 días atrás), loading, datos
  - [ ] Date inputs nativos con `toLocaleDateString("en-CA")` + `"T12:00:00"`
  - [ ] Fetch en `useEffect` que cambia con fechas
  - [ ] Loading spinner MUI mientras carga
  - [ ] Manejo de error (Snackbar o alerta)
  - [ ] Botón exportar descarga CSV
- [ ] **2.4 test**: Navegar a `/reportes` → ver KPIs, cambiar fechas → recarga datos, exportar → descarga CSV
- [ ] **2.5**: Reemplazar placeholder en `AppRouter.jsx`
- [ ] **2.5 test**: Ruta `/reportes` renderiza ReportesPage, no placeholder

### Fase 3 — PERMISOS + SIDEBAR (día 2 tarde)

- [ ] **3.1**: Agregar `canViewReportes: isAdmin` en `usePermissions.js`
- [ ] **3.1 test**: console.log en Sidebar muestra `canViewReportes: true` para admin, `false` para user normal
- [ ] **3.2**: Sidebar filta item Reportes según `canViewReportes`
- [ ] **3.2 test**: User normal no ve "Reportes" en menú

### Fase 4 — TESTING INTEGRAL (día 3)

> **Cada prueba debe pasar antes de marcar el paso. Si falla, se corrige y se repite la prueba.**

- [ ] **4.1**: Prueba de roles (backend real)
  - [ ] Admin (superusuario=true): todos los endpoints 200, ve datos de todos
  - [ ] User nivel 10: igual que admin
  - [ ] User nivel 5: /kpis 200, /actividad-usuarios solo sus datos, /usuarios-inactivos 403, /alertas 403
  - [ ] Token inválido: 401
  - [ ] Usuario inactivo: 403
- [ ] **4.2**: Prueba de validaciones
  - [ ] `desde=2026-07-01&hasta=2026-06-01` → 400
  - [ ] `desde=2020-01-01&hasta=2026-07-01` (rango >365d) → 400
  - [ ] `limite=999` → 422 (FastAPI validation)
  - [ ] `tipo=inventado` en exportar → 400 con lista de válidos
  - [ ] `pagina=0` → 422
- [ ] **4.3**: Prueba de exportación
  - [ ] Exportar cada tipo de reporte → CSV descargable con headers correctos
  - [ ] CSV vacío para rango sin datos → archivo vacío, no error
  - [ ] Auditoría registra `REPORTE_EXPORT` con usuario, tipo, fecha
- [ ] **4.4**: Prueba de timezone
  - [ ] Usuario en UTC-3: fecha `2026-07-01` debe ser `2026-07-01` en backend, no `2026-06-30`
- [ ] **4.5**: Prueba de alertas
  - [ ] Ejecutar 6 DELETE seguidos → no alerta (umbral=50)
  - [ ] Ejecutar 60 DELETE seguidos → alerta "alta" aparece
- [ ] **4.6**: Prueba de rendimiento
  - [ ] `/kpis` responde en < 2s con 7 schemas
  - [ ] `/actividad-usuarios` sobre auditoria con 100k filas responde en < 5s
- [ ] **4.7**: Smoke test (integración)
  - [ ] Login → navegar a Reportes → ver KPIs → cambiar fechas → ver actividad → exportar CSV → descarga correcta
  - [ ] Login como user normal → Reportes no aparece en sidebar → acceso directo a /reportes → ve solo sus datos

---

## 4. Archivos a crear/modificar (resumen)

| Archivo                                      | Acción                     | Fase |
| -------------------------------------------- | --------------------------- | ---- |
| `backend/services/reportes_service.py`     | CREAR                       | 1.2  |
| `backend/routers/reportes_router.py`       | CREAR                       | 1.3  |
| `backend/main.py`                          | MODIFICAR (include_router)  | 1.4  |
| `frontend/src/services/reportesService.js` | CREAR                       | 2.2  |
| `frontend/src/components/ReportesTabs.jsx` | CREAR                       | 2.3  |
| `frontend/src/pages/ReportesPage.jsx`      | CREAR                       | 2.4  |
| `frontend/src/router/AppRouter.jsx`        | MODIFICAR (ruta)            | 2.5  |
| `frontend/src/auth/usePermissions.js`      | MODIFICAR (canViewReportes) | 3.1  |
| `frontend/src/layouts/Sidebar.jsx`         | MODIFICAR (filtrar item)    | 3.2  |

### Correcciones preexistentes (Fase 0)

| Archivo                                      | Cambio                                                       |
| -------------------------------------------- | ------------------------------------------------------------ |
| `backend/services/database_service_web.py` | Validar tabla contra whitelist + RETURNING en vez de LASTVAL |
| `backend/routers/database_router.py`       | No exponer`str(e)`                                         |
| `backend/routers/dashboard_router.py`      | Agregar`Depends()` a stats                                 |

---

## 5. Postergado (no MVP)

- Exportación PDF
- Dashboard configurable por usuario
- Drill-down desde gráficos
- Comparativa interanual
- Reportes programados por email
- Redis cache en vez de lru_cache
- Rate limiting en /exportar
- Particionamiento de auditoria por mes
