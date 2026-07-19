# Análisis y plan de despliegue Railway — verificación contra el código real

> Generado el 18/07/2026 tras contrastar `plan_railway_despliegue.md` y
> `analisis_plan_railway_corregido.md` contra el código real de `C:\plataforma`.

---

## 0. Veredicto de viabilidad

**Los dos documentos tienen aproximaciones útiles pero contienen imprecisiones graves
frente al código real.** Ninguno puede ejecutarse tal cual. Se requiere un plan nuevo
basado en la arquitectura que realmente existe.

| Documento | Precisión | Problema principal |
|---|---|---|
| `plan_railway_despliegue.md` | 30% | Asume `simco_v01` como servicio aislado. Ignora `main_unificado.py` y `data_datcorr/backend`. |
| `analisis_plan_railway_corregido.md` | 75% | Acierta en la necesidad de unificar. Pero dice que `platformcore` tiene `pyproject.toml` (NO existe) y que `main_unificado.py` ejecuta migraciones en import-time (CIERTO después de nuestras correcciones de esta sesión). |

---

## 1. Arquitectura real (lo que SÍ existe en el repo)

```
C:\plataforma\
├── platformcore/                    # Paquete Python fuente (sin setup.py ni pyproject.toml)
│   ├── database.py                  # init_db(), engine, Base
│   ├── config.py                    # PlatformSettings → PLATFORM_DB_*, JWT
│   ├── routers/                     # auth, users, roles, permissions, audit
│   └── models/                      # identity (PlatformUser), security, audit
│
├── simco_v01/
│   ├── Dockerfile                   # Build frontend + pip install + uvicorn app.main:app
│   ├── railway.json                 # healthcheck /api/health, port 8000
│   ├── .dockerignore
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py              # FastAPI independiente (NO usado en unificado)
│   │   │   ├── api/routes/          # solicitudes, respuestas, dashboard, ws, buscar...
│   │   │   ├── db/
│   │   │   │   ├── session.py       # DB_ENGINE + DATABASE_URL/POSTGRES_URL
│   │   │   │   ├── init_db.py       # create_all() para tablas SIMCO
│   │   │   │   └── seed.py          # Crea admin con ADMIN_*
│   │   │   └── models/              # Solicitud, Respuesta, AuditLog, Message, User
│   │   └── requirements.txt
│   └── frontend/                    # React + Vite + TypeScript
│       └── dist/                    # Build output
│
├── data_datcorr/
│   ├── backend/
│   │   ├── main_unificado.py        # *** ENTRYPOINT REAL *** – une platform + datcorr + simco
│   │   ├── main.py                  # FastAPI solo datcorr (alternativa)
│   │   ├── routers/                 # admin, database, dashboard, reportes
│   │   └── requirements.txt         # *** incluye PySide6 (problema) ***
│   ├── frontend/                    # React + Vite (app web datcorr)
│   ├── ui/                          # PySide6 (app de escritorio)
│   └── ventanas/                    # PySide6 (app de escritorio)
│
├── .env                             # Solo para datcorr (no se copia al contenedor)
├── requirements-platform.txt        # Dependencias base para platformcore
```

### Puntos clave de la arquitectura real

1. **`main_unificado.py` es el entrypoint real.** Importa `platformcore`, los routers de `backend/` (datcorr) y los de `app/` (simco). Agrega `PLATAFORMA_DIR` y `simco_v01/backend` a `sys.path` para resolver imports.

2. **`simco_v01/Dockerfile` es insuficiente** para la app unificada: solo copia `backend/` y `requirements.txt` de SIMCO, no incluye `platformcore/` ni `data_datcorr/backend/`.

3. **`platformcore` NO tiene `pyproject.toml` ni `setup.py`.** Es un paquete fuente plano. No se puede instalar con `pip install ./platformcore`. Debe copiarse al contenedor y estar presente en `sys.path` (como ya hace `main_unificado.py`).

