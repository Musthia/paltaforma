from sqlalchemy.orm import Session
from sqlalchemy import or_

from platformcore.models.identity import PlatformUser
from platformcore.services.security import UserService, RoleService
from platformcore.security import hash_password
from platformcore.logger import logger
from platformcore.exceptions import NotFoundError, ConflictError

from backend.services.auditoria_service import registrar_auditoria


def listar_usuarios_web(
    db: Session,
    page: int = 1,
    limit: int = 20,
    search: str = "",
    rol: str = "",
    activo: bool = None,
    incluir_inactivos: bool = False,
    sort_by: str = "id",
    order: str = "asc",
):
    result = UserService.list_users(
        db=db,
        page=page,
        limit=limit,
        search=search,
        role=rol,
        is_active=activo,
        sort_by=sort_by,
        order=order,
        include_inactive=incluir_inactivos,
    )
    return {
        "usuarios": result["users"],
        "total": result["total"],
        "pages": result["pages"],
        "page": result["page"],
        "limit": result["limit"],
    }


def crear_usuario_web(db: Session, datos):
    try:
        user = UserService.create_user(db, datos)
        registrar_auditoria(
            db=db, usuario=datos.usuario, accion="CREATE",
            tabla="usuarios", registro_id=user.id,
            detalle=f"Usuario creado: {datos.usuario}",
        )
        return {"success": True, "mensaje": "Usuario creado.", "usuario_id": user.id}
    except ConflictError as e:
        return {"success": False, "mensaje": e.detail}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando usuario: {e}")
        return {"success": False, "mensaje": "Error interno."}


def actualizar_usuario_web(db: Session, usuario_id: int, datos):
    try:
        before = UserService.get_user(db, usuario_id)
        before_data = {
            "nombre": before.full_name or "",
            "apellido": "",
            "usuario": before.username,
            "rol": before.role,
            "nivel_seguridad": before.nivel_seguridad,
            "activo": before.is_active,
        }

        user = UserService.update_user(db, usuario_id, datos)

        after_data = {
            "nombre": user.full_name or "",
            "apellido": "",
            "usuario": user.username,
            "rol": user.role,
            "nivel_seguridad": user.nivel_seguridad,
            "activo": user.is_active,
        }

        registrar_auditoria(
            db=db, usuario=user.username, accion="UPDATE",
            tabla="usuarios", registro_id=user.id,
            detalle=f"ANTES: {before_data} | DESPUES: {after_data}",
        )
        return {"success": True, "mensaje": "Usuario actualizado."}
    except NotFoundError:
        return {"success": False, "mensaje": "Usuario no encontrado."}
    except ConflictError as e:
        return {"success": False, "mensaje": e.detail}
    except Exception as e:
        db.rollback()
        logger.error(f"Error UPDATE usuario: {e}")
        return {"success": False, "mensaje": "Error interno."}


def desactivar_usuario_web(db: Session, usuario_id: int, usuario_actual: str):
    try:
        user = UserService.deactivate_user(db, usuario_id)
        registrar_auditoria(
            db=db, usuario=usuario_actual, accion="DELETE_LOGICO",
            tabla="usuarios", registro_id=user.id,
            detalle=f"Usuario desactivado: {user.username}",
        )
        return {"success": True, "mensaje": "Usuario desactivado."}
    except NotFoundError:
        registrar_auditoria(
            db=db, usuario=usuario_actual, accion="DELETE_LOGICO_ERROR",
            tabla="usuarios", registro_id=usuario_id,
            detalle="Intento eliminar usuario inexistente",
        )
        return {"success": False, "mensaje": "Usuario no existe."}
    except ConflictError as e:
        registrar_auditoria(
            db=db, usuario=usuario_actual, accion="DELETE_LOGICO_ERROR",
            tabla="usuarios", registro_id=usuario_id, detalle=e.detail,
        )
        return {"success": False, "mensaje": e.detail}
    except Exception as e:
        db.rollback()
        logger.error(f"Error desactivar usuario: {e}")
        return {"success": False, "mensaje": "Error interno."}


def reactivar_usuario_web(db: Session, usuario_id: int, usuario_actual: str):
    try:
        user = UserService.reactivate_user(db, usuario_id)
        registrar_auditoria(
            db=db, usuario=usuario_actual, accion="REACTIVATE",
            tabla="usuarios", registro_id=user.id,
            detalle=f"Usuario reactivado: {user.username}",
        )
        return {"success": True, "mensaje": "Usuario reactivado."}
    except NotFoundError:
        return {"success": False, "mensaje": "Usuario no existe."}
    except Exception as e:
        db.rollback()
        logger.error(f"Error reactivar usuario: {e}")
        return {"success": False, "mensaje": "Error interno."}
