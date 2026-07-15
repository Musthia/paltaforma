from platformcore.services.security import UserService as PlatformUserService
from platformcore.services.audit import AuditService

MASTER_USERNAME = "Musthia"


def list_users(db):
    result = PlatformUserService.list_users(db, include_inactive=True)
    users = [u for u in result["users"] if u.username != MASTER_USERNAME]
    return users


def get_user(db, user_id: int):
    return PlatformUserService.get_user(db, user_id)


def create_user(db, data, current_user_id: int):
    user = PlatformUserService.create_user(db, data)
    AuditService.record(
        db=db, user_id=current_user_id, action="CREAR_USUARIO",
        entity="user", entity_id=user.id,
        detail=f"Usuario {user.username} creado con rol {user.role}",
        module="simco",
    )
    return user


def update_user(db, user_id: int, data, current_user_id: int):
    user = PlatformUserService.get_user(db, user_id)
    if user.username == MASTER_USERNAME:
        return None
    user = PlatformUserService.update_user(db, user_id, data)
    AuditService.record(
        db=db, user_id=current_user_id, action="ACTUALIZAR_USUARIO",
        entity="user", entity_id=user.id,
        detail=f"Usuario {user.username} actualizado",
        module="simco",
    )
    return user


def delete_user(db, user_id: int, current_user_id: int):
    from platformcore.exceptions import NotFoundError
    try:
        user = PlatformUserService.get_user(db, user_id)
        if user.username == MASTER_USERNAME:
            return False
        PlatformUserService.deactivate_user(db, user_id)
        AuditService.record(
            db=db, user_id=current_user_id, action="ELIMINAR_USUARIO",
            entity="user", entity_id=user_id,
            detail=f"Usuario {user.username} eliminado",
            module="simco",
        )
        return True
    except NotFoundError:
        return False
