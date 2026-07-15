# Recuperación de contraseña y endurecimiento del módulo de autenticación


+ cliente de escritorio PySide6 en `services/`, `core/`, `ui/`, `ventanas/`).

Este documento propone las mejoras concretas y cómo ejecutarlas en **este** proyecto.

---

## 1. Diagnóstico (doc vs proyecto)

| Requisito del doc                                  | Estado en el proyecto       | Dónde mirar                                               |
| -------------------------------------------------- | --------------------------- | ---------------------------------------------------------- |
| `email` único y obligatorio en `usuarios`     | ❌ No existe el campo       | `database/modelos.py:38` (clase `Usuario`)             |
| `ultimo_login`                                   | ❌ No existe                | `database/modelos.py`                                    |
| `ultimo_cambio_password`                         | ❌ No existe                | `database/modelos.py`                                    |
| Tabla`password_reset_tokens` separada            | ❌ No existe                | `database/modelos_*.py`                                  |
| Endpoints`/forgot-password`, `/reset-password` | ❌ No existen               | `backend/routers/auth_router.py`                         |
| `rol_id` → tabla `roles` normalizada          | ⚠️`rol` es string plano | `database/modelos.py:74`                                 |
| Hash de contraseña seguro                         | ✅ bcrypt (passlib)         | `utils/hash.py`                                          |
| JWT access + refresh con`jti`                    | ✅                          | `backend/security/jwt_manager.py`                        |
| Rotación + detección de reuse de refresh         | ✅                          | `backend/services/auth_service.py:280`                   |
| Blacklist de tokens                                | ✅                          | `database/modelos_blacklist.py`                          |
| Rate limiting en login                             | ✅ (en memoria)             | `backend/middleware/rate_limit_middleware.py`            |
| Auditoría                                         | ✅                          | `backend/services/auditoria_service.py`                  |
| Permisos funcionales + niveles                     | ✅                          | `core/seguridad.py`, `backend/security/permissions.py` |

### Vulnerabilidades críticas a corregir

1. **Secreto JWT por defecto público** — `backend/security/jwt_manager.py:28`
   `SECRET_KEY = os.getenv("JWT_SECRET_KEY", "DATCORR_SECRET_KEY")`.
   Si falta la variable de entorno, cualquiera firma tokens válidos.
2. **Código muerto / bug en `verificar_token`** — `backend/security/jwt_manager.py:167-187`
   Hay un bloque duplicado de validación de usuario **después de `return payload`** que nunca se ejecuta.
3. **Fechas inconsistentes** — access token usa `datetime.now(timezone.utc)` (aware) y el refresh
   usa `datetime.utcnow()` (naive). Riesgo de comparaciones erróneas.
4. **Rate limiting en memoria por proceso** — `defaultdict` reinicia al reiniciar y no se comparte
   entre workers/instancias; además solo protege `/auth/login`.
5. **Sin bloqueo por cuenta** — solo se limita por IP; un atacante desde varias IPs puede hacer
   fuerza bruta al nombre de usuario.
6. **Enumeración de usuarios** — login distingue "Usuario incorrecto" de "Password incorrecta".

---

## 2. Propuestas

### 2.1 Modelo de datos (PostgreSQL)

Agregar a `usuarios` y crear `password_reset_tokens`. Mantener `rol` como string es aceptable
por ahora; la normalización a `roles` se deja como fase 2 (ver §4).

```sql
-- 1) Campos faltantes en usuarios
ALTER TABLE public.usuarios
    ADD COLUMN email VARCHAR(255),
    ADD COLUMN ultimo_login TIMESTAMP,
    ADD COLUMN ultimo_cambio_password TIMESTAMP;

UPDATE public.usuarios SET email = usuario || '@empresa.com' WHERE email IS NULL;

ALTER TABLE public.usuarios
    ALTER COLUMN email SET NOT NULL,
    ADD CONSTRAINT usuarios_email_unique UNIQUE (email);

-- 2) Tabla de tokens de recuperación (temporal, fuera de usuarios)
CREATE TABLE public.password_reset_tokens (
    id                  SERIAL PRIMARY KEY,
    usuario_id          INTEGER NOT NULL
                            REFERENCES public.usuarios(id) ON DELETE CASCADE,
    token_hash         VARCHAR(255) NOT NULL,
    expires_at         TIMESTAMP NOT NULL,
    usado              BOOLEAN DEFAULT FALSE,
    ip_solicitud       VARCHAR(100),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_reset_usuario ON public.password_reset_tokens(usuario_id);
CREATE INDEX ix_reset_token  ON public.password_reset_tokens(token_hash);
```

Reflejar lo mismo en `database/modelos.py` (SQLAlchemy) para que el ORM y `crear_tablas.py`
estén alineados.

### 2.2 Generación y validación de tokens

- Generar token aleatorio criptográfico (`secrets.token_urlsafe(32)`) y guardar **solo su hash**
  (bcrypt o SHA-256 + salt). Nunca guardar el token plano.
- TTL corto (15-30 min), un solo uso (`usado`), y revocar todos los tokens pendientes al cambiar
  la contraseña.
- Enviar por SMTP el enlace `https://dominio/reset-password?token=...`.

### 2.3 Endpoints (FastAPI)

```text
POST /auth/forgot-password   { email }
POST /auth/reset-password    { token, nueva_password }
PATCH /auth/change-password { actual, nueva }   (autenticado)
```

Reglas:

- `forgot-password` **siempre responde 202 genérico** ("Si el correo existe, enviamos instrucciones")
  para no enumerar cuentas.
