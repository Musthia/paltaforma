
OBJETIVO DEL PLAN
Aplicar todas las brechas de seguridad identificadas en la auditoría del 2026-07-13:

Brecha	Prioridad	Impacto
HTTPS (TLS)	Crítico	Todo el tráfico expuesto
SECRET_KEY hardcodeado	Crítico	Compromiso de firma JWT
Refresh Token en sessionStorage	Alto	Vulnerable a XSS
Inactividad sin timeout	Alto	Sesiones persistentes no vigentes
Access Token 60 min	Medio	Duración óptima 15 min
Debug prints en producción	Bajo	Información sensible en logs
🏆 MEJORES PRÁCTICAS CONSOLIDADAS

1. HTTPS + Reverse Proxy (Crítico)
   Mejor Práctica	Justificación
   HTTPS en todos los endpoints	Evita interceptación de tráfico en red
   Reverse Proxy (Caddy/nginx)	Manejo centralizado de TLS, HSTS, certificaciones
   Let's Encrypt automático	Certificados gratuitos, auto-renovables
   HSTS header	Fuerza HTTPS en todas las conexiones futuras
   CORS configurado para HTTPS	Evita ataques de man-in-the-middle
   yaml

# Caddyfile (ejemplo)

dominio.com {
    reverse_proxy api:8000
    tls {
        automation
    }
    responses {
        headers {
            Strict-Transport-Security "max-age=31536000; includeSubDomains"
        }
    }
}
2. SECRET_KEY desde Entorno (Crítico)
Mejor Práctica	Justificación
Leer de .env	No hardcodear secretos en repositorio
Fallback solo en dev	Evita fallos en producción
Generar con openssl	Aleatoriedad criptográfica
Rotar en mantenimiento	Evita invalidación masiva de tokens
python

# backend/security/jwt_manager.py

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "DATCORR_SECRET_KEY")  # fallback dev
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
INACTIVITY_MINUTES = int(os.getenv("INACTIVITY_MINUTES", "30"))
bash

# Generar SECRET_KEY seguro

openssl rand -hex 32

# Copiar a .env: JWT_SECRET_KEY=<valor></valor>

3. Refresh Token en Cookie HttpOnly (Alto)
   Mejor Práctica	Justificación
   HttpOnly + Secure + SameSite=Strict	Protege de XSS, requiere HTTPS, bloquea navegadores
   Fallback al body JSON	Compatibilidad con cliente desktop
   Re-emitir en cada refresh	Rotación automática del token
   Eliminar en logout	Revocación inmediata de credenciales
   python

# backend/security/jwt_manager.py

