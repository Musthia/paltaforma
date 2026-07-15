# Revisión del Plan Maestro DATCORR — Análisis y Plan Rearmado

> Documento de contraste entre `docs/revision_plan_maestro.md` (revisión previa) y el
> estado **real verificado** del repositorio en `C:\data_datcorr`. Incluye fortalezas,
> vulnerabilidades, plan rearmado y un nuevo plan de ejecución.

---

## 1. Resumen ejecutivo

El Plan Maestro original (`Plan_Maestro_Arquitectura_DATCORR.md`) propone una arquitectura
`React + Qt → FastAPI → PostgreSQL` con el backend como **única fuente de verdad**.
La revisión previa (`revision_plan_maestro.md`) marcó 8 puntos. Tras revisar el código
real, la conclusión principal se mantiene y se agrava:

**El escritorio Qt bypasea el backend y accede a PostgreSQL directamente.**

Pero aparecen **tres hallazgos nuevos que la revisión previa no detectó o subestimó**:

1. **Existen DOS stacks de acceso a datos en paralelo** (raíz vs `backend/`), lo que
   fragmenta la lógica de negocio y duplica validaciones/auditoría.
2. **La capa `repositories/` de la raíz es código muerto** (no se importa en ningún lado).
3. **La migración SQLite NO está terminada** a pesar de lo afirmado en `plan_de_trabajo.md`:
   los archivos `migrate_*.py`, `migration/` y `bases_g/*.db` siguen presentes, y
   `core/database_router.py` aún conserva `is_sqlite()`.

La buena noticia: **la API FastAPI ya expone TODO el CRUD que el escritorio necesita**
(listar, tablas, data, búsqueda, columnas, crear, editar `PATCH`, eliminar `DELETE`) y un
router de reportes muy completo. Por tanto, el esfuerzo principal ya no es "crear endpoints"
sino **migrar el cliente desktop a consumir la API existente**.

---

## 2. Contraste punto por punto (estado verificado)

| # | Punto del Plan Maestro                    | Estado revisión previa | Estado**real verificado**                                                                                                                                                                                                                                        |
| - | ----------------------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Finalizar migración a PostgreSQL         | ✅ ~80%                 | ⚠️**Sobreestimado.** Auth OK, pero `migrate_*.py` (7), `migration/` (8) y `bases_g/*.db` (7) siguen en disco. `core/database_router.py:37` aún tiene `is_sqlite()`.                                                                                 |
| 2 | Repositories por esquema                  | ⚠️ Parcial            | ❌**Peor de lo dicho.** `repositories/` existe pero **no se importa en ningún módulo raíz** (código muerto). El routing real está en `db/router.py`.                                                                                              |
| 3 | Services con lógica de negocio           | ✅ Ok                   | ✅ Confirmado, pero**duplicado**: root `services/` + `backend/services/`. Riesgo de deriva de reglas.                                                                                                                                                        |
| 4 | API REST completa                         | ⚠️ Parcial            | ✅**Sobreestimado en negativo.** `backend/routers/database_router.py` ya tiene CRUD completo + `reportes_router.py` con 11 consultas y exportadores CSV/XLSX/PDF. La API sí cubre lo que el escritorio necesita.                                            |
| 5 | Migrar React a consumir API               | ✅ Ok                   | ✅ Confirmado.`frontend/src/services/*` (dashboard, database, reportes, usuarios) consumen la API.                                                                                                                                                                   |
| 6 | Migrar Qt a consumir API (sin BD directa) | ❌ Incumplido           | ❌**Confirmado y crítico.** `ventana_principal.py` importa `db.router.DatabaseRouter`, `db.service.DatabaseService`, `db.registry.db_registry` y **no usa `self.api` ni una sola vez**. Sólo `base_datcorr.py` usa `ApiClient` para login. |
| 7 | Centralizar reportes                      | ⚠️ Parcial            | ✅ Backend de reportes completo y expuesto. React lo consume (`ReportesPage.jsx`). Qt no.                                                                                                                                                                            |
| 8 | Implementar caché/offline                | ❌ No iniciado          | ❌ No iniciado. Aceptable como fase tardía.                                                                                                                                                                                                                           |

