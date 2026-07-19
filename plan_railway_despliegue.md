# Plan de ejecución para verificar y desplegar el proyecto completo en Railway

> Objetivo: validar el proyecto “de punta a punta” (build, runtime, variables de entorno, BD, frontend, healthchecks, migraciones/seed y pruebas) y dejarlo desplegado correctamente en **Railway** con un flujo repetible.  
> Alcance inicial recomendado: **data_datcorr** (FastAPI; módulo principal según tu confirmación).
> Nota: **simco_v01** se trata como módulo/servicio adicional (si necesitas exponer su frontend o APIs separadas).

---

## 0) Entender arquitectura y puntos de despliegue (verificación rápida)
### Simco_v01 (contenedor principal)
- **Dockerfile**:
  - Build de frontend: `npm run build`
  - Copia `frontend/dist` al contenedor
  - Instala dependencias Python desde `simco_v01/requirements.txt`
  - Ejecuta:
    - `cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- **Endpoint healthcheck**:
  - `/api/health` en `simco_v01/backend/app/main.py`
- **Railway config actual**:
  - `simco_v01/railway.json`
  - healthcheckPath: `/api/health`
  - deploy port: `8000`

### Base de configuración (DB/JWT)
- `platformcore/config.py` define:
  - DB Host/Port/Name/User/Password usando:
    - `PLATFORM_DB_HOST` (o `DB_HOST`), `PLATFORM_DB_PORT` (o `DB_PORT`), etc.
  - Si `PLATFORM_DB_ENGINE` ≠ `postgres` -> usa sqlite local (`sqlite:///./platform.db`)

---

## 1) Checklist de “verifica todo el proyecto” (antes de desplegar)
## 1.1 Build local (simco_v01)
1. Desde `simco_v01/`:
   - `npm ci` + `npm run build` (backend no debería fallar si el dist se genera bien)
2. Desde raíz (o simulando Docker):
   - `pip install -r simco_v01/requirements.txt`
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000` en `simco_v01/backend`
3. Verificar:
   - `GET /api/health` responde correctamente.

## 1.2 Verificación de rutas y frontend embebido
- Confirmar que `frontend/dist` existe al runtime (en Railway).
- Validar que el catch-all:
  - `GET /{full_path:path}` sirve `index.html` si no encuentra archivo estático.

## 1.3 Verificación de variables de entorno (Railway)
Railway debe inyectar env vars para PostgreSQL (recomendado):
- `PLATFORM_DB_ENGINE=postgres`
- `PLATFORM_DB_HOST=<host>`
- `PLATFORM_DB_PORT=5432` (o el del proveedor)
- `PLATFORM_DB_NAME=<db>`
- `PLATFORM_DB_USER=<user>`
- `PLATFORM_DB_PASSWORD=<pass>`

Opcional/según necesidad:
- JWT:
  - `SECRET_KEY` o `JWT_SECRET_KEY`
  - `ALGORITHM` (si quieres cambiar)
- CORS / PUBLIC_URL:
  - `PUBLIC_URL` (si quieres permitir un dominio específico en producción)

> Riesgo actual a mitigar: si NO configuran DB vars, el backend puede intentar usar sqlite local, lo cual normalmente no sirve bien para un entorno cloud.

## 1.4 Migrations/seed (punto crítico)
En lo que se pudo analizar aquí:
- No se encontró en el `main.py` de SIMCO una ejecución automática de migrations/seed.
- El contenedor solo inicia `uvicorn` (lifespan solo arranca `ws` poller).

Acciones propuestas:
- Identificar si existe un comando/entrypoint para inicializar BD (migraciones o creación de tablas).
- Definir en el flujo de Railway:
  - o bien un “pre-deploy job” que corra migraciones,
  - o documentación/ejecución manual una vez desplegado.

---

## 2) Propuesta de ajustes antes del despliegue (para que Railway funcione estable)
### Ajuste A — Asegurar que el contenedor usa PORT de Railway
- Ya está contemplado: `--port ${PORT:-8000}`.
- Verificar que Railway está marcando correctamente el puerto expuesto.

### Ajuste B — Configurar healthcheck consistente
- Ya está: `healthcheckPath: "/api/health"`
- Verificar en runtime que `/api/health` responde siempre.

### Ajuste C — Manejo de base de datos
- Recomiendo **Postgres** en Railway y configurar `PLATFORM_DB_*`.
- Confirmar compatibilidad de SQLAlchemy/driver con Railway (ya usa `psycopg2-binary`).

### Ajuste D — Seguridad de secretos
- `SECRET_KEY` por defecto es “change-me”.
- Recomendado definir `SECRET_KEY` real en Railway para JWT/seguridad.

### Ajuste E — WebSocket / Poller en lifespan
- `start_poller()` corre en lifespan.
- Recomiendo:
  - revisar que no dependa de recursos locales que no existen en Railway,
  - revisar variables para endpoints externos que puedan ser needed.

---

## 3) Plan de despliegue en Railway (paso a paso)
### 3.1 Preparar proyecto en Railway (data_datcorr)
1. Crear un **Project** en Railway.
2. Configurar despliegue para **data_datcorr**:
   - **Recomendado**: crear/usar un `Dockerfile` que:
     - instale `data_datcorr/requirements.txt`
     - ejecute `uvicorn` apuntando a `data_datcorr/backend/main.py`
3. Configurar el servicio:
   - Container port: `8000`
   - Healthcheck: `GET /health`

### 3.2 Variables de entorno (Railway)
Configurar:
- DB (obligatorio si quieres PostgreSQL):
  - `PLATFORM_DB_ENGINE=postgres`
  - `PLATFORM_DB_HOST=...`
  - `PLATFORM_DB_PORT=5432`
  - `PLATFORM_DB_NAME=...`
  - `PLATFORM_DB_USER=...`
  - `PLATFORM_DB_PASSWORD=...`
- JWT:
  - `SECRET_KEY` (o `JWT_SECRET_KEY`)
- (Opcional) CORS:
  - `PUBLIC_URL=https://<tu-dominio-railway>.railway.app`