def set_refresh_cookie(response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
        path="/api/auth",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

def clear_refresh_cookie(response):
    response.delete_cookie("refresh_token", path="/api/auth")
javascript

// frontend/src/auth/authStore.js
setTokens: (access, refresh) => {
    sessionStorage.setItem("access_token", access);
    // refresh_token vive en cookie HttpOnly: no se guarda en JS
    set({ accessToken: access, refreshToken: null, user: decodeToken(access) });
}
4. Expiración por Inactividad (Alto)
Mejor Práctica	Justificación
Sliding timer	Reinicia al hacer actividad
Backend + Frontend	Verificación doble en todos los endpoints
Registro de auditoría	Rastreo de expiraciones
Configurable vía .env	Ajuste según requerimientos
python

# backend/middleware/jwt_middleware.py

if (now - (rt.last_activity or now)).total_seconds() > INACTIVITY_MINUTES * 60:
    rt.revoked = True
    db.commit()
    registrar_auditoria(db=db, usuario=usuario, accion="SESSION_EXPIRED_INACTIVITY")
    return JSONResponse(status_code=401, content={"detail": "Sesión expirada por inactividad."})
javascript

// frontend/src/hooks/useIdleTimeout.js
const useIdleTimeout = (timeout = 15 * 60000) => {
    const [idle, setIdle] = useState(false);
    const [timer, setTimer] = useState(null);

    useEffect(() => {
        const resetTimer = () => {
            if (timer) clearInterval(timer);
            setIdle(false);
            timer = setTimeout(() => {
                setIdle(true);
                setTimer(null);
            }, timeout);
        };

    window.addEventListener('mousemove', resetTimer);
        window.addEventListener('keydown', resetTimer);
        window.addEventListener('click', resetTimer);
        window.addEventListener('scroll', resetTimer);

    return () => {
            if (timer) clearTimeout(timer);
        };
    }, [timeout]);

    return idle;
};
5. Access Token + Duración (Medio)
Mejor Práctica	Justificación
15 min máximo	Balance entre seguridad y UX
Rotación automática	Reduce ventana de exposición
JTI único	Vincula access ↔ refresh para auditoría
Blacklist en logout	Revocación inmediata
python

# backend/security/jwt_manager.py

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
6. QA + Rollback (Medio)
Mejor Práctica	Justificación
Checklist pre-merge	Verificación exhaustiva antes de desplegar
Rollback plan	Recuperación rápida en caso de fallo
Testeo desktop + navegador	Ambas plataformas deben funcionar
Logs sin debug	Evitar información sensible en logs
📅 ESTRATEGIA DE IMPLEMENTACIÓN (Fase por Fase)
text

┌─────────────────────────────────────────────────────────────────┐
│                    FASE 0 — PREPARACIÓN                         │
│  ~30 min | Riesgo: Bajo                                        │
│  ───────────────────────────────────────────────────────────   │
│  • Crear .env con JWT_SECRET_KEY (generado con openssl)         │
│  • Configurar COOKIE_SECURE=true, ENVIRONMENT=production        │
│  • Eliminar print de debug en producción                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FASE 1 — SECRET_KEY + LIMPIEZA               │
│  ~30 min | Riesgo: Crítico (tokens invalidados)                 │
│  ───────────────────────────────────────────────────────────   │
│  • Leer SECRET_KEY de .env en jwt_manager.py                    │
│  • Eliminar fallback dev si no es necesario                     │
│  • Rotar SECRET_KEY en ventana de mantenimiento                 │
│  • Testear login/logout con nuevos tokens                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FASE 2 — COOKIE HttpOnly + Fallback           │
│  ~3 h | Riesgo: Bajo (compatibilidad total)                    │
│  ───────────────────────────────────────────────────────────   │
│  • Backend: set_refresh_cookie() en login/refresh/logout        │
│  • Backend: clear_refresh_cookie() en logout                    │
│  • Frontend: eliminar refresh_token de sessionStorage            │
│  • Backend: fallback al body JSON para desktop                   │
│  • Testeo: Login navegador, Refresh sin body, Logout            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FASE 3 — EXPIRACIÓN POR INACTIVIDAD           │
│  ~4 h | Riesgo: Medio (afecta UX si no testear)                 │
│  ───────────────────────────────────────────────────────────   │
│  • DB: agregar last_activity, access_jti a refresh_tokens        │
│  • Backend: registrar en login/refresh                          │
│  • Backend: middleware verifica timeout                         │
│  • Frontend: useIdleTimeout hook                                │
│  • Testeo: esperar timeout, verificar 401 y redirección         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FASE 4 — HTTPS + REVERSE PROXY               │
│  ~1 h | Riesgo: Bajo (requiere infraestructura)                 │
│  ───────────────────────────────────────────────────────────   │
│  • Configurar Caddy/nginx con TLS (Let's Encrypt)               │
│  • Redirigir HTTP→HTTPS                                         │
│  • Agregar HSTS header                                          │
│  • Configurar CORS para HTTPS                                   │
│  • Testeo: curl https://dominio.com, verificar TLS              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FASE 5 — QA FINAL + ROLBACK                  │
│  ~1 h | Riesgo: Bajo                                           │
│  ───────────────────────────────────────────────────────────   │
│  • Checklist completo (verificar en documento siguiente)        │
│  • Monitoreo de logs durante 24h                                │
│  • Plan de rollback definido                                    │
└─────────────────────────────────────────────────────────────────┘
📋 CHECKLIST DE VERIFICACIÓN (Pre-Deploy)

# Verificación	Estado	Comprobar

1	HTTPS activo en producción	✅	curl -I https://dominio.com
2	HSTS header presente	✅	Strict-Transport-Security
3	SECRET_KEY en .env	✅	cat .env
4	JWT_SECRET_KEY no hardcodeado	✅	grep -r "SECRET_KEY" backend/
5	Refresh token en cookie HttpOnly	✅	DevTools > Application > Cookies
6	Cookie con SameSite=Strict	✅	DevTools > Application > Cookies
7	Logout elimina cookie	✅	DevTools > Application > Cookies (después)
8	Inactividad expira sesión	✅	Esperar timeout + request
9	Desktop sigue funcionando	✅	core/api_client.py con body JSON
10	Sin debug prints en producción	✅	grep -r "print" backend/
11	Tokens rotan correctamente	✅	Refresh token cambia cada uso
12	Blacklist en logout	✅	Access token invalidado
13	Auditoría registrada	✅	Logs de sesión expirada
14	CORS configurado para HTTPS	✅	DevTools > Network > CORS
15	Rollback disponible	✅	Script de revert de cambios
🔄 ESTRATEGIA DE ROLBACK
Caso: Fallo en Fase 1 (SECRET_KEY)
bash

# Rotar SECRET_KEY inválido

# Solución: revertir a valor anterior

echo "JWT_SECRET_KEY=<valor_anterior>" > .env

# Reiniciar servicio

Caso: Fallo en Fase 2 (Cookie HttpOnly)
python

# Desactivar set_refresh_cookie

# Revertir login/routers a no enviar cookie

# Desktop sigue funcionando con body JSON

Caso: Fallo en Fase 3 (Inactividad)
python

# Desactivar middleware de timeout

# Revertir a verificar solo blacklist

📊 MATRIZ DE RIESGO
Fase	Riesgo	Mitigación	Compatibilidad
0	Bajo	Fallback dev	Total
1	Crítico	Rotar en mantenimiento	Total
2	Bajo	Fallback body JSON	Total
3	Medio	Testeo exhaustivo	Total
4	Bajo	HTTPS solo en producción	Total
5	Bajo	Checklist + monitoreo	Total
🎯 RECOMENDACIÓN FINAL
Orden de Ejecución:

text

1. Fase 0 (Preparación) → .env, variables
2. Fase 1 (SECRET_KEY) → Crítico, rotar en mantenimiento
3. Fase 2 (Cookie HttpOnly) → Alto, compatible con desktop
4. Fase 3 (Inactividad) → Alto, testear UX
5. Fase 4 (HTTPS) → Crítico, infraestructura
6. Fase 5 (QA) → Verificar checklist + monitoreo 24h
   Tiempo Total Estimado: ~8-10 horas
   Riesgo Total: Bajo (con mitigaciones en cada fase)
   Impacto Negativo: Mínimo (compatibilidad total con desktop + navegador)

📝 ARCHIVO DE REFERENCIA
Este archivo debe ser:

✅ Documentado en repositorio para equipo
✅ Aprobado por security lead antes de desplegar
✅ Monitoreado durante 24-48h después de deploy
✅ Actualizado si se detectan cambios en la auditoría
