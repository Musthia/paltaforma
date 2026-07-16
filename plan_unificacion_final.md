# Plan de Unificación de Usuarios y Roles — Versión Definitiva

## Objetivo

Una sola tabla de usuarios (`platform_users`) y una sola tabla de roles (`platform_roles`) en la base `platform`. Todos los sistemas (escritorio DATCORR, web DATCORR, web SIMCO) leen y escriben desde ahí mediante la API de platformcore.

---

## Estado Actual (confirmado)

### Lo que ya funciona

- platformcore operativo con modelos, routers, servicios, JWT
- Login del escritorio ya usa `/auth/login` de platformcore (`base_datcorr.py:84`)
- Backend web FastAPI del escritorio ya incluye routers de platformcore
- `ApiUsuariosClient`, `ApiDatabaseClient`, `ApiReportesClient` existen en el escritorio
- 22 usuarios migrados de `datcorr.usuarios` → `platform.platform_users`

### Tablas activas

| Tabla | Base | Quién la usa | Status |
|---|---|---|---|
| `usuarios` | `datcorr` | Escritorio (bypass directo vía `SessionLocal`) | **Reemplazar por API** |
| `roles` / `usuarios_roles` | `datcorr` | Escritorio (migrate, permisos_service) | **Reemplazar por API** |
| `permisos` / `usuarios_permisos` | `datcorr` | Escritorio (`usuario_tiene_permiso()`) | **Reemplazar por API** |
| `platform_users` | `platform` | DATCORR web + SIMCO web (via platformcore) | **Canonical** |
| `platform_roles` / `platform_user_roles` | `platform` | DATCORR web + SIMCO web (via platformcore) | **Canonical** |
| `platform_permissions` / `platform_user_permissions` | `platform` | DATCORR web + SIMCO web (via platformcore) | **Canonical** |
| `users` | `simco` | Seed únicamente, no usado para auth | **Eliminar** |

### Bypass directos a `datcorr` que deben migrarse a API

| Archivo | Qué hace |
|---|---|
| `services/usuario_service.py` | Consulta directa `datcorr.usuarios` vía `SessionLocal` |
| `services/permisos_service.py` | Consulta directa `datcorr.permisos` |
| `services/usuarios_permisos_service.py` | Consulta directa `datcorr.usuarios_permisos` |
| `database/crud/crud_usuarios.py` | CRUD directo sobre `datcorr.usuarios` |
| `database/modelos.py` + `modelos_roles.py` | ORM completo de tablas viejas |
| GUI (ventanas PySide6) | Carga usuarios/permisos desde servicios que tocan `datcorr` directo |
| `session_manager.py:159` | Fallback a `usuario_tiene_permiso()` que va a DB local |

---

## Plan de Trabajo (6 fases)

### Fase 0 — Crear endpoint faltante en platformcore

**Problema:** `ApiUsuariosClient.listar_permisos_usuario()` llama a `GET /permisos/usuario/{usuario_id}` pero ese endpoint **no existe**.

**Acción:**
- Agregar router/endpoint en `platformcore/routers/permissions.py`:
  `GET /permissions/user/{user_id}` → devuelve lista de códigos de permiso
- Alternativamente: si solo se necesita para el usuario logueado, `GET /auth/me` ya lo cubre

**Duración:** ~2-3 horas

---

### Fase 1 — Auditoría exhaustiva

