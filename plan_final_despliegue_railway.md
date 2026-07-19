# Plan final de despliegue Railway — Plataforma Unificada DATCORR + SIMCO

> **Basado en:** verificación exhaustiva del código real (`C:\plataforma`) al 18/07/2026.
> **Arquitectura:** un solo servicio FastAPI (`main_unificado.py`) que integra platformcore + datcorr + simco,
> con tres bases de datos PostgreSQL separadas en un mismo servidor, WebSocket para notificaciones en tiempo real,
> y dos frontends React servidos desde el mismo backend.
>
> **Documento de implementación y guía para despliegue de prueba y producción.**

---

## 0. Verificación de coherencia (respuestas del usuario vs. código real)

| Decisión del usuario | Verificación en código | ¿Coherente? |
|---|---|---|
| App web principal = `data_datcorr/frontend/` | `AppRouter.jsx` usa `BrowserRouter` con rutas `/` (Login), `/dashboard`, `/usuarios`, `/reportes`, etc. API calls con `baseURL: ""` (mismo origen). Login envía `POST /auth/login`. Todo correcto. | ✅ |
| Tres bases separadas (`platform`, `simco`, `datcorr`) | `platformcore/config.py` → `PLATFORM_DB_NAME=platform`. `simco_v01/backend/app/db/session.py` → `DATABASE_URL` apunta a `simco`. `data_datcorr/database/conexion.py` → `DB_NAME=datcorr`. Mismo servidor, distinto DB name. | ✅ |
| WebSocket necesario | `ws.py` router con `start_poller()` que monitorea nuevas solicitudes pendientes/respondidas. Frontend `Solicitudes.tsx`/`Respuestas.tsx` usan `useRefreshOnNotification`. | ✅ |
| API docs solo en desarrollo | `FastAI(docs_url="/docs")`. Hacer condicional con `ENVIRONMENT=production`. | ✅ (por implementar) |

---

## 1. Arquitectura de despliegue

```
Railway: 1 servicio → 1 contenedor → 1 proceso uvicorn
                        │
                        ├─ platformcore/       (paquete fuente)
                        ├─ data_datcorr/
                        │   ├─ backend/        (main_unificado.py + routers datcorr)
                        │   └─ frontend/dist   (React build → servido en /app/)
                        └─ simco_v01/
                            ├─ backend/        (routers simco)
                            └─ frontend/dist   (React build → servido en /simco/)

Railway Postgres: 1 instancia, 3 databases
                        ├─ platform    (platformcore: usuarios, roles, permisos, auditoría)
                        ├─ simco       (SIMCO: solicitudes, respuestas, audit_logs)
                        └─ datcorr     (DATCORR: datos documentales, reportes)
```

---

## 2. Estructura de archivos a crear/modificar

```
C:\plataforma\
├── Dockerfile                          # NUEVO — build multi-etapa, entrypoint unificado
├── railway.json                        # NUEVO — configuración Railway en la raíz
├── .dockerignore                       # NUEVO — excluir lo que no va al contenedor
├── requirements-web.txt                # NUEVO — solo dependencias web (SIN PySide6)
├── data_datcorr/
│   └── backend/
│       └── main_unificado.py           # MODIFICAR — lifespan, docs condicional, servir /app/
└── plan_final_despliegue_railway.md    # ESTE DOCUMENTO
```

---

## 3. Archivos de configuración

### 3.1 Dockerfile (raíz)

```dockerfile
# ── Etapa 1: Build frontend DATCORR ──
FROM node:20 AS datcorr-frontend
WORKDIR /app/data_datcorr/frontend
COPY data_datcorr/frontend/package*.json ./
RUN npm ci
COPY data_datcorr/frontend/ ./
RUN npm run build

# ── Etapa 2: Build frontend SIMCO ──
FROM node:20 AS simco-frontend
WORKDIR /app/simco_v01/frontend
COPY simco_v01/frontend/package*.json ./
RUN npm ci
COPY simco_v01/frontend/ ./
RUN npm run build

# ── Etapa 3: Backend Python ──
FROM python:3.13-slim

# Instalar dependencias del sistema para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar código fuente (paquetes planos)
COPY platformcore/ ./platformcore/
COPY simco_v01/backend/ ./simco_v01/backend/
COPY data_datcorr/backend/ ./data_datcorr/backend/

# Copiar frontends compilados
COPY --from=datcorr-frontend /app/data_datcorr/frontend/dist ./data_datcorr/frontend/dist
COPY --from=simco-frontend /app/simco_v01/frontend/dist ./simco_v01/frontend/dist

# Instalar dependencias Python web
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# Limpiar paquetes de build
RUN apt-get purge -y --auto-remove gcc && rm -rf /var/lib/apt/lists/*

# Variables por defecto
ENV DB_ENGINE=postgres
ENV PLATFORM_DB_ENGINE=postgres
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

WORKDIR /app/data_datcorr
CMD ["sh", "-c", "uvicorn backend.main_unificado:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### 3.2 railway.json (raíz)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "port": 8000,
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE",
    "healthcheckTimeout": 100
  }
}
```

