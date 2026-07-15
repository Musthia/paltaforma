# Plan de Remediación — Seguridad

Basado en auditoría del 2026-07-13. Prioridad: **Crítico → Alto → Medio**.

---

## 1. HTTPS (Crítico — Producción)

**Gap**: Todo el tráfico viaja en HTTP plano. Frontend conecta a `http://127.0.0.1:8000`, CORS solo permite `http://`.

### Remedio recomendado (producción)

```
Cliente → HTTPS → Reverse Proxy (nginx/Caddy) → HTTP → FastAPI :8000
```

| Paso | Acción | Archivos |
|------|--------|----------|
| 1.1 | Configurar Caddy o nginx como reverse proxy con TLS (Let's Encrypt auto) | `Caddyfile` o `nginx.conf` nuevo |
| 1.2 | Cambiar `axiosClient.js` baseURL a `https://dominio.com/api` | `frontend/src/api/axiosClient.js:5` |
| 1.3 | Actualizar CORS origins en `main.py` a `https://dominio.com` | `backend/main.py:35-43` |
| 1.4 | Agregar `Strict-Transport-Security` header en el proxy | Config. del proxy |
| 1.5 | Opcional: `uvicorn --ssl-certfile --ssl-keyfile` para dev con TLS | Script de inicio |

**Esfuerzo**: ~1 h (con Caddy es ~10 líneas de config).

---

## 2. Refresh Token en Cookie HttpOnly (Alto)

**Gap**: El refresh token se almacena en `sessionStorage` y se envía en body JSON, expuesto a XSS.

### Remedio

| Paso | Acción | Archivos |
|------|--------|----------|
| 2.1 | Backend: en el endpoint `/auth/login`, agregar `Set-Cookie` con `HttpOnly; Secure; SameSite=Strict; Path=/api/auth` | `backend/routers/auth_router.py` (~linea 190) |
| 2.2 | Backend: en el endpoint `/usuarios/refresh`, leer refresh token desde cookie en vez de body | `backend/routers/usuarios_router.py:466` |
| 2.3 | Backend: en el endpoint `/auth/logout`, enviar `Set-Cookie` con max-age=0 para eliminar la cookie | `backend/services/auth_service.py` (~linea 530) |
| 2.4 | Frontend: eliminar `sessionStorage` para refresh token, dejarlo solo en cookie | `frontend/src/auth/authStore.js:18` |
| 2.5 | Frontend: en `axiosClient.js`, remover envío manual de refresh_token del body | `frontend/src/api/axiosClient.js:13` |
| 2.6 | Agregar interceptor 401 en `axiosClient.js` que llame al endpoint refresh (con cookie se envía automática) | `frontend/src/api/axiosClient.js` |

**Esfuerzo**: ~3 h.

---

## 3. Expiración por Inactividad (Alto)

**Gap**: No hay timeout de idle. La sesión dura hasta que el Access Token expire (60 min desde emisión), sin importar si el usuario está activo.

### Remedio — Frontend

| Paso | Acción | Archivos |
|------|--------|----------|
| 3.1 | Crear hook `useIdleTimeout` que escuche `mousemove`, `keydown`, `click`, `scroll` y reseteé un timer | `frontend/src/hooks/useIdleTimeout.js` (nuevo) |
| 3.2 | Configurar timeout a 15 min (o configurable vía variable de entorno) | Hook |
| 3.3 | Al expirar, llamar `/auth/logout` y redirigir a `/login` con mensaje "Sesión expirada por inactividad" | Hook |
| 3.4 | Integrar el hook en `DashboardLayout.jsx` o `AppRouter.jsx` (nivel superior) | Layout/Router |

### Remedio — Backend (profundización)

| Paso | Acción | Archivos |
|------|--------|----------|
| 3.5 | Agregar campo `last_activity` en tabla `usuarios` o en tabla de sesiones | `database/modelos.py` |
| 3.6 | Endpoint `/auth/ping` que actualice `last_activity` | `backend/routers/auth_router.py` |
| 3.7 | Middleware opcional que verifique inactividad > N min para rutas sensibles | `backend/middleware/` |

**Esfuerzo**: ~2 h (frontend) + 2 h (backend) = 4 h total.

---

## 4. Access Token de corta duración (Medio)

**Gap**: `ACCESS_TOKEN_EXPIRE_MINUTES = 60` es alto para práctica recomendada (ideal 5-15 min). Además SECRET_KEY hardcodeado.

### Remedio

| Paso | Acción | Archivos |
|------|--------|----------|
| 4.1 | Reducir a 15 minutos | `backend/security/jwt_manager.py:27` |
| 4.2 | Leer `ACCESS_TOKEN_EXPIRE_MINUTES` desde `.env` con fallback a 15 | `jwt_manager.py` |
| 4.3 | Leer `SECRET_KEY` desde `.env` y eliminar hardcodeo | `jwt_manager.py:24` |
| 4.4 | Establecer `SECRET_KEY` real en `.env` (generar con `openssl rand -hex 32`) | `.env:7` |
| 4.5 | Agregar variable de entorno para `REFRESH_TOKEN_EXPIRE_DAYS` | `jwt_manager.py:29` + `.env` |

**Esfuerzo**: ~30 min.

---

## 5. HTTPS + Reverse Proxy (Crítico — Producción)

**Gap**: Todo el tráfico en HTTP plano. Frontend conecta a `http://127.0.0.1:8000`.

### Despliegue con Caddy (recomendado)

```
# 1. Instalar Caddy (Windows: scoop install caddy, Linux: apt install caddy)
# 2. Crear Caddyfile:

midominio.com {
    reverse_proxy localhost:8000
    tls {
        dns cloudflare {env.CF_API_TOKEN}  # opcional: DNS-01 challenge
    }
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
    }
}

# 3. Configurar DNS apuntando al servidor
# 4. Iniciar: caddy run
```

### Cambios en el código para producción

| Archivo | Cambio |
|---------|--------|
| `frontend/src/api/axiosClient.js:5` | `baseURL: "https://midominio.com"` |
| `backend/main.py:35-43` | `allow_origins=["https://midominio.com"]` |
| `.env` | `COOKIE_SECURE=true` |
| `.env` | `ENVIRONMENT=production` |

### Sin dominio público (intranet/IP directa)

Usar **autocert** de Caddy con DNS challenge, o **nginx + self-signed** + confiar el certificado en cada cliente.

---

## Prioridad de Ejecución

```
Fase 0 (inmediata — 30 min) ✓
  └── .env + variables + SECRET_KEY desde .env

Fase 0.5 (1 h) ✓
  └── Rate limiting (5 intentos / 5 min)

Fase 2 (3 h) ✓
  └── Cookie HttpOnly para refresh token

Fase 3 (4 h) ✓
  └── Expiración por inactividad (30 min backend + 15 min frontend)

Fase 4 (producción — 1 h)
  └── HTTPS + reverse proxy (ver instrucciones abajo)
```

---

## Pruebas después de cada fase

| Fase | Prueba |
|------|--------|
| 1 | `pytest` + verificar que login/token refresh sigan funcionando |
| 2 | Verificar cookie `HttpOnly` en DevTools > Application > Cookies. Refresh sin enviar body. |
| 3 | Esperar N minutos sin tocar → verify redirect a login con mensaje |
| 4 | `curl -v https://dominio.com` → verificar TLS + HSTS + redirect HTTP → HTTPS |
