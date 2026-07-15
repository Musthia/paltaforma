# Plan de Unificación: Inicio de Servicios, Proyecto Único y Login Unificado DATCORR + SIMCO

**Fecha:** 2026-07-15  
**Alcance:** Unificar el arranque de servicios, fusionar `data_datcorr` y `simco_v01` en una plataforma única, unificar autenticación y presentar SIMCO como módulo anexo de DATCORR accesible desde el dashboard maestro.

---

## 1. Estado actual (diagnóstico)

### 1.1 DATCORR (`C:\plataforma\data_datcorr\`)
- **Backend:** FastAPI en `backend/main.py` (puerto actual no documentado en `.env`, CORS limitado a `localhost:5173` y `127.0.0.1:5173`).
- **Frontend:** React JS/JSX (`frontend/`), Vite en puerto `5173`.
- **Auth propia duplicada:** `backend/routers/auth_router.py` usa `backend/security/jwt_manager`, `backend/services/auth_service` y `database/modelos.py` locales, **aunque** `backend/main.py` también importa `platformcore.routers.auth_router`.
- **Sin script de inicio oficial** en la raíz del proyecto (solo `.env` y archivos Python sueltos).
- **Bases:** `datcorr` (PostgreSQL/SQLite) y `platform` (PostgreSQL).

### 1.2 SIMCO (`C:\plataforma\simco_v01\`)
- **Backend:** FastAPI en `backend/app/main.py` (puerto `8000`), sirve SPA compilada desde `frontend/dist`.
- **Frontend:** React + TypeScript (`frontend/`), Vite en puerto `5173`.
- **Auth:** `backend/app/api/routes/auth.py` usa `app/services/auth_service` y `app/core/jwt` locales, pero `main.py` también monta `platformcore.routers.auth_router`.
- **Scripts de inicio:** `iniciar_simco.bat`, `iniciar_simco_dev.bat`, `iniciar_simco_dev.ps1`, `detener_simco.bat`.
- **Bases:** `simco` (PostgreSQL/SQLite) y `platform` (PostgreSQL).

### 1.3 Plataforma común (`C:\plataforma\platformcore\`)
- **Ya existe** como paquete shared (`pyproject.toml`).
- Provee: `auth`, `users`, `roles`, `permissions`, `audit`, `security`, `jwt`, `config`, `database`.
- **Problema:** Ambas apps tienen su capa de auth/usuarios local duplicada que NO se está usando porque los `main.py` ya montan `platformcore`, pero los routers locales siguen existiendo y pueden causar colisiones.

---

## 2. Objetivos específicos

1. **Unificar el inicio de servicios:** Un solo script/batche que levante el backend unificado, los frontends (si aplica) y verifique dependencias.
2. **Fusionar proyectos:** Convertir `simco_v01` en un módulo dentro de `data_datcorr` (o viceversa), eliminando duplicación de carpetas.
3. **Unificar el login:** Usar exclusivamente `platformcore` como Identity Provider. Eliminar los routers de auth locales de ambos proyectos.
4. **SIMCO como sección de DATCORR:** Desde el dashboard de DATCORR, un botón/enlace que abra SIMCO en **nueva pestaña** del navegador, manteniendo la sesión y aplicando permisos por rol.
5. **Dashboards:** Login landing = Dashboard DATCORR (maestro). SIMCO = dashboard anexo.

---

## 3. Arquitectura objetivo

```
C:\plataforma\
├── data_datcorr/                  # Proyecto unificado (nuevo nombre: plataforma/)
│   ├── backend/
│   │   └── main.py                # API unificada (routers DATCORR + SIMCO)
│   ├── frontend/                  # SPA unificada (React)
│   │   └── src/
│   │       ├── pages/
│   │       │   ├── Login.jsx      # Login único (consumirá /auth/login de platformcore)
│   │       │   ├── Dashboard.jsx  # Dashboard maestro DATCORR
│   │       │   └── SimcoPage.jsx  # Punto de entrada a SIMCO (redirección/embed)
│   │       └── router/
│   │           └── AppRouter.jsx  # Rutas unificadas + protección por permisos
│   ├── simco/                     # Módulo SIMCO (backend lógico)
│   │   ├── routers/               # Routers SIMCO pegados al main unificado
│   │   ├── services/              # Lógica SIMCO
│   │   └── models/                # Modelos SIMCO
│   ├── config/
│   │   └── app_config.py          # Config unificada (puertos, CORS, URLs)
│   ├── .env                       # Variables unificadas
│   ├── iniciar_plataforma.bat     # Script de inicio único
│   └── detener_plataforma.bat
├── platformcore/                  # Sin cambios (núcleo shared)
└── ...
```

**Decisión de frontend:**
- Opción A (recomendada): Mantener dos SPAs (`data_datcorr/frontend` y `simco_v01/frontend`) pero servidas por el mismo backend unificado. El login está en DATCORR. Desde DATCORR, un botón abre `http://localhost:8000/simco` (o la URL de SIMCO) en nueva pestaña. El backend valida el JWT y, si el usuario tiene permiso `simco.access`, sirve el SPA de SIMCO o redirige a ella.
- Opción B: Migrar todo el código de SIMCO al frontend de DATCORR como rutas adicionales. Más integrado, pero implica convertir TS→JS o mantener ambos en el mismo árbol.