- `reset-password` valida fuerza de la nueva contraseña y actualiza `ultimo_cambio_password`.
- Login debe setear `ultimo_login = now()`.

### 2.4 Endurecimiento de seguridad

1. **Secreto JWT obligatorio en producción** (sin fallback):
   ```python
   SECRET_KEY = os.getenv("JWT_SECRET_KEY")
   if ENVIRONMENT == "production" and not SECRET_KEY:
       raise RuntimeError("JWT_SECRET_KEY no configurado")
   ```
2. **Eliminar el código muerto** en `verificar_token` y dejar la validación en un único lugar
   (`obtener_usuario_actual` ya hace decode + blacklist; `verificar_token` está duplicado).
3. **Fechas timezone-aware** en todos los tokens (`datetime.now(timezone.utc)`).
4. **Rate limiting + bloqueo por cuenta** compartido (Redis o tabla en BD) y aplicado también a
   `/auth/forgot-password` y `/auth/reset-password`. Bloquear la cuenta tras N intentos fallidos
   y registrar en auditoría.
5. **Mensaje de login genérico** ("Credenciales inválidas") para evitar enumeración.
6. **CORS y HTTPS** revisados en `backend/main.py` (`COOKIE_SECURE=true` en producción).

### 2.5 Unificar arquitectura (recomendado)

El doc pide "PySide6 consumirá exactamente la misma API". Hoy existe auth duplicado
(`services/auth_service.py` + `core/session_manager.py` con acceso directo a BD). Conviene que el
cliente de escritorio llame a la API (login/refresh/forgot/reset) y deje de autenticar contra
PostgreSQL directo, para no duplicar lógica de seguridad.

---

## 3. Cómo ejecutarlo en este proyecto (paso a paso)

### Paso 1 — Backup y migración de datos

```bash
# Backup de la base antes de tocar el esquema
pg_dump datcorr > backup_$(date +%Y%m%d).sql
# Ejecutar el SQL del §2.1 (o crear la migración en Alembic si se usa)
```

### Paso 2 — Modelos SQLAlchemy

Editar `database/modelos.py`:

- Agregar `email` (unique, nullable=False), `ultimo_login`, `ultimo_cambio_password` a `Usuario`.
- Crear la clase `PasswordResetToken` (espejo del SQL §2.1) en un nuevo `database/modelos_reset.py`
  e importarlo en `database/conexion.py` para que `Base.metadata.create_all` lo cree.

### Paso 3 — Servicio de recuperación

Crear `backend/services/password_reset_service.py` con:

- `solicitar_reset(db, email, ip)` → genera token, guarda hash, devuelve el token para enviar por mail.
- `resetear_password(db, token, nueva_password)` → valida hash/no expirado/no usado, actualiza
  `password_hash` y `ultimo_cambio_password`, marca `usado=True`, revoca tokens pendientes e
  invalida refresh tokens del usuario.
- `enviar_email_reset(destinatario, enlace)` usando SMTP (credenciales desde `.env`).

### Paso 4 — Esquemas Pydantic

En `backend/schemas/auth_schema.py` agregar `ForgotPasswordRequest`, `ResetPasswordRequest`,
`ChangePasswordRequest`.

### Paso 5 — Router

En `backend/routers/auth_router.py` agregar los tres endpoints del §2.3, protegiendo
`change-password` con `Depends(obtener_usuario_actual)`.

### Paso 6 — Endurecer JWT y rate limiting

- Aplicar §2.4 (1-5) en `backend/security/jwt_manager.py` y `backend/middleware/rate_limit_middleware.py`.
- Mover el contador de intentos a BD/Redis y añadir bloqueo por `usuario`.

### Paso 7 — Login y cambio de contraseña

- En `backend/services/auth_service.py` setear `ultimo_login = datetime.now(timezone.utc)` al loguear.
- En el update de usuario (`backend/services/usuarios_service.py`) setear `ultimo_cambio_password`
  cuando se cambia `password`.

### Paso 8 — Frontend / cliente

- **React**: pantalla "Olvidé mi contraseña" → `forgot-password`; pantalla de reset con el token de la URL.
- **PySide6** (`ventanas/ventana_editar_usuario.py`): reemplazar el reset local por consumo de la API,
  o al menos agregar el campo email y el flujo de recuperación vía API.

### Paso 9 — Configuración y despliegue

En `.env` (producción):

```ini
JWT_SECRET_KEY=<secreto-largo-y-aleatorio>
ALGORITHM=HS256
ENVIRONMENT=production
COOKIE_SECURE=true
SMTP_HOST=...
SMTP_USER=...
SMTP_PASS=...
```

Verificar HTTPS y CORS en `backend/main.py`.

### Paso 10 — Pruebas

- `test_login.py`, `test_api.py`: agregar casos para `forgot`/`reset` (token inválido, expirado,
  reutilizado), bloqueo por intentos, y que `ultimo_login`/`ultimo_cambio_password` se actualicen.

---

## 4. Hoja de ruta sugerida

- **Fase 1 (crítica):** corregir secreto JWT, código muerto y fechas (§2.4). Sin esto el sistema es inseguro aunque se agregue recuperación.
- **Fase 2:** email + `password_reset_tokens` + endpoints + SMTP (§2.1-2.3, Pasos 1-5).
- **Fase 3:** rate limiting compartido + bloqueo por cuenta (§2.4.4-5).
- **Fase 4 (opcional):** normalizar `roles`/`usuarios_roles` y unificar PySide6 sobre la API.