### 3.3 .dockerignore (raíz)

```
venv/
__pycache__/
*.pyc
.env
.git/
.vscode/
*.log
*.tmp
*.bak
node_modules/
data_datcorr/frontend/node_modules/
simco_v01/frontend/node_modules/
*.db
sige.db
.DS_Store
Thumbs.db
.gitignore
README.md
backup/
infra/
*.bat
*.ps1
*.rar
```

### 3.4 requirements-web.txt (raíz)

```
# Web backend — SIN PySide6 (solo para escritorio local)
fastapi==0.138.0
uvicorn[standard]==0.49.0
sqlalchemy==2.0.51
psycopg2-binary==2.9.12
python-jose==3.5.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
python-dotenv==1.2.2
pydantic==2.13.4
python-multipart==0.0.32
openpyxl==3.1.5
reportlab==5.0.0
requests==2.32.5
cryptography>=48.0.0
starlette>=0.49.0
websockets>=14.0
```

---

## 4. Modificaciones a `main_unificado.py`

Cambios requeridos:

1. **Mover `init_db()` y `start_poller()` a un `lifespan`** (evita fallo si BD no está lista al arrancar)
2. **Hacer `/docs` y `/redoc` condicionales** (solo en desarrollo)
3. **Servir frontend DATCORR en `/app/`** (ruta principal de la web)
4. **Agregar CORS para Railway**