### Tabla de doble stack (hallazgo clave)

| Responsabilidad      | Stack del escritorio (raíz)                                    | Stack del backend (`backend/`)                           |
| -------------------- | --------------------------------------------------------------- | ---------------------------------------------------------- |
| Conexión DB         | `db/engines.py`, `db/registry.py`, `database/conexion.py` | `backend/database/conexion.py`                           |
| Acceso a datos       | `db/router.py` (`DatabaseRouter`)                           | `backend/services/database_service_web.py` + router      |
| Lógica de negocio   | `services/`, `core/data_service.py`                         | `backend/services/*`                                     |
| Validación/permisos | `core/access_control.py`, `core/seguridad.py`               | `backend/security/permissions.py`, `jwt_middleware.py` |
| Repositorios         | `repositories/` (***no usado***)                      | implícito en services                                     |
| Modelos ORM          | `database/modelos*.py`, `model/datcorr_dao_postgres.py`     | `backend/database/conexion.py` (SQLAlchemy)              |
| Auditoría           | manual en pantallas (`ventana_principal.py`)                  | `backend/services/auditoria_service.py` + routers        |

---

## 3. Fortalezas

- **Backend FastAPI maduro y bien organizado**: routers por dominio, middlewares JWT,
  manejo global de excepciones (`core/handlers.py`), esquemas Pydantic, y un módulo de
  reportes con consultas y exportadores CSV/XLSX/PDF listos.
- **API de datos ya completa**: el CRUD que el escritorio necesita ya existe en
  `database_router.py` con auditoría integrada por endpoint. No hay que "inventar" endpoints.
- **Frontend React funcional**: consume la API de forma centralizada en `services/`, con
  páginas de Dashboard, Database, CargaDatos, Reportes, Auditoria y Usuarios.
- **Autenticación unificada**: login vía API con JWT + refresh token ya usado por ambos clientes.
- **Principios documentados**: `arquitectura_hibrida_objetivo.md` define fronteras claras
  (el backend como fuente de verdad) que sirven de brújula para el rearme.
- **Datos ya normalizados en PostgreSQL**: los esquemas `ips`, `pediatrico`, `igpj`,
  `maternidad`, `escribania`, etc. ya viven en PG (vistos en `db/router.py:list_bases`).

---

## 4. Vulnerabilidades / Brechas

### V1 — CRÍTICA: Escritorio accede a BD directamente

`VentanaPrincipal` opera sobre `db.router.DatabaseRouter` / `db.service.DatabaseService`
contra PostgreSQL. Rompe "una sola fuente de datos" y "validaciones/auditoría únicas".
Cualquier regla de negocio o permiso nuevo debe implementarse **dos veces**.

### V2 — ALTA: Doble stack de lógica de negocio

Raíz (`services/`, `core/`, `db/`, `database/`, `model/`) y `backend/` duplican conexión,
validación y acceso a datos. Riesgo alto de deriva: lo que valida el backend puede no
validarlo el escritorio y viceversa.

### V3 — MEDIA: `repositories/` es código muerto

La carpeta `repositories/` (base, usuarios, permisos, reportes) **no se importa en ningún
lugar del proyecto**. Representa esfuerzo invertido que no aporta y confunde el panorama.
El punto 2 del Plan Maestro está técnicamente "hecho" pero es inútil tal como está.

### V4 — MEDIA: Migración SQLite no terminada

`migrate_*.py`, `migration/` y `bases_g/*.db` (7 bases) permanecen. `core/database_router.py`
todavía expone `is_sqlite()`. `plan_de_trabajo.md` afirma una limpieza que **no ocurrió en
disco**. Esto genera confusión sobre el estado real del proyecto.

### V5 — MEDIA: `ApiClient` del escritorio es insuficiente

`core/api_client.py` sólo implementa `get` y `post`. Para migrar el escritorio a la API
faltan `put`/`patch`/`delete` y manejo de errores/refresh token consistente.

### V6 — BAJA: Auditoría duplicada / inconsistente

El backend audita por endpoint; el escritorio (cuando edita por BD directa) no pasa por esa
auditoría. Resultado: el log de `auditoria` queda incompleto para operaciones del escritorio.

