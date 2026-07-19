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

# ═══════════════════════════════════════════════════════════════════════
# LIFESPAN (inicialización segura)
# ═══════════════════════════════════════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        platform_init_db()
        simco_init_db()
        start_poller()
        print("[UNIFICADO] Tablas inicializadas y WebSocket poller iniciado")
    except Exception as e:
        print(f"[UNIFICADO] WARN: Error en inicialización (BD puede no estar lista): {e}")
    yield

# ═══════════════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════════════
_is_prod = os.getenv("ENVIRONMENT", "development").lower() == "production"

app = FastAPI(
    title="Plataforma Unificada DATCORR + SIMCO",
    version="1.0.0",
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware, max_attempts=5, window_seconds=300, ban_seconds=900
)
app.add_middleware(JWTMiddleware)

# ── Exception handlers ────────────────────────────────────────────────
app.add_exception_handler(DatcorrException, datcorr_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ═══════════════════════════════════════════════════════════════════════
# ROUTERS PLATFORM
# ═══════════════════════════════════════════════════════════════════════
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(audit_router)

# ═══════════════════════════════════════════════════════════════════════
# ROUTERS DATCORR
# ═══════════════════════════════════════════════════════════════════════
app.include_router(datcorr_admin_router)
app.include_router(datcorr_database_router)
app.include_router(datcorr_dashboard_router)
app.include_router(datcorr_reportes_router)

# ═══════════════════════════════════════════════════════════════════════
# ROUTERS SIMCO
# ═══════════════════════════════════════════════════════════════════════
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
        resp = FileResponse(os.path.join(_datcorr_dist, "index.html"))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(_datcorr_dist, "index.html"))

    print(f"[UNIFICADO] Sirviendo frontend DATCORR desde: {_datcorr_dist}")
else:
    @app.get("/")
    def root_fallback():
        return {
            "mensaje": "Plataforma Unificada DATCORR + SIMCO",
            "version": "1.0.0",
            "modules": ["datcorr", "simco"],
        }

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
        resp = FileResponse(os.path.join(_simco_dist, "index.html"))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp

    @app.get("/favicon.svg")
    async def serve_favicon():
        return FileResponse(os.path.join(_simco_dist, "favicon.svg"))

    @app.get("/icons.svg")
    async def serve_icons():
        return FileResponse(os.path.join(_simco_dist, "icons.svg"))

    print(f"[UNIFICADO] Sirviendo frontend SIMCO desde: {_simco_dist}")
