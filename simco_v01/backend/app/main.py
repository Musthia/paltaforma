import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.solicitudes import router as solicitudes_router
from app.api.routes.respuestas import router as respuestas_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.ws import router as ws_router, start_poller
from app.api.routes.buscar import router as buscar_router
from app.api.routes.notificaciones import router as notificaciones_router
from app.api.routes.messages import router as messages_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed admin (envuelto en try para no bloquear startup)
    try:
        from app.db.seed import create_admin
        create_admin()
    except Exception as e:
        print(f"[SIMCO] Seed postergado: {e}")
    start_poller()
    yield


app = FastAPI(title="SIGE API", lifespan=lifespan)

# ── CORS ───────────────────────────────────────────────────────────
# Cambia PUBLIC_URL por tu dominio real (ej: "https://simco.tudominio.com")
_public_url = os.getenv("PUBLIC_URL", "")

_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.109.116:5173",
]
if _public_url:
    _origins.append(_public_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rutas de la API ───────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(solicitudes_router)
app.include_router(respuestas_router)
app.include_router(dashboard_router)
app.include_router(ws_router)
app.include_router(buscar_router)
app.include_router(notificaciones_router)
app.include_router(messages_router)

# ── Health check (debe ir ANTES del catch-all SPA) ──────────────
@app.get("/api/health")
def health():
    return {"message": "SIGE funcionando"}

# ── Servir frontend compilado (producción) ─────────────────────────
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")

if os.path.isdir(frontend_dist):
    # Archivos estáticos (JS, CSS, imágenes)
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Favicon y otros archivos raíz
    @app.get("/favicon.svg")
    async def favicon():
        path = os.path.join(frontend_dist, "favicon.svg")
        if os.path.isfile(path):
            return FileResponse(path)
        resp = FileResponse(os.path.join(frontend_dist, "index.html"))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp

    # SPA fallback: cualquier ruta que no sea API → index.html
    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        resp = FileResponse(os.path.join(frontend_dist, "index.html"))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp

    print(f"[SIMCO] Sirviendo frontend desde: {frontend_dist}")