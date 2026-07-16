
**Lo que ya está funcionando:**

* **platformcore existe y está operativo** — modelos (`PlatformUser`, `PlatformRole`, `PlatformPermission`, relaciones), routers (`/auth`, `/users`, `/roles`, `/permissions`), servicios (`IdentityService`, `UserService`, `RoleService`, `PermissionService`), JWT con refresh tokens y blacklist.
* **Login unificado** — el escritorio ya usa `/auth/login` de platformcore (`base_datcorr.py:84`).
* **Backend web migrado** — el backend FastAPI del escritorio (`main.py`) ya incluye routers de platformcore y servicios como `roles_service.py` delegan en `PlatformRoleService`.
* **ApiUsuariosClient existe** — el escritorio tiene un cliente API listo para operaciones de usuarios/roles/permisos.
* **Los 22 usuarios están migrados** — como indica el plan.

**Lo que todavía usa tablas viejas en `datcorr`:**

* `services/usuario_service.py` — consulta directa `datcorr.usuarios` via `SessionLocal`
* `services/permisos_service.py` — consulta directa `datcorr.permisos`
* `services/usuarios_permisos_service.py` — consulta directa `datcorr.usuarios_permisos`
* `database/crud/crud_usuarios.py` — consulta directa `datcorr.usuarios`
* `database/modelos.py` y `modelos_roles.py` — ORM completo de tablas viejas
* GUI (ventanas) — carga usuarios/permisos desde servicios que tocan `datcorr` directo
* `session_manager.py:159` — fallback a `usuario_tiene_permiso()` que va a DB local

### Viabilidad por fase

| Fase                                    | Estado                                          | Observación                                                                                                                                                      |
| --------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **F1 — Auditoría**              | **Viable**                                | Referencias confirmadas con grep. Hay 66+ matches de bypass directo.                                                                                              |
| **F2 — Migrar escritorio a API** | **Parcialmente viable, requiere ajustes** | Login y backend web ya migrados. El GUI (PySide6) es la parte pendiente:`VentanaUsuarios` y servicios asociados consultan `datcorr` directo.                  |
| **F3 — Migrar datos**            | **Viable**                                | Usuarios ya migrados. Faltaría verificar/ migrar`roles`, `usuarios_roles`, `permisos`, `usuarios_permisos`.                                              |
| **F4 — Unificar login**          | **Ya iniciada**                           | Login 100% API.`sync_from_api()` existe pero hay que validar que cubra todos los campos que el GUI consume (`rol`, `nivel_seguridad`, `es_superusuario`). |
| **F5 — Eliminar tablas**         | **Viable pero bloqueada por F2**          | No se pueden dropear tablas mientras el GUI siga usando`SessionLocal` de `datcorr`.                                                                           |

### Problemas específicos detectados

1. **Endpoint faltante en platformcore:** `ApiUsuariosClient.listar_permisos_usuario()` llama a `GET /permisos/usuario/{usuario_id}` (`core/api_usuarios_client.py:44`), pero ese endpoint **no existe** en platformcore. Solo existe `/auth/me` (usuario actual) y `/permissions/me` (admin). Hay que agregarlo o cambiar la lógica del cliente.
2. **`initialize_postgres()` en `base_datcorr.py:165`:** Después del login, el escritorio sigue inicializando el engine de `datcorr`. Mientras exista, el escritorio mantiene conexión directa a esa base.
3. **Código deprecated:** Existe `backend/_deprecated/usuarios_router.py` y `permisos_router.py` que usan tablas viejas. Aunque no están montados en `main.py`, representan código muerto que debería eliminarse.
4. **`db/registry.py`:** Mantiene un registry global para PostgreSQL local. Si el escritorio va a ser 100% cliente de platformcore, este registry debería reorientarse o eliminarse.

### Conclusión

El plan es **técnicamente viable** porque la arquitectura ya está diseñada para ello (platformcore como núcleo, login unificado, clientes API existentes). Sin embargo, hay  **desajustes entre el plan y el código actual** :

* El plan da por hecho que el escritorio consulta tablas viejas, pero no menciona que el backend web ya está parcialmente migrado ni que el login ya está unificado.
* El plan no menciona el endpoint faltante `/permisos/usuario/{usuario_id}`.
* El mayor esfuerzo está en el  **GUI PySide6** , no en el backend web.

**Esfuerzo real estimado:** El plan dice "~3-5 días hábiles". Considerando que el backend web ya está migrado y el login está unificado, el trabajo real se concentra en:

* Migrar ~5-7 servicios del GUI a llamadas API
* Crear 1 endpoint faltante en platformcore
* Adaptar `session_manager.py` para eliminar el fallback a DB
* Migrar/verificar datos de roles y permisos
* Limpiar código deprecated
