from sqlalchemy.orm import Session

from database.modelos_roles import (
    Rol,
    UsuarioRol
)

from database.modelos import Usuario

from backend.core.logger import logger


ROL_POR_DEFECTO = "Consulta"


def listar_roles(db: Session):

    roles = db.query(Rol).order_by(
        Rol.nivel_minimo.desc()
    ).all()

    logger.info(
        f"Roles listados: {len(roles)}"
    )

    return roles


def obtener_rol_por_nombre(
    db: Session, nombre: str
):

    return db.query(Rol).filter(
        Rol.nombre == nombre
    ).first()


def asignar_rol_usuario(
    db: Session,
    usuario_id: int,
    rol_nombre: str
):
    rol = obtener_rol_por_nombre(db, rol_nombre)
    if not rol:
        logger.warning(
            f"Rol '{rol_nombre}' no encontrado, "
            f"usando '{ROL_POR_DEFECTO}'"
        )
        rol = obtener_rol_por_nombre(
            db, ROL_POR_DEFECTO
        )
        if not rol:
            return

    existente = db.query(UsuarioRol).filter(
        UsuarioRol.usuario_id == usuario_id
    ).first()

    if existente:
        existente.rol_id = rol.id
    else:
        db.add(UsuarioRol(
            usuario_id=usuario_id,
            rol_id=rol.id
        ))

    db.flush()
    logger.info(
        f"Rol '{rol_nombre}' asignado a usuario {usuario_id}"
    )


def obtener_roles_usuario(
    db: Session, usuario_id: int
):
    registros = db.query(UsuarioRol).filter(
        UsuarioRol.usuario_id == usuario_id
    ).all()

    roles = []
    for ur in registros:
        rol = db.query(Rol).filter(
            Rol.id == ur.rol_id
        ).first()
        if rol:
            roles.append(rol)

    return roles


def migrar_rol_columna_a_relacion(
    db: Session, usuario_id: int
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not usuario or not usuario.rol:
        return

    asignar_rol_usuario(
        db, usuario.id, usuario.rol
    )