```python
"""
Backend Unificado DATCORR + SIMCO
Sirve ambos módulos desde un solo proceso FastAPI.
"""
import os
import sys
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

# ── Agregar rutas base al path ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATAFORMA_DIR = os.path.dirname(BASE_DIR)
for p in [PLATAFORMA_DIR, os.path.join(PLATAFORMA_DIR, "simco_v01", "backend")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# ── Platform Core ────────────────────────────────────────────────────────
from platformcore.routers import (
    auth_router, users_router, roles_router,
    permissions_router, audit_router,
)

# ── DATCORR module ──────────────────────────────────────────────────────
from backend.routers.admin_router import router as datcorr_admin_router
from backend.routers.database_router import router as datcorr_database_router
from backend.routers.dashboard_router import router as datcorr_dashboard_router
from backend.routers.reportes_router import router as datcorr_reportes_router
from backend.core.exceptions import DatcorrException
from backend.core.handlers import datcorr_exception_handler, generic_exception_handler

# ── SIMCO module ────────────────────────────────────────────────────────
from app.api.routes.solicitudes import router as simco_solicitudes_router
from app.api.routes.respuestas import router as simco_respuestas_router
from app.api.routes.dashboard import router as simco_dashboard_router
from app.api.routes.ws import router as simco_ws_router, start_poller
from app.api.routes.buscar import router as simco_buscar_router
from app.api.routes.notificaciones import router as simco_notificaciones_router
from app.api.routes.messages import router as simco_messages_router
from app.db.init_db import init_db as simco_init_db
from platformcore.database import init_db as platform_init_db

# ── Middleware ──────────────────────────────────────────────────────────
from backend.middleware.jwt_middleware import JWTMiddleware
from backend.middleware.rate_limit_middleware import RateLimitMiddleware

# ── Lifespan (inicialización segura) ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        platform_init_db()
        simco_init_db()
        start_poller()
        print("[UNIFICADO] Tablas inicializadas y WebSocket poller iniciado")
    except Exception as e:
        print(f"[UNIFICADO] WARN: Error en inicialización (la BD puede no estar lista aún): {e}")
    yield

# ── Docs solo en desarrollo ─────────────────────────────────────────────
_is_prod = os.getenv("ENVIRONMENT", "development").lower() == "production"

app = FastAPI(
    title="Plataforma Unificada DATCORR + SIMCO",
    version="1.0.0",
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────────
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
public_url = os.getenv("PUBLIC_URL", "")
railway_url = os.getenv("RAILWAY_URL", "")
for url in [public_url, railway_url]:
    if url and url not in origins:
        origins.append(url)

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.add_middleware(RateLimitMiddleware, max_attempts=5, window_seconds=300, ban_seconds=900)
app.add_middleware(JWTMiddleware)

# ── Exception handlers ──────────────────────────────────────────────────
app.add_exception_handler(DatcorrException, datcorr_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ═══════════════════════════════════════════════════════════════════════
# ROUTERS
# ═══════════════════════════════════════════════════════════════════════

# Platform
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(audit_router)

# DATCORR
app.include_router(datcorr_admin_router)
app.include_router(datcorr_database_router)
app.include_router(datcorr_dashboard_router)
app.include_router(datcorr_reportes_router)

# SIMCO
app.include_router(simco_solicitudes_router)
app.include_router(simco_respuestas_router)
app.include_router(simco_dashboard_router)
app.include_router(simco_ws_router)
app.include_router(simco_buscar_router)
app.include_router(simco_notificaciones_router)
app.include_router(simco_messages_router)

# ═══════════════════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════════════════
@app.get("/health")
def health():
    return {"status": "ok", "platform": "unificada", "modules": ["datcorr", "simco"]}

@app.get("/api/health")
def api_health():
    return {"message": "Plataforma Unificada funcionando"}

# ═══════════════════════════════════════════════════════════════════════
# FRONTENDS
# ═══════════════════════════════════════════════════════════════════════

# ── Frontend DATCORR (app principal) en /app/ ─────────────────────────
_datcorr_dist = os.path.join(
    os.path.dirname(__file__), "..", "frontend", "dist"
)
if os.path.isdir(_datcorr_dist):
    _datcorr_assets = os.path.join(_datcorr_dist, "assets")
    if os.path.isdir(_datcorr_assets):
        app.mount("/app/assets", StaticFiles(directory=_datcorr_assets), name="datcorr_assets")

    @app.get("/app")
    async def serve_datcorr_root():
        return FileResponse(os.path.join(_datcorr_dist, "index.html"))

    @app.get("/app/{full_path:path}")
    async def serve_datcorr_frontend(full_path: str):
        file_path = os.path.join(_datcorr_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(_datcorr_dist, "index.html"),
                            headers={"Cache-Control": "no-cache, no-store, must-revalidate",
                                     "Pragma": "no-cache", "Expires": "0"})

    # Redirigir raíz a /app/
    @app.get("/")
    async def root():
        return FileResponse(os.path.join(_datcorr_dist, "index.html"))

    print(f"[UNIFICADO] Sirviendo frontend DATCORR desde: {_datcorr_dist}")
else:
    @app.get("/")
    def root_fallback():
        return {"mensaje": "Plataforma Unificada DATCORR + SIMCO", "version": "1.0.0",
                "modules": ["datcorr", "simco"]}

# ── Frontend SIMCO en /simco/ ─────────────────────────────────────────
_simco_dist = os.path.join(
    os.path.dirname(__file__), "..", "..", "simco_v01", "frontend", "dist"
)
if os.path.isdir(_simco_dist):
    _simco_assets = os.path.join(_simco_dist, "assets")
    if os.path.isdir(_simco_assets):
        app.mount("/simco/assets", StaticFiles(directory=_simco_assets), name="simco_assets")
        app.mount("/assets", StaticFiles(directory=_simco_assets), name="simco_assets_root")

    @app.get("/simco")
    async def serve_simco_root():
        return FileResponse(os.path.join(_simco_dist, "index.html"))

    @app.get("/simco/{full_path:path}")
    async def serve_simco_frontend(full_path: str):
        file_path = os.path.join(_simco_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(_simco_dist, "index.html"),
                            headers={"Cache-Control": "no-cache, no-store, must-revalidate",
                                     "Pragma": "no-cache", "Expires": "0"})

    @app.get("/favicon.svg")
    async def serve_favicon():
        return FileResponse(os.path.join(_simco_dist, "favicon.svg"))

    @app.get("/icons.svg")
    async def serve_icons():
        return FileResponse(os.path.join(_simco_dist, "icons.svg"))

    print(f"[UNIFICADO] Sirviendo frontend SIMCO desde: {_simco_dist}")
```

