from sqlalchemy.orm import Session

from platformcore.services.security import RoleService as PlatformRoleService
from platformcore.logger import logger

ROL_POR_DEFECTO = "Consulta"


def listar_roles(db: Session):
    return PlatformRoleService.list_roles(db)


def obtener_rol_por_nombre(db: Session, nombre: str):
    return PlatformRoleService.get_role_by_name(db, nombre)


def asignar_rol_usuario(db: Session, usuario_id: int, rol_nombre: str):
    PlatformRoleService.assign_role_to_user(db, usuario_id, rol_nombre)


def obtener_roles_usuario(db: Session, usuario_id: int):
    return PlatformRoleService.get_user_roles(db, usuario_id)


def migrar_rol_columna_a_relacion(db: Session, usuario_id: int):
    from database.modelos import Usuario
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario or not usuario.rol:
        return
    asignar_rol_usuario(db, usuario.id, usuario.rol)
