from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers compartidos de platformcore
from platformcore.routers import (
    auth_router,
    users_router,
    roles_router,
    permissions_router,
    audit_router,
)

# Routers específicos del módulo DATCORR
from backend.routers.admin_router import router as admin_router
from backend.routers.database_router import router as database_router
from backend.routers.dashboard_router import router as dashboard_router
from backend.routers.reportes_router import router as reportes_router

from backend.core.exceptions import DatcorrException
from backend.core.handlers import (
    datcorr_exception_handler,
    generic_exception_handler,
)

from backend.middleware.jwt_middleware import JWTMiddleware
from backend.middleware.rate_limit_middleware import RateLimitMiddleware


app = FastAPI(title="DatCorr API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware, max_attempts=5, window_seconds=300, ban_seconds=900)
app.add_middleware(JWTMiddleware)

app.add_exception_handler(DatcorrException, datcorr_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routers compartidos (Platform)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(audit_router)

# Routers específicos del módulo DATCORR
app.include_router(admin_router)
app.include_router(database_router)
app.include_router(dashboard_router)
app.include_router(reportes_router)


@app.get("/")
def root():
    return {"mensaje": "DatCorr API funcionando"}


@app.get("/health")
def health():
    return {"status": "ok"}