> **Nota:** Los assets del login (`login.png`, `logo.webp`) están en `data_datcorr/frontend/public/images/login/`.
> Vite los copia automáticamente a `dist/images/login/` durante el build, por lo que estarán disponibles
> en `/app/images/login/login.png` y `/app/images/login/logo.webp`.

---

## 5. Variables de entorno en Railway

### 5.1 Plugin PostgreSQL

Agregar un **Railway Postgres plugin** al proyecto. Railway inyecta automáticamente:
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
- `DATABASE_URL` con la conexión a la base por defecto (usaremos esta para `datcorr`)

### 5.2 Variables adicionales a configurar manualmente

```
# ── Para SIMCO (app/db/session.py lee DATABASE_URL o POSTGRES_URL)
DB_ENGINE=postgres
# DATABASE_URL la inyecta Railway (apunta a la DB por defecto)
# SIMCO necesita su propia DB "simco" → se la pasamos como POSTGRES_URL
POSTGRES_URL=postgresql://<user>:<pass>@<host>:<port>/simco

# ── Para platformcore (config.py lee PLATFORM_DB_*)
PLATFORM_DB_ENGINE=postgres
PLATFORM_DB_HOST=${{Postgres.HOST}}
PLATFORM_DB_PORT=${{Postgres.PORT}}
PLATFORM_DB_NAME=platform
PLATFORM_DB_USER=${{Postgres.USER}}
PLATFORM_DB_PASSWORD=${{Postgres.PASSWORD}}

# ── Para DATCORR (database/conexion.py lee DB_*)
DB_USER=${{Postgres.USER}}
DB_PASSWORD=${{Postgres.PASSWORD}}
DB_HOST=${{Postgres.HOST}}
DB_PORT=${{Postgres.PORT}}
DB_NAME=datcorr

# ── JWT
JWT_SECRET_KEY=<generar secreto: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
SECRET_KEY=<mismo valor>

# ── Entorno
ENVIRONMENT=production
PUBLIC_URL=https://<proyecto>.railway.app
RAILWAY_URL=https://<proyecto>.railway.app
```

