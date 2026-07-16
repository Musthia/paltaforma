
## Análisis: Situación Actual de Tablas de Usuarios y Roles

### Estado Actual

| Tabla                                                    | Base         | ¿Quién la usa?                                                         | ¿En uso real? |
| -------------------------------------------------------- | ------------ | ------------------------------------------------------------------------ | -------------- |
| `usuarios` (columna `rol`)                           | `datcorr`  | Escritorio (consultas directas:`crud_usuarios.py`, `database/crud/`) | **Sí**  |
| `roles` / `usuarios_roles`                           | `datcorr`  | Escritorio (migrate, permisos_service)                                   | **Sí**  |
| `permisos` / `usuarios_permisos`                     | `datcorr`  | Escritorio (`usuario_tiene_permiso()` en `services/`)                | **Sí**  |
| `platform_users` (columna `role`)                    | `platform` | DATCORR web + SIMCO web (via platformcore)                               | **Sí**  |
| `platform_roles` / `platform_user_roles`             | `platform` | DATCORR web + SIMCOR web (via platformcore)                              | **Sí**  |
| `platform_permissions` / `platform_user_permissions` | `platform` | DATCORR web + SIMCO web (via platformcore)                               | **Sí**  |
| `users` (columna `role`)                             | `simco`    | SIMCO (seed únicamente,**no usado para auth** )                   | **No**   |

### Problema

* **Los datos están duplicados** : los mismos 22 usuarios migrados existen tanto en `datcorr.usuarios` como en `platform.platform_users`
* **Cambiar un rol no se propaga** : si modificás el rol de un usuario en platform, el escritorio no se entera (y viceversa)
* **El escritorio tiene bypass directo a DB** en ciertos módulos, saltándose la API unificada

---

## Propuesta de Unificación: Tabla Única en `platform`

### Principio

> **Una sola tabla de usuarios + una sola tabla de roles, todos los sistemas la leen desde el mismo lugar.**

### ¿Por qué `platform` y no `datcorr` o `simco`?

* Ya es la base compartida por ambos webs
* platformcore ya está diseñado para ser el núcleo
* La migración de 22 usuarios ya se hizo hacia `platform`

---

## Plan de Migración (5 fases)

### Fase 1 — Auditoría: encontrar todas las referencias a las tablas viejas

Buscar en `C:\plataforma\data_datcorr\` (y `simco_v01`) todo código que lea/escriba directamente `usuarios`, `roles`, `permisos` en la base `datcorr`, saltándose la API.

**Ejemplos conocidos:**

* `database/crud/crud_usuarios.py` — consultas directas a `usuarios`
* `services/usuarios_permisos_service.py` — consulta `permisos` + `usuarios_permisos`
* `services/permisos_service.py` — consulta `roles`
* `session_manager.py` línea 159 — fallback a `usuario_tiene_permiso()` que va directo a DB
* `db/registry.py` — conexión directa a `datcorr`

### Fase 2 — Migrar el escritorio a usar solo la API

Reemplazar cada bypass directo a `datcorr` por una llamada API a platformcore. Ejemplos:

| Llamada directa actual                | Reemplazo API                                                                 |
| ------------------------------------- | ----------------------------------------------------------------------------- |
| `crud_usuarios.crear_usuario(...)`  | `POST /users/`                                                              |
| `crud_usuarios.buscar_usuario(...)` | `GET /users/{id}`                                                           |
| `usuario_tiene_permiso(id, codigo)` | `GET /auth/me` (vía `_permisos` cache) o `GET /users/{id}/permissions` |
| `obtener_descripcion_nivel(nivel)`  | Pasar a ser función local (solo mapeo, no requiere DB)                       |

### Fase 3 — Migrar datos

1. Verificar que todos los usuarios de `datcorr.usuarios` ya existan en `platform.platform_users` (22 ya migrados)
2. Verificar que `datcorr.roles` → `platform.platform_roles` tengan los mismos registros
3. Verificar que `datcorr.usuarios_roles` → `platform.platform_user_roles` tengan las mismas asignaciones
4. Migrar `datcorr.permisos` → `platform.platform_permissions`
5. Migrar `datcorr.usuarios_permisos` → `platform.platform_user_permissions`

### Fase 4 — Unificar el login del escritorio

El escritorio ya usa la API unificada para login (`/auth/login` vía platformcore). Pero todavía:

* Tiene lógica de post-login que asume estructura de `datcorr`
* Almacena sesión con claves en español (`usuario`, `rol`, `es_superusuario`)
* Hace `sync_from_api()` que mapea mal los campos

**Corregir:** Ya empezamos en la iteración anterior. El escritorio debe depender 100% de la respuesta de platformcore.

### Fase 5 — Eliminar tablas viejas (solo cuando F1-F4 estén 100% operativas)

```
DROP TABLE IF EXISTS datcorr.usuarios_permisos CASCADE;
DROP TABLE IF EXISTS datcorr.permisos CASCADE;
DROP TABLE IF EXISTS datcorr.usuarios_roles CASCADE;
DROP TABLE IF EXISTS datcorr.roles CASCADE;
DROP TABLE IF EXISTS datcorr.usuarios CASCADE;

DROP TABLE IF EXISTS simco.users CASCADE;
```

---

## ¿Viable o mejor mantener separado?

| Aspecto                | Unificar (recomendado)                                  | Mantener separado                                              |
| ---------------------- | ------------------------------------------------------- | -------------------------------------------------------------- |
| **Consistencia** | Un solo cambio = todos los sistemas actualizados        | Hay que sincronizar manualmente                                |
| **Complejidad**  | Requiere migrar el escritorio a API                     | El escritorio ya tiene bypass directos que rompen consistencia |
| **Riesgo**       | Si falla la API, el escritorio se queda sin auth        | El escritorio puede caer a DB local como fallback              |
| **Esfuerzo**     | ~3-5 días hábiles                                     | 0 esfuerzo, pero el problema persiste                          |
| **Futuro**       | Escritorio como "cliente" de la API, igual que los webs | Sigue siendo un híbrido frágil                               |

**Mi recomendación:** Es viable y  **es lo correcto** . La arquitectura ya está diseñada para eso (platformcore). El escritorio ya usa la API para login. Solo hay que eliminar los bypasseos directos a DB que quedan y migrar el cacheo local de sesión a depender exclusivamente de la API.