4. **Dos configuraciones de base de datos divergentes:**
   - `platformcore/config.py`: usa variables `PLATFORM_DB_*` (o fallback `DB_*`)
   - `simco_v01/backend/app/db/session.py`: usa `DB_ENGINE` + `DATABASE_URL`/`POSTGRES_URL`
   - `data_datcorr/backend/` usa las variables de `data_datcorr/.env`
   - **Ninguna apunta automáticamente al mismo Postgres.** En Railway hay que coordinar las tres o unificarlas.

5. **Dos frontends React:**
   - `simco_v01/frontend/` → se sirve desde `main_unificado.py` en `/simco` (build ya incluido)
   - `data_datcorr/frontend/` → es la web app de datcorr (Panel de control, reportes). **Actualmente NO se sirve desde el backend.** Solo existe como app de escritorio PySide6.

6. **`data_datcorr/requirements.txt` incluye PySide6 (escritorio).** Esto rompe el build en Linux slim si se instala tal cual.

---

## 2. Contraste punto por punto con `plan_railway_despliegue.md`

| # | Plan dice | Realidad | ¿Viable? |
|---|---|---|---|
| 1 | "data_datcorr es el módulo principal" | `main_unificado.py` es el que integra TODO. data_datcorr es un módulo dentro de él | ⚠️ Impreciso |
| 2 | "simco_v01 es módulo adicional con su propio Dockerfile" | El Dockerfile de simco_v01 no incluye platformcore ni data_datcorr | ❌ Falla en build |
| 3 | "Healthcheck: /api/health" | Existe en `main_unificado.py:131` también | ✅ |
| 4 | "Railway inyecta PLATFORM_DB_*" | platformcore sí los usa; simco NO (usa DB_ENGINE + DATABASE_URL) | ⚠️ Parcial |
| 5 | "init_db + seed manual con Railway Job" | `main_unificado.py` ya ejecuta `platform_init_db()`, `simco_init_db()` y `start_poller()` en import-time (líneas 136-138) | ✅ Ya resuelto |
| 6 | "migrate_sqlite_to_postgres.py existe" | NO existe en el repo | ❌ Inexistente |
| 7 | "data_datcorr es segundo servicio independiente" | Es parte del mismo proceso unificado | ❌ Incorrecto |

---

## 3. Contraste punto por punto con `analisis_plan_railway_corregido.md`

| # | Análisis dice | Realidad | ¿Correcto? |
|---|---|---|---|
| 1 | "platformcore está empaquetado vía pyproject.toml (0.1.0)" | **NO existe** pyproject.toml ni setup.py | ❌ Falso |
| 2 | "pip install ./platformcore" | Eso fallaría porque no hay setup.py | ❌ Inviable |
| 3 | "main_unificado.py ejecuta migraciones en import-time" | ✅ Cierto (líneas 136-138 después de nuestras correcciones) | ✅ |
| 4 | "dockerignore excluir node_modules, venv, *.db" | `simco_v01/.dockerignore` existe pero no cubre data_datcorr | ⚠️ Parcial |
| 5 | "Crear requirements-railway.txt sin PySide6" | ✅ Recomendación correcta | ✅ |
| 6 | "Dos configuraciones de BD divergentes" | ✅ Cierto, hay que resolverlo | ✅ |
| 7 | "Dockerfile nuevo en la raíz" | ✅ Recomendación correcta | ✅ |
| 8 | "Un único servicio Railway" | ✅ Correcto | ✅ |

---

## 4. Problemas críticos reales para el despliegue

### 🔴 CRÍTICO 1 — `platformcore` no tiene empaquetado pip
No hay `pyproject.toml`, `setup.py` ni `setup.cfg`. El plan de análisis dice "pip install ./platformcore"
pero eso no funciona. **Solución:** copiar `platformcore/` al contenedor y confiar en que `main_unificado.py`
agrega `PLATAFORMA_DIR` a `sys.path`. El Dockerfile debe hacer `COPY platformcore/ ./platformcore/`.

