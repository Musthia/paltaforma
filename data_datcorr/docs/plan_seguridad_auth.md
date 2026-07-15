# Plan de Implementación: Cierre de Brechas de Seguridad en Auth

> Objetivo: aplicar los puntos pendientes de la revisión
> (Refresh Token en cookie `HttpOnly`, expiración por inactividad, HTTPS,
> y el `SECRET_KEY` hardcodeado) **sin romper** lo ya diseñado:
> - `frontend/src/auth/authStore.js` (sessionStorage)
> - `frontend/src/api/axiosClient.js` (Bearer access token)
> - `core/api_client.py` (cliente desktop, refresh en body JSON)
> - Blacklist + rotación de refresh ya existentes

Principio rector: **agregar capas, no reemplazarlas**. El refresh token
seguirá viajando en el body JSON (para el cliente desktop), y *adicionalmente*
se emitirá en cookie `HttpOnly` para el navegador. El backend acepta ambos.

---

## Fase 0 — Pre-requisitos (infraestructura)

1. **Variables de entorno** (crear `.env` / config del contenedor):
   ```
   JWT_SECRET_KEY=<secreto aleatorio >=32 bytes>
   COOKIE_SECURE=true          # false solo en dev http local
   ENVIRONMENT=production
   ```
2. **HTTPS** en producción delante de la API (reverse proxy / load balancer).
   La cookie `Secure` y HSTS solo funcionan sobre TLS. Sin esto, la Fase 2
   debe usar `COOKIE_SECURE=false` temporalmente.

---

## Fase 1 — `SECRET_KEY` desde entorno + limpiar debug  (riesgo: Crítico)

**No rompe nada.** Solo cambia el origen del secreto.

`backend/security/jwt_manager.py`:
```python
import os
from datetime import datetime, timezone, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "DATCORR_SECRET_KEY")  # fallback solo dev
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
INACTIVITY_MINUTES = int(os.getenv("INACTIVITY_MINUTES", "30"))
```

`backend/security/jwt_manager.py` — eliminar los `print` de producción
(líneas 321, 324, 330):
```python
def verificar_refresh_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
```

> ⚠️ Al rotar `SECRET_KEY` en producción, **todos los tokens vigentes se
> invalidan** (los emitidos con la key vieja fallan la firma). Hacerlo en
> ventana de mantenimiento o con blue/green.

---

## Fase 2 — Refresh Token en cookie `HttpOnly` + `SameSite=strict`

### 2.1 Backend: helper de cookie (nuevo, reutilizable)
Agregar al final de `backend/security/jwt_manager.py`:
```python
def set_refresh_cookie(response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
        path="/usuarios/refresh",          # solo viaja al endpoint de refresh
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

def clear_refresh_cookie(response):
    response.delete_cookie("refresh_token", path="/usuarios/refresh")
```

### 2.2 Login — emitir cookie SIN quitar el body
`backend/routers/auth_router.py` (función `login`):
```python
from fastapi import Response
# ...
def login(
    request: Request,
    datos: LoginRequest,
    response: Response,                       # ← nuevo
    db: Session = Depends(get_db)
):
    ...
    set_refresh_cookie(response, resultado["refresh_token"])  # ← nuevo
    return LoginResponse(
        success=True,
        mensaje=resultado["mensaje"],
        usuario=resultado["usuario"],
        token=resultado["token"],
        refresh_token=resultado["refresh_token"],   # ← se mantiene (desktop)
    )
```
✅ El frontend sigue guardando en sessionStorage y el desktop sigue
funcionando con el body. El navegador además recibe la cookie.

### 2.3 Refresh — leer cookie, con fallback al body (desktop)
`backend/routers/usuarios_router.py` (función `refresh_token`):
```python
from fastapi import Request, Response
# ...
def refresh_token(
    datos: RefreshRequest,
    request: Request,                          # ← nuevo
    response: Response,                        # ← nuevo
    db: Session = Depends(get_db)
):
    # Navegador: cookie HttpOnly. Desktop: body JSON. Ambos válidos.
    refresh_token_value = request.cookies.get("refresh_token") or datos.refresh_token

    resultado = refresh_access_token(db=db, refresh_token=refresh_token_value)
    if not resultado["success"]:
        raise HTTPException(status_code=401, detail=resultado["mensaje"])

    set_refresh_cookie(response, resultado["refresh_token"])   # ← re-emite rotada
    return RefreshResponse(
        success=True,
        access_token=resultado["access_token"],
        refresh_token=resultado["refresh_token"],             # ← se mantiene (desktop)
    )
```

### 2.4 Logout — revocar cookie
`backend/routers/auth_router.py` (función `logout`):
```python
def logout(
    datos: LogoutRequest,
    request: Request,                          # ← nuevo
    response: Response,                        # ← nuevo
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    refresh_value = request.cookies.get("refresh_token") or datos.refresh_token
    resultado = logout_usuario(db=db, refresh_token=refresh_value)
    if not resultado["success"]:
        raise HTTPException(status_code=401, detail=resultado["mensaje"])

    clear_refresh_cookie(response)             # ← nuevo
    # ...blacklist del access token (ya existente)...
```

### 2.5 Frontend — dejar de tocar el refresh token en JS
`frontend/src/auth/authStore.js`: el refresh token de la cookie ya no necesita
guardarse en `sessionStorage`. Se puede seguir guardando el `accessToken` (lo
usa `axiosClient` para el Bearer), pero **eliminar** `refreshToken` de
sessionStorage para reducir superficie XSS:
```js
setTokens: (access, refresh) => {
    sessionStorage.setItem("access_token", access);
    // refresh_token vive en cookie HttpOnly: no se guarda en JS
    set({ accessToken: access, refreshToken: null, user: decodeToken(access) });
},
logout: () => {
    sessionStorage.removeItem("access_token");
    set({ accessToken: null, refreshToken: null, user: null });
}
```
El interceptor de refresh (en `core/api_client.py` / axios) ya envía el body;
para el navegador, el body puede omitirse porque la cookie viaja sola. Mantener
el body en `false`/vacío es seguro: el backend usa cookie o body.

