from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from backend.routers.auth_router import router as auth_router
from backend.routers.admin_router import router as admin_router
from backend.routers.usuarios_router import router as usuarios_router
from backend.routers.database_router import router as database_router
from backend.routers.dashboard_router import router as dashboard_router
from backend.routers.reportes_router import router as reportes_router
from backend.routers.roles_router import router as roles_router
from backend.routers.permisos_router import router as permisos_router

from backend.core.exceptions import DatcorrException
from backend.core.handlers import (
    datcorr_exception_handler,
    generic_exception_handler
)

from backend.middleware.jwt_middleware import JWTMiddleware
from backend.middleware.rate_limit_middleware import RateLimitMiddleware

from fastapi.middleware.cors import CORSMiddleware


# -----------------------------------
# APP
# -----------------------------------

app = FastAPI(
    title="DatCorr API",
    version="1.0.0"
)

# -----------------------------------
# CORS
# -----------------------------------

origins = [
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# MIDDLEWARE GLOBAL JWT (FASE 6E)
# -----------------------------------

app.add_middleware(RateLimitMiddleware, max_attempts=5, window_seconds=300, ban_seconds=900)
app.add_middleware(JWTMiddleware)

# -----------------------------------
# HANDLERS GLOBALES
# -----------------------------------

app.add_exception_handler(
    DatcorrException,
    datcorr_exception_handler
)

app.add_exception_handler(
    Exception,
    generic_exception_handler
)

# -----------------------------------
# ROUTERS
# -----------------------------------

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(usuarios_router)
app.include_router(database_router)
app.include_router(dashboard_router)
app.include_router(reportes_router)
app.include_router(roles_router)
app.include_router(permisos_router)

# -----------------------------------
# ROOT
# -----------------------------------

@app.get("/")
def root():

    return {
        "mensaje": "DatCorr API funcionando"
    }

# -----------------------------------
# HEALTH
# -----------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok"
    }