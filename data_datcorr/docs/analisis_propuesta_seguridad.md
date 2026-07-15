# Análisis de Propuesta — `implem_securyti.md`

## Fortalezas

| Elemento | Por qué es bueno |
|----------|-----------------|
| **Estructura por fases** | Fase 0→5 con dependencias claras. Reduce riesgo de implementar todo junto |
| **Rollback plan por caso** | Cada fase tiene su propio plan de reversión, no un solo comodín |
| **Checklist pre-deploy** | 15 ítems verificables, varios automatizables con script |
| **Fallback body JSON para desktop** | El cliente Python (`core/api_client.py`) no puede enviar cookies HttpOnly automáticamente; tener fallback evita romperlo |
| **Matriz de riesgo** | Buena comunicación con stakeholders |
| **Variables de entorno** | Todo configurable vía `.env` sin tocar código |
| **Caddy como proxy** | Mejor opción para TLS: cero config, cert auto, HSTS en 1 línea |
| **Reuso de infraestructura existente** | La blacklist, rotación y auditoría ya están — tu plan no las duplica |

## Vulnerabilidades / Gaps en la Propuesta

### 1. Hook `useIdleTimeout` — errores de implementación

```javascript
// PROBLEMA 1: clearInterval en vez de clearTimeout
if (timer) clearInterval(timer);  // ❌ timer es un setTimeout, no setInterval

// PROBLEMA 2: timer se cierra en el callback, siempre será el valor inicial
timer = setTimeout(() => {  // ❌ timer se redeclara en cada llamado
    setIdle(true);
    setTimer(null);
}, timeout);

// PROBLEMA 3: No elimina event listeners al desmontar
window.addEventListener('mousemove', resetTimer);
// ❌ Falta el removeEventListener en el cleanup
```

**Corrección**: usar `useRef` para el timer y `clearTimeout`/`addEventListener` con cleanup.

### 2. Inactividad — lado backend incompleto

El middleware asume `rt.last_activity` pero la propuesta no define:

- ❌ Dónde almacenar `last_activity` (¿tabla `refresh_tokens`? ¿tabla nueva `user_sessions`?)
- ❌ Cuándo se actualiza (¿cada request? ¿solo en `/auth/ping`?)
- ❌ La expresión `(now - (rt.last_activity or now))` da **0 segundos** si `last_activity` es `NULL` — el token jamás expiraría por inactividad
- ❌ No hay endpoint `/auth/ping` para que el frontend refresque actividad

**Corrección**: usar `rt.created_at` como fallback en vez de `now`, y proponer campo concreto.

### 3. Cookie Secure en desarrollo local

```python
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
```

El default `"true"` rompe el login en `localhost` porque `Secure` requiere HTTPS. En desarrollo sin HTTPS, la cookie no se setea y el refresh token desaparece.

**Corrección**: default `"false"` o detectar automáticamente si la request es HTTPS.

### 4. Brute force / Rate limiting — ausente

La propuesta cubre autenticación pero no menciona:
- Límite de intentos por IP/usuario en `/auth/login`
- Bloqueo temporal tras N fallos
- Protección contra enumeración de usuarios (devolver mensaje genérico "credenciales inválidas" sin especificar si el usuario existe)

**Agregar** como Fase 0.5.

### 5. Política de contraseñas — ausente

- No hay política de complejidad (longitud, caracteres)
- No hay expiración de contraseña (90 días)
- No hay historial para evitar reuso
- No hay MFA (comprensible para MVP, pero mencionarlo como futuro)

### 6. CSRF Protection

Al mover el refresh token a cookie, la autenticación se vuelve basada en cookies. Sin un token CSRF, un atacante podría usar el refresh cookie para renovar tokens sin que el usuario lo sepa. FastAPI/Starlette tiene `CookieParameters` con `samesite="strict"` que mitiga parcialmente, pero en formularios cross-site sigue siendo un riesgo.

**Mitigación**: agregar `CSRF-TOKEN` header + cookie doble submit, o confiar en `SameSite=Strict`.