**Este plan adopta la Opción A** por menor impacto y respetando la solicitud de "nueva pestaña en el navegador".

---

## 4. Fases de ejecución

### Fase 0 — Unificar el inicio de servicios
**Objetivo:** Un solo punto de arranque para toda la plataforma.

**Acciones:**
1. Crear `data_datcorr/iniciar_plataforma.bat` (y `.ps1`) que:
   - Verifique PostgreSQL en `localhost:5432`.
   - Verifique existencia de venv de DATCORR (`data_datcorr/venv`).
   - Levante el backend unificado con `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`.
   - Opcionalmente, levante el frontend de DATCORR (`npm run dev` en `data_datcorr/frontend`) en puerto `5173`.
   - Si se requiere SIMCO standalone en dev, levantar también `simco_v01/frontend` en `5174` o similar, o mejor, integrar el build de SIMCO al backend unificado.
   - Incluir checks de salud (`/health`, `/api/health`).
   - Manejar detención limpia de procesos previos.

2. Crear `data_datcorr/detener_plataforma.bat` que mate `uvicorn`, `node` y procesos asociados.

3. Mover/renombrar scripts de SIMCO a `data_datcorr/simco/scripts/` para mantener histórico.

---

### Fase 1 — Consolidar estructura de proyecto
**Objetivo:** Fusionar carpetas eliminando duplicación.

**Acciones:**
1. Decidir proyecto base: `data_datcorr` pasa a ser el proyecto único. Se crea `data_datcorr/simco/` como módulo.
2. Mover código de SIMCO:
   - `simco_v01/backend/app/api/routes/` → `data_datcorr/backend/routers/simco/`
   - `simco_v01/backend/app/services/` → `data_datcorr/backend/services/simco/`
   - `simco_v01/backend/app/models/` → `data_datcorr/backend/modelos/simco/`
   - `simco_v01/backend/app/schemas/` → `data_datcorr/backend/schemas/simco/`
   - `simco_v01/backend/app/db/` → `data_datcorr/backend/database/simco/`
   - `simco_v01/backend/app/core/` → `data_datcorr/backend/core/simco/`
   - `simco_v01/frontend/` → `data_datcorr/frontend_simco/` (se mantiene separado por ahora).
3. Actualizar imports en el código movido.
4. Eliminar `simco_v01/` (o archivarla como `.archive/simco_v01/` para rollback).

---

### Fase 2 — Depurar autenticación duplicada en DATCORR
**Objetivo:** Usar exclusivamente `platformcore` para identidad.

**Acciones:**
1. En `data_datcorr/backend/main.py`, **eliminar** importaciones y middlewares locales que dupliquen platformcore:
   - `backend.middleware.jwt_middleware.JWTMiddleware`
   - `backend.middleware.rate_limit_middleware.RateLimitMiddleware` (evaluar si se migra a platformcore o se mantiene local).
   - `backend.core.exceptions.DatcorrException` y handlers locales (evaluar si se mueven a platformcore).
2. Eliminar `data_datcorr/backend/routers/auth_router.py` (o renombrar a `_deprecated_auth_router.py`) y confiar en `platformcore.routers.auth_router`.
3. Actualizar `data_datcorr/frontend/src/auth/` para consumir `platformcore` (endpoint `/auth/login`, `/auth/me`, `/auth/refresh`).
4. Eliminar `data_datcorr/backend/security/` (jwt_manager, jwt_bearer) si ya no se usa.

**Nota:** SIMCO ya usa `platformcore.routers.auth_router` en su `main.py`, pero tiene `backend/app/api/routes/auth.py` local que también expone `/auth/login`. Se debe **eliminar** ese router local y confiar 100% en platformcore.

---

### Fase 3 — Unificar backend (API unificada)
**Objetivo:** Un solo `main.py` que sirva DATCORR y SIMCO.

**Acciones:**
1. Crear `data_datcorr/backend/main_unificado.py` (o modificar el existente) que incluya:
   - `platformcore.routers`: `auth`, `users`, `roles`, `permissions`, `audit`.
   - `backend.routers`: `admin`, `database`, `dashboard`, `reportes` (DATCORR).
   - `backend.routers.simco`: `solicitudes`, `respuestas`, `dashboard_simco`, `ws`, `buscar`, `notificaciones`, `messages`.
2. Configurar CORS unificado para ambos frontends (DATCORR: `5173`, SIMCO: `5173` o `5174`).
3. Unificar variables de entorno en `data_datcorr/.env`:
   - `DB_NAME_DATCOOR=datcorr`
   - `DB_NAME_SIMCO=simco`
   - `DB_NAME_PLATFORM=platform`
   - `BACKEND_PORT=8000`
   - `FRONTEND_DATCOOR_URL=http://localhost:5173`
   - `FRONTEND_SIMCO_URL=http://localhost:5174` (o build embebido)