### 🔴 CRÍTICO 2 — `data_datcorr/requirements.txt` con PySide6 rompe el build
Railway usa `python:3.13-slim`. PySide6 necesita `libGL`, `libxcb`, etc. y pesa ~200MB extra.
**Solución:** crear un archivo `requirements-web.txt` que excluya las dependencias de escritorio.

### 🔴 CRÍTICO 3 — Dos backend Python con requirements distintos
- `simco_v01/requirements.txt` → fastapi 0.138, sqlalchemy 2.0.51, passlib 1.7.4, bcrypt 4.0.1
- `data_datcorr/requirements.txt` → fastapi 0.128, sqlalchemy 2.0.49, passlib 1.7.4 (sin bcrypt)
- `requirements-platform.txt` → fastapi >=0.128, sqlalchemy >=2.0

**Hay que resolver una sola versión para cada dependencia.** Recomendado: usar las versiones de
`simco_v01/requirements.txt` (más modernas) como base del archivo web unificado.

### 🔴 CRÍTICO 4 — Dos frontends React, solo uno se sirve
- `simco_v01/frontend/` → ya se sirve en `/simco` desde `main_unificado.py`
- `data_datcorr/frontend/` → es la web app del panel de control, NO se sirve desde el backend actualmente

**¿Cuál es la web app principal?** El usuario accede a:
  - `http://dominio/` → raíz de la API
  - `http://dominio/simco/` → frontend SIMCO (solicitudes/respuestas)
  - `http://dominio/docs` → Swagger
  
La app web `data_datcorr/frontend/` (login, dashboard, reportes web) es la que acabamos de rediseñar
(Login.jsx). Pero las rutas NO están montadas en `main_unificado.py`. Si la idea es que sea la web
principal, hay que buildearla y servirla en `/` o en una ruta como `/app/`.

### 🟠 MAYOR 5 — Dos bases de datos sin coordinación en Railway
El plan de análisis sugiere "unificar variables". Pero no es solo un tema de variables: los modelos de
`platformcore` (PlatformUser) viven en la base `platform`, los de `simco` (Solicitud, Respuesta) en
`simco`, y los de `datcorr` en `datcorr`. En Railway todo puede ir a un mismo Postgres con schemas o
bases separadas, pero hay que decidir el esquema.

### 🟠 MAYOR 6 — `start_poller()` + migraciones en import-time
`main_unificado.py:136-138` ejecuta:
```python
platform_init_db()
simco_init_db()
start_poller()
```
Esto sucede **al importar el módulo**, no en el lifespan. Si la BD no está lista aún (Railway a veces
tarda en provisionar), el import falla y el contenedor no arranca. Además `start_poller()` usa
`asyncio.create_task()` fuera de contexto async (aunque parece funcionar en la práctica).

### 🟡 MENOR 7 — Assets del login
La pantalla de login usa `/images/login/login.png` y `/images/login/logo.webp`. Estos archivos están
en `data_datcorr/frontend/public/images/login/`. Si ese frontend no se sirve desde el backend web,
las imágenes no cargarán en producción. Habrá que copiar esos assets a donde el backend los sirva.

---

## 5. Plan de acción concreto

### Fase 0 — Decisiones previas (responder antes de ejecutar)

- [ ] **P0.1**: ¿La app web principal es `data_datcorr/frontend/` (Login + Dashboard web) o
      `simco_v01/frontend/` (solicitudes/respuestas)?
- [ ] **P0.2**: ¿Se despliega una sola base de datos PostgreSQL en Railway que contenga los tres
      schemas (`platform`, `simco`, `datcorr`), o tres bases separadas?
- [ ] **P0.3**: ¿WebSocket es necesario en producción? Si sí, hay que instalar `websockets` y
      considerar que 1 réplica no escala el poller.