### V7 — BAJA: Sin caché/offline

No implementado, pero aceptable como fase tardía (la arquitectura actual lo permite
agnósticamente).

---

## 5. Plan rearmado

Frente al plan original de 8 pasos y la revisión previa de 5 acciones, propongo
**reordenar por impacto y reducir trabajo innecesario**:

### Ejes rectores

1. **El backend ya es la fuente de verdad para datos** → el escritorio debe volverse un
   cliente HTTP puro. No se crean nuevos endpoints de datos; se consumen los existentes.
2. **Eliminar el doble stack progresivamente**: el escritorio deja de importar `db.*`,
   `core.data_service`, `database.*`, `model.*` para datos. Esas capas raíz quedan solo
   para arranque/UI hasta su retiro.
3. **No invertir en `repositories/` muerto**: o se conecta al backend como capa delgado de
   cliente, o se elimina. No se "completa" con repositorios por esquema que nadie usará.
4. **Cerrar la migración SQLite de verdad**: ejecutar migraciones pendientes y borrar
   archivos legacy + remover `is_sqlite()`, para que el disco refleje la realidad.
5. **Unificar auditoría**: toda escritura (desktop y web) pasa por la API → un solo log.

### Nuevos objetivos (reemplazan los 8 originales)

- **O1.** Escritorio consume 100% de la API para datos (CRUD + reportes).
- **O2.** Unificar validación/permisos/auditoría en el backend.
- **O3.** Eliminar el doble stack de acceso a datos de la raíz.
- **O4.** Terminar y limpiar la migración SQLite (disco coherente).
- **O5.** (Tardío) Caché/offline opcional y mejoras de resiliencia del `ApiClient`.

---

## 6. Plan de ejecución (nuevo)

### Fase A — Preparar el cliente desktop (habilitador)

**Objetivo:** `ApiClient` capaz de cubrir todo el CRUD de datos.

- [ ] A.1 Extender `core/api_client.py` con `put`, `patch`, `delete`, y refresco automático
  de token en 401. Devolver dict consistente `{success, data, mensaje}` para todos.
- [ ] A.2 Añadir `core/api_database_client.py` (o métodos en `ApiClient`) que mapee 1:1 los
  endpoints de `database_router.py`: `listar_bases`, `tablas`, `data`, `search`,
  `columnas`, `crear`, `actualizar`, `eliminar`.
- [ ] A.3 Añadir `core/api_reportes_client.py` para los endpoints de `reportes_router.py`.
- [ ] A.4 Tests de humo: `test_api_client.py` que ejerza los 8 métodos contra el backend.

**Criterio de aceptación:** los métodos del cliente pasan contra la API con un usuario real.

### Fase B — Migrar operaciones de datos del escritorio a la API (CRÍTICA)

**Objetivo:** `VentanaPrincipal` deja de usar `db.router`/`db.service`/`db_registry`.

- [ ] B.1 Reemplazar `TreeLoader(self.router)` por carga vía `api_database_client.listar_bases`
  y `tablas`.
- [ ] B.2 Reemplazar búsqueda/consulta (líneas que usan `self.router.search`/`fetch_all`) por
  llamadas a la API.
- [ ] B.3 Reemplazar alta (`DatabaseService`/`insert`) por `api_database_client.crear`.
- [ ] B.4 Reemplazar edición (`self.router.update_by_id`) por `api_database_client.actualizar`
  (PATCH).
- [ ] B.5 Reemplazar baja (`self.router.delete_by_id`) por `api_database_client.eliminar`
  (DELETE).
- [ ] B.6 Confirmar que la auditoría del backend se dispara para todas estas acciones del
  escritorio (revisar tabla `auditoria`).
- [ ] B.7 Tests E2E: `test_qt_usa_api.py` (o manual documentado) que verifique que ningún
  módulo de `ventana_principal.py` importa `db.router`/`db.service`/`db_registry` para datos.

**Criterio de aceptación:** `grep` de `db.router|db.service|db_registry` en `ventana_principal.py`
devuelve 0 coincidencias para operaciones de datos.

### Fase C — Unificar validación y permisos en el backend

- [ ] C.1 Verificar que `database_router.py` aplica `validar_permiso`/`obtener_usuario_actual`
  en create/update/delete (no solo lectura).
