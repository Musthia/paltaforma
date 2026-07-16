from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from platformcore.database import get_db
from platformcore.dependencies import get_current_user, require_permission, require_role
from platformcore.schemas.identity import (
    UserCreateRequest, UserUpdateRequest, UserResponse,
)
from platformcore.services.security import UserService, PermissionService
from platformcore.services.audit import AuditService
from platformcore.models.identity import PlatformUser
from platformcore.exceptions import NotFoundError, ConflictError

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str = "",
    role: str = "",
    is_active: bool = None,
    sort_by: str = "id",
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
):
    result = UserService.list_users(
        db=db, page=page, limit=limit, search=search,
        role=role, is_active=is_active,
        sort_by=sort_by, order=order, include_inactive=True,
    )
    return result


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(get_current_user),
):
    try:
        return UserService.get_user(db, user_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")


@router.post("/", response_model=UserResponse)
def create_user(
    data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
):
    try:
        user = UserService.create_user(db, data)
        AuditService.record(
            db=db, user_id=current_user.id, username=current_user.username,
            action="CREATE_USER", entity="user", entity_id=user.id,
            detail=f"Usuario {user.username} creado",
        )
        return user
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=e.detail)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
):
    try:
        user = UserService.update_user(db, user_id, data)
        AuditService.record(
            db=db, user_id=current_user.id, username=current_user.username,
            action="UPDATE_USER", entity="user", entity_id=user.id,
            detail=f"Usuario {user.username} actualizado",
        )
        return user
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=e.detail)


@router.delete("/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
):
    try:
        user = UserService.deactivate_user(db, user_id)
        AuditService.record(
            db=db, user_id=current_user.id, username=current_user.username,
            action="DEACTIVATE_USER", entity="user", entity_id=user.id,
            detail=f"Usuario {user.username} desactivado",
        )
        return {"success": True, "mensaje": "Usuario desactivado."}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=e.detail)


@router.patch("/{user_id}/reactivate")
def reactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
):
    try:
        user = UserService.reactivate_user(db, user_id)
        AuditService.record(
            db=db, user_id=current_user.id, username=current_user.username,
            action="REACTIVATE_USER", entity="user", entity_id=user.id,
            detail=f"Usuario {user.username} reactivado",
        )
        return {"success": True, "mensaje": "Usuario reactivado."}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
