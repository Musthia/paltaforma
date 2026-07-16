# Conclusiones y Plan de Ejecución — Unificación Usuarios/Roles

## Resumen de verificación

El plan `plan_unificacion_final.md` es **técnicamente correcto en objetivo**, pero requiere ajustes porque parte de la migración ya está realizada y el alcance real es menor al estimado.

### Estado real confirmado

| Aspecto | Estado |
|---|---|
| **platformcore operativo** | Sí — modelos, routers, servicios, JWT, refresh tokens |
| **Login unificado** | Sí — escritorio usa `/auth/login` (`base_datcorr.py:84`) |
| **Backend web migrado** | Sí — `main.py` monta routers de platformcore |
| **GUI parcialmente migrado** | Sí — `ventana_usuarios.py` ya usa `ApiUsuariosClient` en 4 puntos |
| **Endpoint faltante** | Confirmado — `/permissions/user/{user_id}` no existe en platformcore |
| **Bypass directos restantes** | Confirmados — `services/usuario_service.py`, `services/permisos_service.py`, `services/usuarios_permisos_service.py`, `database/crud/crud_usuarios.py`, `database/modelos*.py`, `session_manager.py:159` |
| **Código deprecated** | Confirmado — `backend/_deprecated/usuarios_router.py`, `permisos_router.py` |
| **22 usuarios migrados** | Confirmado |
| **Seed SIMCO** | Confirmado — `simco_v01/backend/app/db/seed.py` crea `users` |

### Correcciones al plan original

1. **Fase 2 sobreestimada**: `ventana_usuarios.py` ya consume `ApiUsuariosClient`. No requiere migración desde cero, solo verificar que no haya servicios legacy respaldándolo.
2. **No existen `ui/ventana_roles.py` ni `ui/ventana_permisos.py`** como ventanas separadas. El plan los lista como objetivo de migración, pero no existen como archivos independientes.
3. **Fase 4 puede ejecutarse en paralelo** con F2, no depende estrictamente de que F2 termine si se usa un flag o configuración.
4. **Fase 3 es más riesgosa de lo estimado**: `initialize_postgres()` inicializa el engine global que usan múltiples módulos, no solo el GUI. Requiere auditoría de dependencias antes de eliminar.

---

## Plan de Ejecución Ajustado

### Fase 0 — Endpoint faltante (2-3 h)

**Objetivo:** Habilitar `GET /permissions/user/{user_id}` en platformcore.

**Acciones:**
- Crear endpoint en `platformcore/routers/permissions.py`:
  - `GET /permissions/user/{user_id}` → lista de códigos de permiso
  - Usar `PermissionService.user_has_permission()` o extender `get_user_permissions()` para filtrar por user_id arbitrario
- Actualizar `ApiUsuariosClient.listar_permisos_usuario()` para usar el nuevo endpoint
- Probar con curl/Postman

**Criterio de completitud:** `ApiUsuariosClient.listar_permisos_usuario()` responde 200 con la lista de permisos del usuario.

---

### Fase 1 — Auditoría detallada (1 día)

**Objetivo:** Checklist 1:1 de referencias a tablas/ORM legacy.

**Acciones:**
- Ejecutar grep sobre `data_datcorr/` y `simco_v01/` buscando:
  - `SessionLocal`, `database.conexion`, `database.session`
  - `usuarios`, `roles`, `permisos`, `usuarios_roles`, `usuarios_permisos`
  - `crud_usuarios`, `usuario_service`, `permisos_service`, `usuarios_permisos_service`
  - `db_registry`, `initialize_postgres`
- Mapear cada match a: archivo, función, si tiene reemplazo API, prioridad (alta/media/baja)
- Identificar módulos que usan `datcorr` para consultas no-auth (reportes, inventario) — estos **no** entran en esta unificación

**Entregable:** Checklist markdown con ~30-40 ítems clasificados.

---

### Fase 2 — Migrar servicios legacy a API (2-3 días)

**Objetivo:** Eliminar consultas directas a `datcorr.usuarios`, `datcorr.roles`, `datcorr.permisos` desde servicios del escritorio.

**Orden recomendado (de menor a mayor riesgo):**

1. **`services/permisos_service.py`** — Bajo riesgo
   - `listar_permisos()` → `GET /permissions/`
   - `obtener_descripcion_nivel()` → ya es función local, sin cambios
   - Eliminar import de `database.conexion`

2. **`services/usuarios_permisos_service.py`** — Bajo riesgo
   - `asignar_permiso_usuario()` → `POST /permissions/assign`
   - `quitar_permiso_usuario()` → `POST /permissions/remove`
   - `listar_permisos_usuario()` → `GET /permissions/user/{user_id}`
   - `usuario_tiene_permiso()` → `GET /auth/me` (cache) o endpoint nuevo
   - Eliminar imports de `database.conexion`

3. **`services/usuario_service.py`** — Riesgo medio
   - Funciones CRUD → `ApiUsuariosClient`
   - Mantener firma de funciones para no romper llamadores
   - `repo.close()` en `finally` (el repo actual usa `SessionLocal`)

4. **`database/crud/crud_usuarios.py`** — Bajo riesgo si nadie lo usa
   - Verificar si algún módulo lo importa
   - Si no, marcar como deprecated; si sí, migrar a API client

