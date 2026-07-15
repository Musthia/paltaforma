# Propuesta de Implementación — Plataforma Unificada DATCORR + SIMCO

> Basado en el análisis del código real de `data_datcorr/` y `simco_v01/`. Este documento detalla la implementación concreta, archivo por archivo, y el orden de ejecución.

---

## 1. Diagnóstico del plan original

El plan de 9 fases del `Resumen_Unificacion_DATCORR_SIMCO.md` es conceptualmente correcto pero carece de:

| Carencia | Solución propuesta |
|----------|-------------------|
| Estructura de paquete Python (`platformcore/`) no definida | Crear `platformcore/` como paquete instalable con `pip install -e .` |
| No especifica qué archivos crear y con qué contenido | Este documento detalla cada archivo |
| No define el orden de implementación interno por archivo | Fases P0.1, P0.2, etc. con archivos concretos |
| No menciona compatibilidad hacia atrás | Ambos proyectos seguirán funcionando durante la migración |
| No hay plan de migración de datos | Estrategia por fases: extraer → adaptar → migrar datos |

---

## 2. Estructura del paquete `platformcore/`

```
plataforma/
├── platformcore/                          # ← NUEVO: Paquete compartido
│   ├── __init__.py                    # Exporta símbolos principales
│   ├── config.py                      # Settings unificado (SECRET_KEY, DB URLs, etc.)
│   ├── database.py                    # Base declarativa + engine + sesión + get_db
│   ├── exceptions.py                  # Excepciones personalizadas
│   ├── logger.py                      # Logging unificado
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── identity.py                # Usuario, RefreshToken, TokenBlacklist, PasswordResetToken
│   │   ├── security.py                # Rol, Permiso, UsuarioRol, UsuarioPermiso
│   │   └── audit.py                   # Auditoria
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── identity.py                # LoginRequest, TokenResponse, MeResponse, etc.
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── identity.py                # AuthService (login, logout, refresh, password reset)
│   │   ├── security.py                # UserService, RoleService, PermissionService
│   │   └── audit.py                   # AuditService
│   │
│   ├── dependencies.py                # get_current_user, require_permission, require_role
│   ├── jwt.py                         # JWT create/verify/refresh
│   ├── security.py                    # Password hashing (bcrypt via passlib)
│   ├── middleware.py                  # JWTMiddleware + RateLimitMiddleware
│   └── tests/
│       ├── __init__.py
│       ├── test_jwt.py
│       ├── test_services.py
│       └── conftest.py
│
├── data_datcorr/                      # ← MODIFICADO: importará de platformcore/
├── simco_v01/                         # ← MODIFICADO: importará de platformcore/
│
├── setup.py                           # ← NUEVO: pip install -e .
├── pyproject.toml                     # ← NUEVO
├── requirements-platform.txt          # ← NUEVO: dependencias del platform
├── .gitignore                         # ← MODIFICADO: ignorar __pycache__ de platform
│
├── Propuesta_Implementacion_Plataforma.md  # ← ESTE DOCUMENTO
├── Resumen_Unificacion_DATCORR_SIMCO.md    # (existente)
└── Plan_Unificacion_DATCORR_SIMCO.md       # (existente)
```

---

## 3. Plan de implementación por archivos

### Fase P0 — Infraestructura del monorepo

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `pyproject.toml` | CREAR | Config setuptools + dependencias del platform |
| `setup.py` | CREAR | Editable install |
| `requirements-platform.txt` | CREAR | Dependencias mínimas (FastAPI, SQLAlchemy, jose, passlib, bcrypt) |
| `platformcore/__init__.py` | CREAR | Exporta: config, database, jwt, security, exceptions, logger |
| `platformcore/config.py` | CREAR | `PlatformSettings` unificando `.env` de DATCORR y SIMCO |
| `platformcore/database.py` | CREAR | `Base`, `engine`, `SessionLocal`, `get_db()` |
| `platformcore/exceptions.py` | CREAR | `PlatformException`, `AuthError`, `PermissionDenied` |
| `platformcore/logger.py` | CREAR | Logger "platform" |

### Fase P1 — Identity (autenticación compartida)

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `platformcore/security.py` | CREAR | `hash_password()`, `verify_password()` (unifica `utils/hash.py` + `core/security.py`) |
| `platformcore/jwt.py` | CREAR | `create_token()`, `verify_token()`, `create_refresh_token()`, `verify_refresh_token()` (unifica `jwt_manager.py` + `core/jwt.py`) |
| `platformcore/models/identity.py` | CREAR | `User`, `RefreshToken`, `TokenBlacklist`, `PasswordResetToken` (unifica modelos de ambos) |
| `platformcore/schemas/identity.py` | CREAR | `LoginRequest`, `TokenResponse`, `MeResponse`, `RefreshRequest`, `ChangePasswordRequest`, `ForgotPasswordRequest`, `ResetPasswordRequest` |
| `platformcore/services/identity.py` | CREAR | `IdentityService` — login, logout, refresh, password reset (unifica `auth_service` de ambos) |
| `platformcore/dependencies.py` | CREAR | `get_current_user()`, `get_optional_user()` |