### Fase 1 — Preparar el repositorio para Railway

1. **Crear `Dockerfile` en la raíz** (`C:\plataforma\Dockerfile`):
   ```dockerfile
   # Etapa 1: Frontend SIMCO
   FROM node:20 AS simco-frontend
   WORKDIR /app/simco_v01/frontend
   COPY simco_v01/frontend/package*.json ./
   RUN npm ci
   COPY simco_v01/frontend/ ./
   RUN npm run build

   # Etapa 2: Frontend DATCORR (si aplica según P0.1)
   FROM node:20 AS datcorr-frontend
   WORKDIR /app/data_datcorr/frontend
   COPY data_datcorr/frontend/package*.json ./
   RUN npm ci
   COPY data_datcorr/frontend/ ./
   RUN npm run build

   # Etapa 3: Backend Python
   FROM python:3.13-slim
   WORKDIR /app

   # Copiar código fuente (paquetes planos, sin setup.py)
   COPY platformcore/ ./platformcore/
   COPY simco_v01/backend/ ./simco_v01/backend/
   COPY data_datcorr/backend/ ./data_datcorr/backend/
   COPY --from=simco-frontend /app/simco_v01/frontend/dist ./simco_v01/frontend/dist
   COPY --from=datcorr-frontend /app/data_datcorr/frontend/dist ./data_datcorr/frontend/dist

   # Instalar dependencias web (SIN PySide6)
   COPY requirements-web.txt .
   RUN pip install --no-cache-dir -r requirements-web.txt

   # Variables de entorno por defecto
   ENV DB_ENGINE=postgres
   ENV PLATFORM_DB_ENGINE=postgres

   EXPOSE 8000
   WORKDIR /app/data_datcorr
   CMD ["sh", "-c", "uvicorn backend.main_unificado:app --host 0.0.0.0 --port ${PORT:-8000}"]
   ```

2. **Crear `requirements-web.txt`** (sin PySide6, con versiones compatibles):
   ```
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
   ```

3. **Crear `railway.json` en la raíz:**
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

