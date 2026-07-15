from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.user_service import list_users, get_user, create_user, update_user, delete_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def read_me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }


@router.get("/")
def listar_usuarios(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    require_roles("admin")(user)
    return list_users(db)


@router.get("/{user_id}")
def obtener_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    require_roles("admin")(user)
    u = get_user(db, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u


@router.post("/")
def crear_usuario(
    data: UserCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    require_roles("admin")(user)
    return create_user(db, data, user.id)


@router.put("/{user_id}")
def actualizar_usuario(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    require_roles("admin")(user)
    u = update_user(db, user_id, data, user.id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o es el administrador maestro")
    return u


@router.delete("/{user_id}")
def eliminar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    require_roles("admin")(user)
    ok = delete_user(db, user_id, user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o es el administrador maestro")
    return {"detail": "Usuario eliminado"}
