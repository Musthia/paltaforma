from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from platformcore.database import get_db
from platformcore.dependencies import require_role
from platformcore.services.security import PermissionService
from platformcore.models.identity import PlatformUser

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/")
def list_permissions(
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
):
    perms = PermissionService.list_permissions(db)
    return [{"id": p.id, "code": p.code, "description": p.description, "module": p.module} for p in perms]


@router.get("/me")
def my_permissions(
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
    db: Session = Depends(get_db),
):
    perms = PermissionService.get_user_permissions(db, current_user.id)
    return {"permissions": perms}