### Fase P2 — Security (usuarios, roles, permisos)

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `platformcore/models/security.py` | CREAR | `Role`, `Permission`, `UserRole`, `UserPermission` |
| `platformcore/services/security.py` | CREAR | `UserService` (CRUD), `RoleService`, `PermissionService`, `require_permission()`, `require_role()` |

### Fase P3 — Audit

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `platformcore/models/audit.py` | CREAR | `AuditLog` (unifica `Auditoria` + `AuditLog`) |
| `platformcore/services/audit.py` | CREAR | `AuditService.record()` |

### Fase P4 — Middleware compartido

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `platformcore/middleware.py` | CREAR | `JWTMiddleware` (unificado), `RateLimitMiddleware` (unificado) |

### Fase R1 — Refactor DATCORR para usar platform

Reemplazar imports locales por `from platform import ...` en:
- `data_datcorr/backend/security/jwt_manager.py` → wrapper/fachada que delega en `platform.jwt`
- `data_datcorr/backend/services/auth_service.py` → delega en `platform.services.identity.IdentityService`
- `data_datcorr/backend/services/auditoria_service.py` → delega en `platform.services.audit.AuditService`
- `data_datcorr/backend/security/permissions.py` → delega en `platform.services.security`
- `data_datcorr/database/modelos.py` → hereda de `platform.models.identity.User`
- etc.

### Fase R2 — Refactor SIMCO para usar platform

Mismo proceso: reemplazar `app.core.jwt`, `app.core.security`, `app.core.deps`, `app.services.auth_service`, etc. por `platform.*`.

---

## 4. Orden de ejecución recomendado

```
Semana 1: P0 (infraestructura) + P1 (identity)
  Día 1: pyproject.toml, setup.py, platformcore/__init__.py, platformcore/config.py, platformcore/database.py
  Día 2: platformcore/security.py (passwords), platformcore/jwt.py
  Día 3: platformcore/models/identity.py, platformcore/models/__init__.py
  Día 4: platformcore/schemas/identity.py, platformcore/services/identity.py
  Día 5: platformcore/dependencies.py, platformcore/middleware.py

Semana 2: P2 (security) + P3 (audit)
  Día 1-2: platformcore/models/security.py, platformcore/services/security.py
  Día 3: platformcore/models/audit.py, platformcore/services/audit.py
  Día 4-5: Tests unitarios del platform

Semana 3: R1 (refactor DATCORR)
  Reemplazar imports y verificar que todo funciona

Semana 4: R2 (refactor SIMCO)
  Reemplazar imports y verificar que todo funciona
```

---

## 5. Decisiones técnicas

| Decisión | Opción elegida | Motivo |
|----------|---------------|--------|
| Hashing | bcrypt via passlib (ambos ya lo usan) | Compatible, misma librería |
| JWT | python-jose (ambos ya lo usan) | Sin cambio de librería |
| ORM | SQLAlchemy 2.0 (ambos ya lo usan) | Sin cambio |
| Base declarativa | Una sola `Base` en `platform.database` | Todos los modelos comparten la misma base |
| BD de platform | PostgreSQL (esquema `platform` o BD separada `platform`) | Ya usan PostgreSQL ambos |
| Nombres de tablas | `platform_users`, `platform_roles`, etc. (prefijo `platform_`) | Evita colisión con tablas de módulos |
| Frontend | Se mantiene separado (JS en DATCORR, TS en SIMCO) | Decisión de convergencia postergada |
| Tests | pytest + httpx (FastAPI TestClient) | Ambos proyectos sin tests existentes |

---

## 6. Migración de datos

Los datos existentes se migrarán **después** de que el platform esté funcionando y ambos proyectos hayan sido refactorizados:

1. Crear BD `platform` en PostgreSQL
2. Ejecutar script `platformcore/scripts/migrate_users.py` que:
   - Lee usuarios de DATCORR (SQLite o PostgreSQL)
   - Lee usuarios de SIMCO (SQLite o PostgreSQL)
   - Detecta duplicados por username/email
   - Unifica en `platform_users`
3. Los módulos DATCORR y SIMCO conservan sus propias BD con datos funcionales (expedientes, solicitudes, etc.)

---

## 7. Cómo empezar la implementación

```bash
# 1. Crear estructura de directorios
mkdir -p platformcore/models platformcore/schemas platformcore/services platformcore/tests

# 2. Crear pyproject.toml
# 3. Crear setup.py
# 4. Implementar platformcore/config.py
# 5. Implementar platformcore/database.py
# 6. Instalar en modo editable
pip install -e .
# 7. Implementar servicios capa por capa
```

La implementación comienza inmediatamente con la Fase P0.
