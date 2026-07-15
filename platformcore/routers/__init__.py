from platformcore.routers.auth import router as auth_router
from platformcore.routers.users import router as users_router
from platformcore.routers.roles import router as roles_router
from platformcore.routers.permissions import router as permissions_router
from platformcore.routers.audit import router as audit_router

__all__ = [
    "auth_router",
    "users_router",
    "roles_router",
    "permissions_router",
    "audit_router",
]
