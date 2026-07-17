"""
Backend Unificado DATCORR + SIMCO
Sirve ambos módulos desde un solo proceso FastAPI.
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

# ── Agregar SIMCO al path para poder importar sus routers ─────────────
SIMCO_BACKEND = os.path.join(os.path.dirname(__file__), "..", "..", "simco_v01", "backend")
if SIMCO_BACKEND not in sys.path:
    sys.path.insert(0, SIMCO_BACKEND)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# ── Platform Core (compartido) ─────────────────────────────────────────
from platformcore.routers import (
    auth_router,
    users_router,
    roles_router,
    permissions_router,
    audit_router,
)

# ── DATCORR module ─────────────────────────────────────────────────────
from backend.routers.admin_router import router as datcorr_admin_router
from backend.routers.database_router import router as datcorr_database_router
from backend.routers.dashboard_router import router as datcorr_dashboard_router
from backend.routers.reportes_router import router as datcorr_reportes_router

from backend.core.exceptions import DatcorrException
from backend.core.handlers import datcorr_exception_handler, generic_exception_handler

# ── SIMCO module ───────────────────────────────────────────────────────
from app.api.routes.solicitudes import router as simco_solicitudes_router
from app.api.routes.respuestas import router as simco_respuestas_router
from app.api.routes.dashboard import router as simco_dashboard_router
from app.api.routes.ws import router as simco_ws_router, start_poller
from app.api.routes.buscar import router as simco_buscar_router
from app.api.routes.notificaciones import router as simco_notificaciones_router
from app.api.routes.messages import router as simco_messages_router

# ── Middleware compartido ──────────────────────────────────────────────
from backend.middleware.jwt_middleware import JWTMiddleware
from backend.middleware.rate_limit_middleware import RateLimitMiddleware

# ═══════════════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Plataforma Unificada DATCORR + SIMCO",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
public_url = os.getenv("PUBLIC_URL", "")
if public_url:
    origins.append(public_url)

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
# ROUTERS PLATFORM (shared)
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

# ── Servir frontend compilado SIMCO (producción) ──────────────────────
frontend_dist = os.path.join(
    os.path.dirname(__file__), "..", "..", "simco_v01", "frontend", "dist"
)
if os.path.isdir(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/simco/assets", StaticFiles(directory=assets_dir), name="simco_assets")
        app.mount("/assets", StaticFiles(directory=assets_dir), name="simco_assets_root")

    @app.get("/simco")
    async def serve_simco_root():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/simco/{full_path:path}")
    async def serve_simco_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        resp = FileResponse(os.path.join(frontend_dist, "index.html"))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp

    @app.get("/favicon.svg")
    async def serve_favicon():
        return FileResponse(os.path.join(frontend_dist, "favicon.svg"))

    @app.get("/icons.svg")
    async def serve_icons():
        return FileResponse(os.path.join(frontend_dist, "icons.svg"))

    print(f"[UNIFICADO] Sirviendo SIMCO frontend desde: {frontend_dist}")


@app.get("/")
def root():
    return {
        "mensaje": "Plataforma Unificada DATCORR + SIMCO",
        "version": "1.0.0",
        "modules": ["datcorr", "simco"],
    }