### 7. Debug prints — búsqueda insuficiente

El checklist ítem 10: `grep -r "print" backend/` — falso negativo fácil si hay prints con `#` comentados o en cadenas de logging. Sugerir `grep -rn "^[^#]*\bprint\b" backend/` o mejor usar `tokenize`.

### 8. SECRET_KEY hardcodeado — puede haber más lugares

El checklist ítem 4 busca `SECRET_KEY` pero el valor actual es `"DATCORR_SECRET_KEY"`. Si en el refactor se deja un `os.getenv(...)` con ese fallback, el string `"DATCORR_SECRET_KEY"` estaría en el código igual. Mejor buscar la cadena literal `"DATCORR_SECRET_KEY"`.

### 9. Nombre de archivo con typo (`securyti` vs `security`)

No es crítico pero dificulta encontrar el documento por búsqueda.

---

## Mejor forma de implementar

### Orden ajustado (recomendado)

```
Fase 0: .env + variables                    30 min  ← igual
Fase 0.5: Rate limiting + bloqueo           1 h     ← nuevo, previo a exponer auth
Fase 1: SECRET_KEY desde .env              30 min  ← igual
Fase 2: Cookie HttpOnly + interceptor       3 h     ← incluir CSRF
Fase 3: Inactividad (backend + frontend)    4 h     ← corregir bugs del hook
Fase 4: HTTPS + reverse proxy               1 h     ← igual
Fase 5: QA final + checklist                1 h     ← igual
```

### Errata corregida — `useIdleTimeout.js`

```javascript
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../auth/authStore";

export function useIdleTimeout(timeout = 15 * 60 * 1000) {
    const timerRef = useRef(null);
    const navigate = useNavigate();
    const logout = useAuthStore((s) => s.logout);

    useEffect(() => {
        const reset = () => {
            if (timerRef.current) clearTimeout(timerRef.current);
            timerRef.current = setTimeout(() => {
                logout();
                navigate("/login", { state: { msg: "Sesión expirada por inactividad" } });
            }, timeout);
        };
        const events = ["mousemove", "keydown", "click", "scroll", "touchstart"];
        events.forEach((e) => window.addEventListener(e, reset));
        reset();
        return () => {
            events.forEach((e) => window.removeEventListener(e, reset));
            if (timerRef.current) clearTimeout(timerRef.current);
        };
    }, [timeout, logout, navigate]);
}
```

### Variable `last_activity` — propuesta concreta

**Dónde**: agregar columna en tabla `refresh_tokens`:

```python
last_activity = Column(DateTime, nullable=True)  # default None
last_ip = Column(String, nullable=True)           # tracking opcional
```

**Cuándo actualizar**: en el middleware JWT (cada request autenticado) mediante UPDATE asíncrono o en endpoint `/auth/ping` que el frontend llame cada 5 min.

**Cálculo correcto de expiración**:

```python
ultima_actividad = rt.last_activity or rt.created_at
if (datetime.utcnow() - ultima_actividad).total_seconds() > INACTIVITY_MINUTES * 60:
    # expirar sesión
```

---

## Veredicto Final

| Aspecto | Calificación |
|---------|-------------|
| **Cobertura** | 8/10 — Falta rate limiting, CSRF, política de passwords |
| **Precisión técnica** | 7/10 — Hook con bugs, cookie Secure en dev roto, inactividad incompleto |
| **Mantenibilidad** | 9/10 — Variables de entorno, fases separadas, rollback plan |
| **Compatibilidad** | 9/10 — Fallback body JSON para desktop bien pensado |
| **Documentación** | 9/10 — Checklist, matriz, faseado, todo en un archivo |

**Conclusión**: La propuesta es sólida y bien estructurada. Con las correcciones de implementación (hook, `last_activity`, default `COOKIE_SECURE`, rate limiting) y agregando CSRF + política de contraseñas como items identificados, es un plan completo y ejecutable.