## 3.3 Provisionamiento de datos (SIMCO v01 - referencia)
En `simco_v01/backend/app/db/` el flujo de inicialización es simple (sin Alembic). **Esto aplica si despliegas simco_v01** como servicio:
- `init_db.py` → crea tablas con `Base.metadata.create_all()`
- `seed.py` → crea un admin con env vars `ADMIN_USERNAME`, `ADMIN_PASSWORD`, etc.
- `migrate_sqlite_to_postgres.py` → migra un `sige.db` local a Postgres (opcional)

### 3.3.1 Requisitos de variables de entorno para DB
En `simco_v01/backend/app/db/session.py`:
- Si `DB_ENGINE=postgres`:
  - debe existir `DATABASE_URL` (o `POSTGRES_URL`)
  - el proyecto falla en runtime si no está
- Si no:
  - usa sqlite local `sqlite:///./sige.db`

**Recomendado en Railway:**
- `DB_ENGINE=postgres`
- `DATABASE_URL=<tu_connection_string_de_postgres>`

### 3.3.2 Job recomendado en Railway para inicializar (tablas + admin)
Configurar un **Railway Job** (o comando previo) que ejecute dentro del mismo contenedor/imagen:

**A) Crear tablas**
```bash
python -c "from app.db.init_db import init_db; init_db()"
```

**B) Crear admin (seed)**
```bash
python -c "from app.db.seed import create_admin; create_admin()"
```

**Env vars adicionales para seed (obligatorias si quieres admin automático):**
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_FULLNAME`
- `ADMIN_ROLE` (opcional, default: `admin`)

> Nota: `seed.py` hace `Base.metadata.create_all()` también, pero se recomienda ejecutar igual el step de init_db para mayor claridad/trace.


### 3.4 Validación post-deploy
1. Verificar healthcheck:
   - `/api/health`
2. Probar:
   - login / endpoints principales (según frontend)
3. Validar WebSocket:
   - abrir conexión y confirmar que `ws_router` funciona.
4. Verificar servir frontend:
   - abrir raíz `https://...` y confirmar carga del UI.

---

## 4) ¿Y “data_datcorr”?
Por el objetivo “desplegarlo por completo”, si data_datcorr es parte integral del sistema, deben confirmarse:
- si data_datcorr es un segundo servicio independiente con su propio backend,
- o si solo son scripts/módulos.

Puntos a revisar para data_datcorr (cuando lo analicemos):
- entrypoint ASGI/WSGI o main server (`main.py`).
- Dockerfile (si existe) o cómo construir.
- requirements y env vars DB propias.
- si usa PostgreSQL o un esquema distinto.
- migrations/seed (si aplica).

---

## 5) Cambios a pedirte/confirmar antes de implementar (ajustes propuestos)
Estos ajustes son los “más típicos” para que Railway quede estable:
1. Confirmar que el despliegue apunta a **data_datcorr** como servicio principal.
2. Confirmar si quieres **migraciones/seed automáticas** (ideal) o manuales.
3. Confirmar esquema de BD requerido:
   - si el sistema requiere tablas iniciales antes del primer login.
4. Confirmar si simco_v01 debe desplegarse como servicio adicional (y si aplica su seed/init).

---

## 6) Resultado esperado
- Un despliegue en Railway:
  - con Dockerfile funcionando,
  - healthcheck estable,
  - frontend servido desde `dist`,
  - backend conectado a PostgreSQL con variables `PLATFORM_DB_*`,
  - JWT funcionando con `SECRET_KEY` real,
  - y BD inicializada (migraciones/seed ejecutadas según corresponda).

---

## 7) Siguientes pasos para ejecutar (con tu aprobación)
1. Analizar en detalle:
   - dónde corren migraciones/seed (si existe comando),
   - qué endpoints requieren inicialización,
   - si existen archivos de configuración adicionales por entorno.
2. Preparar:
   - Job/Comando de migraciones (si aplica),
   - ajuste final a `railway.json` o creación de Procfile/entrypoint si Railway lo requiere.
3. Ejecutar despliegue.