### 5.3 Seed admin SIMCO (opcional, una sola vez)

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<contraseña-segura>
ADMIN_FULLNAME=Administrador
ADMIN_ROLE=admin
```

---

## 6. Creación de las bases de datos en Railway

Railway Postgres provisiona automáticamente una base (ej: `railway`). Las otras dos (`platform`, `simco`)
se crean ejecutando SQL contra la misma instancia.

### Método A — Railway Job post-deploy (recomendado)

Crear un **Railway Job** que ejecute:

```bash
# psql usa las credenciales del plugin Postgres
psql $DATABASE_URL -c "CREATE DATABASE platform;"
psql $DATABASE_URL -c "CREATE DATABASE simco;"
```

Si `$DATABASE_URL` apunta a la DB por defecto (`railway`), los comandos `CREATE DATABASE` crean nuevas
bases en el mismo servidor.

### Método B — Manual (una sola vez)

```bash
# Desde la CLI de Railway o un contenedor temporal
railway run psql -c "CREATE DATABASE platform;"
railway run psql -c "CREATE DATABASE simco;"
```

### Método C — En el Dockerfile (al arrancar)

Agregar al `CMD` del Dockerfile:

```bash
(sh -c "
  psql $DATABASE_URL -c 'CREATE DATABASE platform;' 2>/dev/null || true;
  psql $DATABASE_URL -c 'CREATE DATABASE simco;' 2>/dev/null || true;
  uvicorn backend.main_unificado:app --host 0.0.0.0 --port ${PORT:-8000}
")
```

Esto intenta crear las bases cada vez que arranca; si ya existen, el error se silencia.

---

## 7. Plan de pruebas pre-despliegue

### 7.1 Prueba de build local

```bash
# 1. Construir la imagen
docker build -t plataforma-test -f Dockerfile .

# 2. Ejecutar contenedor local con Postgres (necesitas Postgres corriendo con las 3 DBs)
docker run --rm -p 8000:8000 ^
  -e DATABASE_URL=postgresql://postgres:postgres123@host.docker.internal:5432/railway ^
  -e POSTGRES_URL=postgresql://postgres:postgres123@host.docker.internal:5432/simco ^
  -e PLATFORM_DB_ENGINE=postgres ^
  -e PLATFORM_DB_HOST=host.docker.internal ^
  -e PLATFORM_DB_PORT=5432 ^
  -e PLATFORM_DB_NAME=platform ^
  -e PLATFORM_DB_USER=postgres ^
  -e PLATFORM_DB_PASSWORD=postgres123 ^
  -e DB_USER=postgres ^
  -e DB_PASSWORD=postgres123 ^
  -e DB_HOST=host.docker.internal ^
  -e DB_PORT=5432 ^
  -e DB_NAME=datcorr ^
  -e JWT_SECRET_KEY=test-key-no-segura ^
  -e SECRET_KEY=test-key-no-segura ^
  -e ENVIRONMENT=development ^
  plataforma-test
```

### 7.2 Test endpoints (post-build)

```bash
# Healthchecks
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8000/api/health | jq .

# Swagger (solo si ENVIRONMENT≠production)
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs

# Frontend DATCORR
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/app/
# Debe responder 200 y ser HTML

# Frontend SIMCO
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/simco/
# Debe responder 200 y ser HTML

# Login API
curl -s -X POST http://localhost:8000/auth/login ^
  -H "Content-Type: application/json" ^
  -d '{"username":"admin","password":"admin123"}' | jq .

# SIMCO solicitudes (sin token, esperar 200 porque no requiere auth GET)
curl -s http://localhost:8000/solicitudes/ | jq .
```

### 7.3 Test WebSocket

```bash
# Usar wscat o python para verificar conexión WebSocket
python -c "
import asyncio, websockets
async def test():
    async with websockets.connect('ws://localhost:8000/ws/notificaciones') as ws:
        print('WS connected')
        msg = await asyncio.wait_for(ws.recv(), timeout=10)
        print('Received:', msg)
asyncio.run(test())
"
```

---

## 8. Script de test automatizado

Crear `test_despliegue.py` en la raíz para validación post-deploy:

```python
"""
test_despliegue.py — Pruebas de humo post-despliegue.
Uso: python test_despliegue.py <base_url>
Ejemplo: python test_despliegue.py https://plataforma.up.railway.app
"""
import sys, requests, json

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"

def test(desc, method, path, expect=200, **kwargs):
    url = f"{BASE}{path}"
    try:
        r = requests.request(method, url, **kwargs, timeout=15)
        status = "✅" if r.status_code == expect else "❌"
        print(f"  {status} {method} {path} → {r.status_code} (esperado {expect})")
        if r.status_code != expect:
            print(f"      Body: {r.text[:200]}")
        return r.status_code == expect
    except Exception as e:
        print(f"  ❌ {method} {path} → ERROR: {e}")
        return False

print(f"\n═══ Pruebas de despliegue: {BASE} ═══\n")

all_ok = True

# Health
all_ok &= test("Health", "GET", "/health")
all_ok &= test("API Health", "GET", "/api/health")

# Frontends
all_ok &= test("Frontend DATCORR", "GET", "/app/")
all_ok &= test("Frontend SIMCO", "GET", "/simco/")

# Swagger (debe ser 200 si no es producción)
env = requests.get(f"{BASE}/health").json().get("environment", "development")
if env != "production":
    all_ok &= test("Swagger docs", "GET", "/docs", 200)

# API endpoints
all_ok &= test("Solicitudes (sin auth)", "GET", "/solicitudes/")
all_ok &= test("Respuestas (sin auth)", "GET", "/respuestas/")
all_ok &= test("Dashboard activity", "GET", "/dashboard/activity")

# Login (depende de que exista usuario)
r = requests.post(f"{BASE}/auth/login", json={"username": "test", "password": "test"}, timeout=10)
if r.status_code == 200:
    print(f"  ✅ Login funciona (usuario existe)")
else:
    print(f"  ⚠️  Login: {r.status_code} (esperado si no hay seed)")

print(f"\n═══ Resultado: {'✅ TODAS OK' if all_ok else '❌ ALGUNAS FALLARON'} ═══\n")
sys.exit(0 if all_ok else 1)
```

---

## 9. Guía de despliegue paso a paso

### 9.1 Despliegue de prueba (Railway Preview)

1. **Crear proyecto Railway** y conectar repositorio GitHub (rama `main` o `develop`)
2. **Agregar Postgres plugin** (Railway lo provisiona automáticamente)
3. **Configurar variables de entorno** según la sección 5
4. **Crear bases de datos** usando un Railway Job (sección 6)
5. **Railway detecta `railway.json`** y ejecuta el build con `Dockerfile`
6. **Railway asigna URL** tipo `https://plataforma-xxxx.up.railway.app`
7. **Ejecutar tests:**
   ```bash
   python test_despliegue.py https://plataforma-xxxx.up.railway.app
   ```
8. **Verificar login manual:** abrir `https://plataforma-xxxx.up.railway.app/app/`

### 9.2 Despliegue de producción

1. **Cambiar `ENVIRONMENT=production`** en Railway
2. **Generar `JWT_SECRET_KEY`** segura: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
3. **Configurar dominio personalizado** en Railway Settings → Domains
4. **Actualizar `PUBLIC_URL` y `RAILWAY_URL`** con el dominio real
5. **Ejecutar seed de admin** si es necesario:
   ```bash
   railway run python -c "
   import sys
   sys.path.insert(0, '/app')
   sys.path.insert(0, '/app/simco_v01/backend')
   from app.db.seed import create_admin
   create_admin()
   "
   ```
6. **Verificar migración de datos** (cuando corresponda):
   - Exportar datos de `platform`, `simco`, `datcorr` desde desarrollo
   - Importar en las bases de Railway
   - Verificar consistencia

---

## 10. Migración de datos reales (futuro)

Cuando llegue el momento de migrar datos reales:

1. **Exportar desde entorno actual:**
   ```bash
   pg_dump -h localhost -U postgres -d platform > platform_export.sql
   pg_dump -h localhost -U postgres -d simco > simco_export.sql
   pg_dump -h localhost -U postgres -d datcorr > datcorr_export.sql
   ```
2. **Importar en Railway:**
   ```bash
   # Obtener DATABASE_URL del plugin Postgres en Railway
   psql $DATABASE_URL/platform -f platform_export.sql
   psql $DATABASE_URL/simco -f simco_export.sql
   psql $DATABASE_URL/datcorr -f datcorr_export.sql
   ```
   O usando `railway run`:
   ```bash
   railway run psql -d platform -f platform_export.sql
   railway run psql -d simco -f simco_export.sql
   railway run psql -d datcorr -f datcorr_export.sql
   ```
3. **Verificar:** login, consultas, reportes con datos reales

---

## 11. Riesgos y contingencias

| Riesgo | Impacto | Mitigación |
|---|---|---|
| PySide6 en requirements si se usa archivo incorrecto | Build falla en `python:3.13-slim` | Usar exclusivamente `requirements-web.txt` para el contenedor |
| BD no lista al iniciar el contenedor | `init_db()` falla, app no arranca | Migrado a `lifespan` con try/except |
| WebSocket no funciona sin `websockets` | Notificaciones en tiempo real rotas | Incluido en `requirements-web.txt` |
| Assets de login no encontrados | Login sin imágenes | Vite copia `public/` a `dist/` automáticamente |
| `platformcore` no encontrado en import | App no arranca | `main_unificado.py` agrega `PLATAFORMA_DIR` a `sys.path`, y `Dockerfile` copia `platformcore/` |
| Dos frontends en rutas separadas | Confusión de URL | `/app/` = datcorr (principal), `/simco/` = SIMCO (solicitudes) |
| Multi-réplica con WebSocket poller | Broadcast duplicados | `numReplicas: 1` en `railway.json` (si se escala, migrar a Redis pub/sub) |

---

## 12. Checklist final pre-ejecución

- [ ] ¿`Dockerfile` creado en la raíz con multi-etapa?
- [ ] ¿`railway.json` creado en la raíz con healthcheck `/health`?
- [ ] ¿`.dockerignore` creado en la raíz?
- [ ] ¿`requirements-web.txt` creado SIN PySide6?
- [ ] ¿`main_unificado.py` modificado con `lifespan`, docs condicional, `/app/` frontend?
- [ ] ¿Build local exitoso? (`docker build -t plataforma .`)
- [ ] ¿Variables de entorno configuradas en Railway?
- [ ] ¿Bases de datos `platform` y `simco` creadas en Railway Postgres?
- [ ] ¿Tests de humo pasan? (`python test_despliegue.py <url>`)
- [ ] ¿Seed de admin ejecutado?
- [ ] ¿Login manual verificado en `/app/`?
- [ ] ¿SIMCO verificado en `/simco/`?
