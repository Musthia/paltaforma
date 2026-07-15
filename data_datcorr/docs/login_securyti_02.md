
Las fallas de seguridad graves NO están remediadas. El código actual de Login.jsx y authStore.js sigue teniendo vulnerabilidades que impiden ejecutar el plan de rediseño de forma segura:

Fallas graves pendientes (no remediadas)

# Falta	Severidad	Evidencia en código actual

1	Sin try/catch en handleLogin	Media-Alta	Login.jsx:14-27 — si api.post falla (401, 500, red), la app crashea en blanco
2	Sin estado de carga / botón no deshabilita	Media	No existe loading; el <button></button> siempre está habilitado, permitiendo doble envío
3	Access token en sessionStorage	Alta	authStore.js:15 — vulnerable a XSS; cualquier script inyectado roba el token
4	Inputs sin id, htmlFor, autoComplete	Baja	Login.jsx:36-42 — sin labels accesibles ni autocomplete para gestores de contraseña
5	Sin mensaje de error al usuario	Baja	No hay estado error ni renderizado de mensaje; falla silenciosa
¿Por qué no se puede ejecutar el plan actual?
El plan_ejecucion_rediseno_login.md asume en su encabezado que las Fases 0–3 previas ya corrigieron estas fallas, pero contrastando el código real, siguen presentes. Si se ejecuta el rediseño visual (Fases 1–4 del plan) sin corregirlas, se perpetúan:

Crashes en producción ante fallos de red/auth.
Doble envío de credenciales (riesgo de lockout).
Superficie XSS sobre sessionStorage sin mitigar.
Falta de accesibilidad y usabilidad básica.
Acción requerida antes del rediseño
Ejecutar primero un Fase 0 de hardening del login actual:

Añadir try/catch/finally en handleLogin con mensaje genérico anti-enumeración.
Añadir estado loading y disabled={loading} en el botón.
Añadir id, htmlFor, name, autoComplete en inputs.
Añadir estado error y renderizado de mensaje.
Evaluar mitigación XSS sobre sessionStorage (sanitización, CSP, o migración a cookie HttpOnly + SameSite).
Solo una vez que el Login.jsx base tenga manejo de errores, estados de carga y accesibilidad corregidos, se puede proceder con las Fases 1–4 del plan de rediseño visual.
