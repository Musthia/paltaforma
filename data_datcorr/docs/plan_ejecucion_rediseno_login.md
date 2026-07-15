# Plan de Ejecución: Rediseño Login "Transparencia Institucional"

> Basado en `docs/login_securyti_02.md`, `docs/revision_login_rediseno.md` y estado actual del código.

---

## Estado real de las fallas

### Ya remediadas (infraestructura/backend, no tocaron Login.jsx)

| # | Problema | Severidad | Dónde se corrigió |
|---|----------|-----------|-------------------|
| A | Access Token 60 min → 15 min | Alta | `jwt_manager.py:52` via `.env:ACCESS_TOKEN_EXPIRE_MINUTES=15` |
| B | Refresh Token en `sessionStorage` → cookie HttpOnly | Alta | `authStore.js` (ya no guarda refresh_token) + `jwt_manager.py:set_refresh_cookie()` |
| C | Sin rate limiting en login | Media | `rate_limit_middleware.py` (5 intentos / 5 min) |
| D | Sin expiración por inactividad | Media | `jwt_middleware.py:136-149` (30 min backend) + `useIdleTimeout.js` (15 min frontend) |
| E | `SECRET_KEY` hardcodeado | Alta | `jwt_manager.py` lee de `.env` |
| F | `print()` de debug en endpoints | Baja | Eliminados de `auth_router.py` y `jwt_manager.py` |

### Pendientes en Login.jsx (ninguna tocada por Fases 0–3)

| # | Problema | Severidad | Línea actual |
|---|----------|-----------|-------------|
| 1 | Sin `try/catch` en `handleLogin` → crashea en blanco si falla API | **Media-Alta** | `Login.jsx:14-27` |
| 2 | Sin estado `loading` / botón siempre habilitado → doble envío | Media | `Login.jsx:44-46` |
| 3 | Access token en `sessionStorage` → vulnerable a XSS | **Alta** | `authStore.js:15` (mitigado parcialmente por refresh token en cookie + access token 15 min) |
| 4 | Inputs sin `id`/`htmlFor`/`autoComplete` → sin autofill ni accesibilidad | Baja | `Login.jsx:36-42` |
| 5 | Sin mensaje de error al usuario → falla silenciosa | Baja | `Login.jsx` nunca renderiza `styles.error` |
| 6 | Sin `type="submit"` explícito en botón | Baja | `Login.jsx:44` |

---

## Plan de ejecución

### Fase 0: Hardening de Login.jsx (40 min) — **OBLIGATORIO antes del rediseño**

| Paso | Acción | Archivo |
|------|--------|---------|
| 0.1 | Envolver `api.post` en `try/catch/finally`, mostrar error genérico "Usuario o contraseña incorrectos." (anti-enumeración) | `Login.jsx:14-27` |
| 0.2 | Agregar estado `loading`, deshabilitar botón con `disabled={loading}`, texto "Ingresando…" | `Login.jsx` |
| 0.3 | Agregar `id`, `name`, `htmlFor` en labels, `autoComplete="username"` / `"current-password"` en inputs | `Login.jsx:36-42` |
| 0.4 | Agregar renderizado condicional de error `<div style={styles.error}>` | `Login.jsx` |
| 0.5 | Agregar `type="submit"` al botón | `Login.jsx:44` |
| 0.6 | Verificar que `setTokens(data.token)` ya no recibe `refresh_token` (backend no lo devuelve en body post-Fase2) | `Login.jsx:24` |
| 0.7 | **Build + test**: `npm run build`, login correcto, login fallido, botón deshabilitado durante envío | — |

### Fase 1: Assets visuales (30 min)

| Paso | Acción |
|------|--------|
| 1.1 | Descargar imagen Unsplash como `bg.webp` y `bg.jpg` a `frontend/public/images/login/` |
| 1.2 | Optimizar < 300 KB con `sharp` o similar |
| 1.3 | Eliminar cualquier URL de Unsplash del código fuente |

### Fase 2: CSS glassmorphism (20 min)

| Paso | Acción |
|------|--------|
| 2.1 | Crear `frontend/src/pages/Login.css` con §7.2 de `revision_login_rediseno.md` (texto **claro** `#f1f5f9` sobre vidrio oscuro — contraste corregido) |
| 2.2 | Verificar `prefers-reduced-motion: reduce` desactiva `slowZoom` |
| 2.3 | Medir contraste con herramienta (texto ≥ 4.5:1 sobre fondo) |

### Fase 3: Login.jsx rediseñado (20 min)

| Paso | Acción |
|------|--------|
| 3.1 | Integrar clases CSS del nuevo `Login.css` en `Login.jsx` (reemplazar `styles` objeto inline) |
| 3.2 | Trust footer: "Conexión cifrada (TLS)" + "Datos protegidos" (sin ISO/RGPD falsos) |
| 3.3 | Mantener todo el hardening de Fase 0 (try/catch, loading, labels, autocomplete, error) |

### Fase 4: QA final (20 min)

| Paso | Acción |
|------|--------|
| 4.1 | `npm run build` sin errores |
| 4.2 | Login correcto → redirige a `/dashboard` |
| 4.3 | Login incorrecto → muestra error, NO crashea |
| 4.4 | Botón deshabilitado durante envío, texto "Ingresando…" |
| 4.5 | Autocomplete funciona (navegador ofrece guardar/rellenar) |
| 4.6 | Probar en Chrome + Firefox + Edge |
| 4.7 | Contraste verificado con herramienta |

---

## Resumen de esfuerzo

| Fase | Tiempo |
|------|--------|
| Fase 0: Hardening Login.jsx | 40 min |
| Fase 1: Assets | 30 min |
| Fase 2: CSS | 20 min |
| Fase 3: Login.jsx rediseño | 20 min |
| Fase 4: QA | 20 min |
| **Total** | **~2 h 10 min** |

## Nota sobre Access Token en sessionStorage (#3)

Es la única falla **Alta** que no se puede eliminar por completo sin un refactor mayor del esquema de autenticación. Está **mitigada** por:
- Refresh token en cookie HttpOnly (inaccesible desde JS)
- Access token con expiración corta (15 min)
- Rate limiting en login (5 intentos/5 min)

Para eliminarla completamente haría falta migrar a un esquema donde el access token se envíe en cookie HttpOnly + cabecera personalizada (`X-Auth-Token`). Esto es un **breaking change** que requiere refactor de todo el frontend. Se recomienda evaluar en una iteración futura si el riesgo XSS lo justifica.