5. **`session_manager.py:159`** — Bajo riesgo
   - Eliminar fallback a `usuario_tiene_permiso()`
   - Confiar 100% en `_permisos` cache desde `/auth/me`

**Criterio de completitud:** `grep -r "SessionLocal" data_datcorr/services/` devuelve 0 matches (o solo comentarios).

---

### Fase 3 — Desconectar engine `datcorr` (4 h)

**Objetivo:** Eliminar dependencia de conexión directa a `datcorr` desde el escritorio.

**Acciones:**
1. En `base_datcorr.py:165`, comentar/eliminar `initialize_postgres()`
2. Ejecutar la app y verificar que no haya errores al iniciar
3. Si hay errores, identificar el módulo que requiere el engine y evaluar si tiene reemplazo API
4. Revisar `db/registry.py`:
   - Si ningún módulo lo usa para `datcorr`, eliminarlo o reorientarlo a `platform`
   - `db_registry` se usa en `ventana_principal copy.py` para diagnóstico, no en producción

**Criterio de completitud:** Escritorio inicia y funciona sin errores de import/DB.

---

### Fase 4 — Migrar datos de roles y permisos (1 día)

**Objetivo:** Sincronizar `datcorr.roles/permisos` → `platform.platform_roles/permissions`.

**Acciones:**
1. Crear script `migrate_roles_permisos.py` en `data_datcorr/`:
   - Leer `datcorr.roles` → insertar en `platform.platform_roles` (evitar duplicados por `name`)
   - Leer `datcorr.usuarios_roles` → insertar en `platform.platform_user_roles` (evitar duplicados por `user_id`)
   - Leer `datcorr.permisos` → insertar en `platform.platform_permissions` (evitar duplicados por `code`)
   - Leer `datcorr.usuarios_permisos` → insertar en `platform.platform_user_permissions`
2. Ejecutar en staging primero, validar conteos
3. Backup de tablas origen antes de cualquier modificación

**Criterio de completitud:** Conteo de roles/permisos/usuarios_roles en ambas bases coincide.

---

### Fase 5 — Limpieza final (4 h)

**Objetivo:** Eliminar código y tablas legacy.

**Acciones:**
1. Eliminar `backend/_deprecated/` (mover a backup por 1 sprint antes de borrar)
2. Eliminar `database/modelos.py`, `database/modelos_roles.py`, `database/modelos_refresh.py`, `database/modelos_reset.py` (o mover a backup)
3. Eliminar `database/crud/crud_usuarios.py` si no tiene usadores
4. Eliminar seed SIMCO (`simco_v01/backend/app/db/seed.py`) — documentar que los usuarios se crean vía platformcore
5. **Solo después de validación completa**, ejecutar DDL:
   ```sql
   DROP TABLE IF EXISTS datcorr.usuarios_permisos CASCADE;
   DROP TABLE IF EXISTS datcorr.permisos CASCADE;
   DROP TABLE IF EXISTS datcorr.usuarios_roles CASCADE;
   DROP TABLE IF EXISTS datcorr.roles CASCADE;
   DROP TABLE IF EXISTS datcorr.usuarios CASCADE;
   DROP TABLE IF EXISTS simco.users CASCADE;
   ```

**Criterio de completitud:** 0 referencias a tablas/archivos legacy en `data_datcorr/`.

---

## Esfuerzo revisado

| Fase | Duración | Depende de |
|---|---|---|
| F0 — Endpoint faltante | 2-3 h | Nada |
| F1 — Auditoría | 1 día | Nada |
| F2 — Migrar servicios legacy | 2 días | F0, F1 |
| F3 — Desconectar engine datcorr | 4 h | F2 |
| F4 — Migrar datos roles/permisos | 1 día | Puede ser paralelo a F2 |
| F5 — Limpieza | 4 h | F2, F3, F4 |
| **Total** | **~4-6 días** | |

**Ahorro vs plan original:** ~1-2 días, porque el GUI ya está migrado y el backend web ya usa platformcore.

---

## Riesgos y mitigaciones (ajustados)

| Riesgo | Mitigación |
|---|---|
| API caída = escritorio sin auth | Mantener engine `datcorr` como respaldo hasta validación completa de F2 |
| Endpoint faltante bloquea F2 | F0 como prerequisito estricto |
| `initialize_postgres()` rompe módulos ocultos | F3 requiere lista de dependencias de F1 |
| Datos duplicados en migración F4 | Script con verificación previa y backup |
| Seed SIMCO crea usuario inconsistente | Eliminar seed, documentar flujo de creación vía platformcore |

---

## Criterios de éxito

- [ ] `GET /permissions/user/{user_id}` responde correctamente
- [ ] Escritorio funciona 100% sin `SessionLocal` en `services/`
- [ ] Crear/modificar rol/usuario desde cualquier app se refleja en todas
- [ ] Login funciona igual en escritorio, DATCORR web y SIMCO web
- [ ] 0 referencias a tablas legacy en `data_datcorr/services/` y `data_datcorr/database/`
- [ ] Tablas viejas dropeadas sin impacto
- [ ] `grep -r "datcorr" data_datcorr/` solo devuelve comentarios/docs