4. Configurar `platformcore/config.py` para leer estas variables.

---

### Fase 4 — Unificar frontend y acceso a SIMCO
**Objetivo:** SIMCO accesible desde DATCORR en nueva pestaña, con permisos.

**Acciones:**
1. **Opción A (SPA separada, nueva pestaña):**
   - En `data_datcorr/frontend/src/pages/Dashboard.jsx`, agregar botón/enlace "SIMCO" visible solo para usuarios con permiso `simco.access`.
   - Al hacer clic, abrir `http://localhost:8000/simco` (o ruta equivalente) en nueva pestaña (`window.open`).
   - En el backend unificado, agregar ruta `/simco` que:
     - Verifica JWT (usando dependencia de platformcore).
     - Verifica permiso `simco.access`.
     - Si tiene permiso, sirve el build de SIMCO desde `data_datcorr/frontend_simco/dist/` (o redirige).
     - Si no, retorna 403.
   - Rutas SIMCO dentro del backend unificado: `/simco/*` sirven el SPA de SIMCO, mientras que `/api/simco/*` sirven los endpoints específicos.

2. **Opción B (iframe embebido):**
   - Dentro del layout de DATCORR, un iframe apuntando a `/simco`.
   - Menos recomendado por limitaciones de navegador y autenticación de cookies.

3. **Login único:**
   - El frontend de DATCORR consume `/auth/login` de `platformcore`.
   - El frontend de SIMCO (si se sirve separado) también consume `/auth/login` de `platformcore`, usando el mismo `SECRET_KEY` y `PLATFORM_DB`.
   - El JWT emitido debe contener claims de módulos permitidos: `{"modules": ["datcorr", "simco"], "permissions": [...]}`.

---

### Fase 5 — Permisos cross-módulo
**Objetivo:** Un rol pueda tener acceso a DATCORR, SIMCO o ambos.

**Acciones:**
1. En `platformcore`, extender el modelo de permisos para incluir ámbito de módulo:
   - `permiso.codigo = "simco.solicitudes.ver"`
   - `permiso.codigo = "simco.respuestas.crear"`
2. En el backend unificado, crear un middleware o dependencia `require_module_permission("simco", "solicitudes.ver")`.
3. En el frontend de DATCORR, ocultar/mostrar el botón SIMCO según `user.permissions.includes("simco.access")`.
4. Migrar permisos existentes de SIMCO a `platformcore` (si están en `simco` BD, mover a `platform` BD).

---

### Fase 6 — Verificación y ajustes
**Objetivo:** Probar flujo completo y ajustar.

**Acciones:**
1. Levantar `iniciar_plataforma.bat`.
2. Acceder a `http://localhost:8000` (o frontend DATCORR en `5173`).
3. Login con usuario de prueba.
4. Verificar:
   - Dashboard DATCORR carga.
   - Botón SIMCO visible solo para usuarios con permiso.
   - Al abrir SIMCO en nueva pestaña, la sesión se mantiene (mismo JWT, misma cookie `refresh_token`).
   - Endpoints de SIMCO responden correctamente.
   - Permisos deniegan acceso a SIMCO si el usuario no tiene el permiso.
5. Verificar que `platformcore` es el único identity provider (no hay llamadas a backends locales de auth).
6. Ajustar CORS, cookies y dominios si se despliega en producción.

---

## 5. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Pérdida de código de SIMCO al mover carpetas | Hacer commit/backup antes de mover. Mantener `simco_v01` como `.archive/simco_v01/` hasta validar Fase 3. |
| Colisión de puertos (5173 usado por ambos) | Usar `5173` para DATCORR y `5174` para SIMCO en dev, o integrar SIMCO como build servido por el backend unificado. |
| Cookies de refresh_token con dominios distintos | Usar dominio común y `path=/`, `samesite=strict` (ya está en platformcore). |
| Permisos legacy de SIMCO en BD propia | Script de migración de permisos SIMCO → platform BD. |
| Frontend SIMCO en TS y DATCORR en JS | Mantener `frontend_simco/` separado con su propio `package.json` y build. |

---

## 6. Entregables por fase

| Fase | Entregable |
|------|------------|
| 0 | `iniciar_plataforma.bat` / `.ps1` funcionando. |
| 1 | Estructura de carpetas unificada, código de SIMCO en `data_datcorr/simco/`. |
| 2 | Auth duplicada eliminada. Login consume solo `platformcore`. |
| 3 | `backend/main.py` unificado con routers DATCORR + SIMCO. |
| 4 | Botón en Dashboard DATCORR abre SIMCO en nueva pestaña con sesión activa. |
| 5 | Permisos `simco.*` funcionando en platformcore y reflejados en frontends. |
| 6 | Documento de verificación firmado y plan ajustado según hallazgos. |

---

## 7. Próximo paso inmediato

Ejecutar **Fase 0**: crear `iniciar_plataforma.bat` que levante el backend actual de DATCORR y verificar que arranca correctamente. Luego, proceder con Fase 1 (reestructuración de carpetas) y Fase 2 (limpieza de auth duplicada).
