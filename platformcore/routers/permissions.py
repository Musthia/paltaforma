from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from platformcore.database import get_db
from platformcore.dependencies import require_role
from platformcore.services.security import PermissionService
from platformcore.models.identity import PlatformUser

router = APIRouter(prefix="/permissions", tags=["Permissions"])


class AssignRemoveRequest(BaseModel):
    user_id: int
    permission_code: str


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


@router.get("/user/{user_id}")
def user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
):
    perms = PermissionService.get_user_permissions(db, user_id)
    return {"permissions": perms}


@router.post("/assign")
def assign_permission(
    body: AssignRemoveRequest,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
):
    result = PermissionService.assign_permission(db, body.user_id, body.permission_code)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["mensaje"])
    return result


@router.post("/remove")
def remove_permission(
    body: AssignRemoveRequest,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
):
    result = PermissionService.remove_permission(db, body.user_id, body.permission_code)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["mensaje"])
    return result