**Acción:** Grep completo sobre `C:\plataforma\data_datcorr\` y `C:\plataforma\simco_v01\` para listar **cada referencia directa** a las tablas viejas (`usuarios`, `roles`, `permisos`, `session` de `datcorr`).

**Objetivo:** Tener un checklist 1:1 de qué tocar, sin sorpresas.

**Ya confirmado:** 66+ matches de bypass directo (escritorio + backend deprecated + GUI).

**Duración:** ~1 día

---

### Fase 2 — Migrar servicios del escritorio a API (el esfuerzo real)

Reemplazar cada bypass directo por llamada a platformcore:

| Llamada directa actual | Reemplazo API |
|---|---|
| `crud_usuarios.crear_usuario(...)` | `POST /users/` |
| `crud_usuarios.buscar_usuario(...)` | `GET /users/{id}` |
| `usuario_tiene_permiso(id, codigo)` | `GET /auth/me` (cache `_permisos`) o `GET /permissions/user/{id}` |
| `obtener_descripcion_nivel(nivel)` | Función local (solo mapeo, no requiere DB) |
| `services/usuario_service.py` queries | `ApiUsuariosClient` |
| `services/permisos_service.py` queries | `ApiClient.get("/permissions/...")` |
| `services/usuarios_permisos_service.py` queries | `ApiClient.get("/permissions/user/{id}")` |

**Archivos del GUI a migrar (~5-7):**
- `ui/ventana_usuarios.py` o similar (gestión de usuarios)
- `ui/ventana_roles.py` (gestión de roles)
- `ui/ventana_permisos.py` (gestión de permisos)
- Cualquier diálogo que cargue listas de usuarios/roles para combos

**Duración:** ~2-3 días

---

### Fase 3 — Desconectar `initialize_postgres()` y `db/registry.py`

**Acción:**
- `base_datcorr.py:165`: Eliminar o condicionar `initialize_postgres()` — ya no necesario si todo va vía API
- `db/registry.py`: Reorientar para que use `platform` en vez de `datcorr`, o eliminar si ningún módulo lo requiere

**Riesgo:** Verificar que ningún módulo use el engine global de `datcorr` para consultas que no tengan reemplazo API.

**Duración:** ~4 horas

---

### Fase 4 — Migrar datos de roles y permisos

**Acción:**
1. Verificar que `datcorr.roles` → `platform.platform_roles` tengan los mismos registros
2. Verificar que `datcorr.usuarios_roles` → `platform.platform_user_roles` tengan las mismas asignaciones
3. Migrar `datcorr.permisos` → `platform.platform_permissions`
4. Migrar `datcorr.usuarios_permisos` → `platform.platform_user_permissions`

**Script:** Crear un script `migrate_roles_permisos.py` que lea de `datcorr` y escriba en `platform`.

**Duración:** ~1 día

---

### Fase 5 — Limpieza final

**Acción:**
1. Eliminar `backend/_deprecated/` (usuarios_router.py, permisos_router.py)
2. Eliminar `database/modelos.py`, `database/modelos_roles.py` (o mover a backup)
3. Eliminar seed de SIMCO que crea `simco.users`
4. Drop tables viejas solo cuando F2-F4 estén 100% operativas:

```sql
DROP TABLE IF EXISTS datcorr.usuarios_permisos CASCADE;
DROP TABLE IF EXISTS datcorr.permisos CASCADE;
DROP TABLE IF EXISTS datcorr.usuarios_roles CASCADE;
DROP TABLE IF EXISTS datcorr.roles CASCADE;
DROP TABLE IF EXISTS datcorr.usuarios CASCADE;

DROP TABLE IF EXISTS simco.users CASCADE;
```

**Duración:** ~4 horas

---

## Resumen de esfuerzo

| Fase | Duración | Depende de |
|---|---|---|
| F0 — Endpoint faltante | 2-3h | Nada |
| F1 — Auditoría | 1 día | Nada |
| F2 — Migrar servicios/GUI | 2-3 días | F0, F1 |
| F3 — Desconectar engine datcorr | 4h | F2 |
| F4 — Migrar datos roles/permisos | 1 día | F2 |
| F5 — Limpieza | 4h | F2, F3, F4 |
| **Total** | **~5-7 días** | |

---

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| API caída = escritorio sin auth | Mantener el engine de `datcorr` como respaldo temporal hasta validación |
| Endpoint faltante bloquea F2 | F0 como prerequisito |
| GUI tiene lógica transaccional compleja | Migrar por capas: primero consultas (read), luego escrituras (write) |
| Algun módulo olvidado usa tablas viejas | F1 + pruebas post-migración |
| Seed de SIMCO crea usuario inconsistente | Eliminar seed, documentar que los usuarios se crean vía platformcore |

---

## Criterios de éxito

- [ ] El escritorio funciona 100% sin conexión directa a `datcorr.usuarios`
- [ ] Crear/modificar un rol desde cualquier app se refleja en todas
- [ ] Login funciona igual en escritorio, DATCORR web y SIMCO web
- [ ] 0 referencias a tablas viejas en `data_datcorr/`
- [ ] Tablas viejas dropeadas sin impacto
- [ ] Tests existentes (16/16) siguen pasando