- [ ] C.2 Reemplazar `core/access_control.py` y `core/seguridad.py` en el flujo del escritorio
  por validación vía respuesta de la API (el backend ya filtra por nivel/rol).
- [ ] C.3 Dejar un único punto de verdad de niveles en `backend/security/permissions.py`;
  exponerlo por un endpoint `/auth/me` si no existe.

### Fase D — Eliminar el doble stack y el código muerto

- [ ] D.1 Decidir destino de `repositories/`: conectarlo como cliente delgado de la API o
  eliminarlo. **Recomendación:** eliminar (es muerto y no aporta al cliente HTTP).
- [ ] D.2 Retirar `db/router.py`, `db/service.py`, `db/registry.py`, `core/data_service.py`
  una vez que el escritorio no los use (Fase B completa).
- [ ] D.3 Unificar `database/conexion.py` (raíz) y `backend/database/conexion.py` en un único
  módulo compartido importado por ambos.
- [ ] D.4 Eliminar `model/datcorr_dao_postgres.py` y `model/legacy/` si nadie los importa.

### Fase E — Cerrar la migración SQLite de verdad

- [ ] E.1 Ejecutar los `migrate_*.py` pendientes contra PostgreSQL y validar conteo de filas.
- [ ] E.2 Borrar `migrate_*.py`, `migration/` y `bases_g/*.db` del repo (o mover a `archive/`).
- [ ] E.3 Eliminar `is_sqlite()` de `core/database_router.py` y cualquier resto de rama SQLite.
- [ ] E.4 Actualizar `plan_de_trabajo.md` para que refleje el estado real (la "limpieza"
  aún no ocurrió en disco).

### Fase F — Reportes en el escritorio (opcional, valor rápido)

- [ ] F.1 Exponer los reportes en el escritorio vía `api_reportes_client` (la API ya los tiene).
- [ ] F.2 Reutilizar los mismos datos que `ReportesPage.jsx` consume.

### Fase G — Resiliencia (tardía)

- [ ] G.1 Implementar caché/offline ligero en `ApiClient` (cache de lecturas + cola de escritura).
- [ ] G.2 Manejo de reconexión y mensajes de error unificados en el escritorio.

---

## 7. Priorización y secuencia recomendada

| Orden | Fase | Prioridad          | Esfuerzo | Dependencia       |
| ----- | ---- | ------------------ | -------- | ----------------- |
| 1     | A    | Alta               | Bajo     | —                |
| 2     | B    | **Crítica** | Medio    | A                 |
| 3     | C    | Alta               | Bajo     | B                 |
| 4     | E    | Media              | Bajo     | — (paralela a A) |
| 5     | D    | Media              | Medio    | B, E              |
| 6     | F    | Baja               | Bajo     | B                 |
| 7     | G    | Baja               | Medio    | A, B              |

**Camino crítico:** A → B → C → D. Las fases E pueden correr en paralelo desde el inicio.

---

## 8. Riesgos y mitigaciones

- **R1:** El escritorio tiene 1345 líneas y múltiples formularios dinámicos (`DynamicForm`,
  `TreeLoader`). Mitigación: migrar por operación (B.1→B.5), no todo de golpe; mantener
  `db.router` disponible hasta cubrir B.7.
- **R2:** Permisos distintos entre `core/seguridad.py` y `backend/security`. Mitigación:
  C.1–C.3 validan paridad antes de cortar el código raíz.
- **R3:** Borrar `bases_g/*.db` sin migrar pierde datos históricos. Mitigación: E.1 antes de E.2.

---

## 9. Definición de terminado (DoD)

- [ ] El escritorio no importa `db.router`, `db.service`, `db_registry` para datos.
- [ ] Toda operación CRUD del escritorio pasa por la API y queda auditada.
- [ ] No existe código SQLite ni `is_sqlite()` en el repo.
- [ ] Una sola capa de conexión/validación/auditoría compartida por web y desktop.
- [ ] `repositories/` muerto eliminado o reconectado como cliente HTTP.
- [ ] `plan_de_trabajo.md` y `revision_plan_maestro.md` actualizados al estado real.