> Nota: el middleware tiene `/auth/refresh` en `public_paths` pero la ruta real
> es `/usuarios/refresh`. Se recomienda corregir `public_paths` a
> `"/usuarios/refresh"` para coherencia (sin impacto funcional hoy).

---

## Fase 3 — Expiración automática por inactividad

La sesión se considera inactiva si pasan `INACTIVITY_MINUTES` sin requests
autenticados. Se implementa con la tabla `refresh_tokens` ya existente.

### 3.1 Modelo: nuevas columnas
`database/modelos_refresh.py`:
```python
from datetime import datetime

last_activity = Column(TIMESTAMP, nullable=True)
access_jti = Column(String(255), nullable=True)   # vincula access ↔ refresh
```

Migración (según tu motor; ejemplo PostgreSQL):
```sql
ALTER TABLE refresh_tokens
    ADD COLUMN last_activity TIMESTAMP,
    ADD COLUMN access_jti VARCHAR(255);
```

### 3.2 Login/Refresh: registrar `access_jti` y `last_activity`
En `auth_service.py`, al crear cada `RefreshToken`:
```python
nuevo_refresh = RefreshToken(
    usuario_id=usuario_db.id,
    token_jti=resultado_refresh["jti"],
    refresh_token=resultado_refresh["refresh_token"],
    access_jti=resultado_token["jti"],          # ← nuevo
    revoked=False,
    last_activity=datetime.now(timezone.utc),    # ← nuevo
    expires_at=resultado_refresh["expires_at"],
)
```
Aplicar igual en `refresh_access_token` (nuevo refresh) usando el
`nuevo_access["jti"]`.

### 3.3 Middleware: aplicar timeout (sliding)
En `backend/middleware/jwt_middleware.py`, tras decodificar y antes de
`request.state.user`, inyectar la verificación:
```python
from datetime import datetime, timezone, timedelta
from database.modelos_refresh import RefreshToken

# ...dentro del bloque DB, tras validar blacklist...
access_jti = payload.get("jti")
if access_jti:
    rt = db.query(RefreshToken).filter(
        RefreshToken.access_jti == access_jti
    ).first()

    if rt and (rt.revoked or rt.access_jti is None):
        return JSONResponse(status_code=401, content={"detail": "Sesión cerrada."})

    if rt:
        now = datetime.now(timezone.utc)
        # throttle: solo escribir si pasó > 60s desde last_activity
        if (now - (rt.last_activity or now)).total_seconds() > 60:
            rt.last_activity = now
            db.commit()
        if (now - (rt.last_activity or now)).total_seconds() > INACTIVITY_MINUTES * 60:
            rt.revoked = True
            db.commit()
            registrar_auditoria(db=db, usuario=usuario, accion="SESSION_EXPIRED_INACTIVITY",
                                tabla="auth", detalle="Sesión expirada por inactividad")
            return JSONResponse(status_code=401,
                                content={"detail": "Sesión expirada por inactividad."})
```
✅ El access token sigue expirando a los 60 min; la inactividad corta la
sesión antes si el usuario se queda quieto. El cliente desktop también se ve
afectado (comportamiento deseado de seguridad).

---

## Fase 4 — HTTPS (despliegue)

- Terminar TLS en el reverse proxy (nginx/Caddy/Traefik) o en el balanceador.
- Redirigir HTTP→HTTPS.
- Cabeceras: `Strict-Transport-Security: max-age=31536000; includeSubDomains`.
- `COOKIE_SECURE=true` (Fase 0) para que la cookie no viaje por HTTP.
- No exponer `/docs` ni `/openapi.json` en producción.

---

## Fase 5 — QA y Rollback

### Checklist pre-merge
- [ ] Login navegador: cookie `refresh_token` presente, `HttpOnly`, `SameSite=Strict`, `Secure` (en HTTPS).
- [ ] Login desktop (`core/api_client.py`): sigue refrescando vía body JSON.
- [ ] Refresh navegador: funciona sin leer token en JS (usa cookie).
- [ ] Logout: cookie eliminada + access en blacklist.
- [ ] Inactividad: esperar `INACTIVITY_MINUTES` + request → 401 y cierre en frontend.
- [ ] Rotación y reuse-detection siguen funcionando (sin regresión).
- [ ] Sin `print` de debug en logs de producción.
- [ ] `JWT_SECRET_KEY` viene de env, no hardcodeado.

### Rollback
- Fase 1 y 3 son aditivas (columnas nuevas, helper). Si hay fallo, revertir
  los endpoints a no setear cookie / no chequear inactividad; el body JSON
  sigue siendo válido (desktop y frontend no rompen).
- Fase 1 (cambio de `SECRET_KEY`): solo revertir la env var a la anterior
  para no invalidar tokens en vuelo.

---

## Resumen de impacto

| Cambio | Riesgo de rotura | Compatibilidad |
|--------|------------------|----------------|
| `SECRET_KEY` desde env | Bajo (solo si no se setea env) | Total |
| Quitar `print` debug | Nulo | Total |
| Cookie `HttpOnly` (refresh) | Bajo | Desktop vía body; navegador vía cookie |
| Frontend: no guardar refresh en JS | Bajo | Access token en sessionStorage intacto |
| Inactividad (middleware) | Medio | Afecta desktop también (esperado) |
| HTTPS / `Secure` cookie | Bajo (en dev usar `false`) | Requiere proxy TLS |