4. **Crear `.dockerignore` en la raíz:**
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
   ```

### Fase 2 — Ajustes al código

5. **Mover inicialización de BD a lifespan** (opcional pero recomendado):
   En `main_unificado.py`, cambiar las líneas 136-138 de import-time a un `lifespan`:
   ```python
   from contextlib import asynccontextmanager

   @asynccontextmanager
   async def lifespan(app: FastAPI):
       try:
           platform_init_db()
           simco_init_db()
           start_poller()
       except Exception as e:
           print(f"[WARN] DB init error (will retry on next request): {e}")
       yield

   app = FastAPI(..., lifespan=lifespan)
   # Eliminar las líneas 136-138 de import-time
   ```

6. **Servir el frontend datcorr** (si la respuesta a P0.1 es afirmativa):
   Agregar en `main_unificado.py`:
   ```python
   datcorr_dist = os.path.join(
       os.path.dirname(__file__), "..", "frontend", "dist"
   )
   if os.path.isdir(datcorr_dist):
       @app.get("/app/{full_path:path}")
       async def serve_datcorr_frontend(full_path: str):
           file_path = os.path.join(datcorr_dist, full_path)
           if os.path.isfile(file_path):
               return FileResponse(file_path)
           return FileResponse(os.path.join(datcorr_dist, "index.html"))
   ```
   Y copiar assets de login (`images/login/*`) a la carpeta `data_datcorr/frontend/public/` → `dist/`.

7. **Configurar CORS para Railway:**
   En `main_unificado.py:69-77`, agregar origen de Railway como variable de entorno:
   ```python
   origins = [
       "http://localhost:5173",
       "http://127.0.0.1:5173",
   ]
   public_url = os.getenv("PUBLIC_URL", "")
   railway_url = os.getenv("RAILWAY_URL", "")
   if public_url:
       origins.append(public_url)
   if railway_url:
       origins.append(railway_url)
   ```

### Fase 3 — Variables de entorno en Railway

8. **Setear en Railway** (Plugin PostgreSQL + variables manuales):
   ```
   # Postgres (Railway plugin) — usado por simco
   DB_ENGINE=postgres
   DATABASE_URL=${{Postgres.DATABASE_URL}}    # Railway injecta automáticamente

   # Platformcore DB
   PLATFORM_DB_ENGINE=postgres
   PLATFORM_DB_HOST=${{Postgres.HOST}}
   PLATFORM_DB_PORT=${{Postgres.PORT}}
   PLATFORM_DB_NAME=${{Postgres.DATABASE}}    # o un nombre fijo como "platform"
   PLATFORM_DB_USER=${{Postgres.USER}}
   PLATFORM_DB_PASSWORD=${{Postgres.PASSWORD}}

   # JWT
   JWT_SECRET_KEY=<generar secreto fuerte>
   SECRET_KEY=<generar secreto fuerte>

   # URLs
   PUBLIC_URL=https://<proyecto>.railway.app
   RAILWAY_URL=https://<proyecto>.railway.app
   ```

### Fase 4 — Build y validación

9. **Build local de prueba:**
   ```bash
   docker build -t plataforma -f Dockerfile .
   docker run --rm -p 8000:8000 -e DATABASE_URL=... -e JWT_SECRET_KEY=test plataforma
   ```

10. **Verificar endpoints:**
    - `GET /health` → 200
    - `GET /api/health` → 200
    - `GET /simco/` → HTML del frontend SIMCO
    - `GET /docs` → Swagger UI
    - `POST /auth/login` → login funciona

### Fase 5 — Post-deploy

11. **Railway Job para seed de admin SIMCO** (opcional, si no existe usuario en BD):
    ```bash
    cd data_datcorr && python -c "
    import sys
    sys.path.insert(0, '/app')
    sys.path.insert(0, '/app/simco_v01/backend')
    from app.db.seed import create_admin
    create_admin()
    "
    ```
    Con env vars: `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_FULLNAME`.

---

## 6. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| PySide6 en requirements si se usa lista completa | Build falla | Usar `requirements-web.txt` separado |
| BD no lista al iniciar | Contenedor no arranca | Mover `init_db()` a `lifespan` con try/except |
| Dos frontends compitiendo por ruta raíz | Confusión URL | Decidir cuál es el principal (P0.1) |
| WebSocket poller con múltiples réplicas | Broadcast duplicados | Limitar a 1 réplica o rediseñar con Redis pub/sub |
| Assets de login no encontrados | Login sin imágenes | Buildear `data_datcorr/frontend` y servir desde el backend |
| Secrets hardcodeados en config.py | Inseguro | Setear `JWT_SECRET_KEY` fuerte en Railway |

---

## 7. Preguntas pendientes para definir antes de ejecutar

1. **¿El frontend principal para el usuario final es `simco_v01/frontend/` (solicitudes/respuestas)
   o `data_datcorr/frontend/` (login + dashboard web + reportes)?**
   - Si es `data_datcorr/frontend/`: hay que buildearlo y servirlo desde `main_unificado.py`.
     Los assets del login (`login.png`, `logo.webp`) se copiarán automáticamente.
   - Si es `simco_v01/frontend/`: el login rediseñado (Login.jsx) solo se ve desde la app de
     escritorio, no desde la web. La web SIMCO tiene su propio login (`Login.tsx`).

2. **¿Una sola base de datos Postgres con tablas separadas por schema, o tres bases distintas?**

3. **¿Se necesita WebSocket en producción?** Si no, podemos desactivar `start_poller()` y
   eliminar la dependencia de `websockets`.

4. **¿Queremos que `main_unificado.py` sirva también la API docs (`/docs`) expuesta públicamente
   o solo en desarrollo?**
