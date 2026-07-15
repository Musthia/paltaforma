from database.conexion import SessionLocal

from database.modelos import (
    Usuario,
    Permiso,
    UsuarioPermiso
)

#raise Exception("OLD ORM USAGE DETECTED")

# -----------------------------------
# ASIGNAR PERMISO
# -----------------------------------

def asignar_permiso_usuario(
    usuario_id,
    codigo_permiso
):

    db = SessionLocal()

    try:

        permiso = (
            db.query(Permiso)
            .filter(
                Permiso.codigo ==
                codigo_permiso
            )
            .first()
        )

        if not permiso:

            return {
                "success": False,
                "mensaje": "Permiso inexistente."
            }

        existe = (
            db.query(UsuarioPermiso)
            .filter(
                UsuarioPermiso.usuario_id ==
                usuario_id,

                UsuarioPermiso.permiso_id ==
                permiso.id
            )
            .first()
        )

        if existe:

            return {
                "success": False,
                "mensaje": "Permiso ya asignado."
            }

        nuevo = UsuarioPermiso(
            usuario_id=usuario_id,
            permiso_id=permiso.id
        )

        db.add(nuevo)

        db.commit()

        return {
            "success": True,
            "mensaje": "Permiso asignado."
        }

    except Exception as e:

        db.rollback()

        return {
            "success": False,
            "mensaje": str(e)
        }

    finally:

        db.close()

# -----------------------------------
# VALIDAR PERMISO
# -----------------------------------

def usuario_tiene_permiso(
    usuario_id,
    codigo_permiso
):

    db = SessionLocal()

    try:

        permiso = (
            db.query(UsuarioPermiso)
            .join(Permiso)
            .filter(
                UsuarioPermiso.usuario_id ==
                usuario_id,

                Permiso.codigo ==
                codigo_permiso
            )
            .first()
        )

        return permiso is not None

    finally:

        db.close()

# -----------------------------------
# QUITAR PERMISO
# -----------------------------------

def quitar_permiso_usuario(
    usuario_id,
    codigo_permiso
):

    db = SessionLocal()

    try:

        permiso = (
            db.query(Permiso)
            .filter(
                Permiso.codigo ==
                codigo_permiso
            )
            .first()
        )

        if not permiso:

            return {
                "success": False,
                "mensaje": "Permiso inexistente."
            }

        relacion = (
            db.query(UsuarioPermiso)
            .filter(
                UsuarioPermiso.usuario_id ==
                usuario_id,

                UsuarioPermiso.permiso_id ==
                permiso.id
            )
            .first()
        )

        if not relacion:

            return {
                "success": False,
                "mensaje": (
                    "El usuario no posee "
                    "ese permiso."
                )
            }

        db.delete(relacion)

        db.commit()

        return {
            "success": True,
            "mensaje": "Permiso removido."
        }

    except Exception as e:

        db.rollback()

        return {
            "success": False,
            "mensaje": str(e)
        }

    finally:

        db.close()

# -----------------------------------
# LISTAR PERMISOS USUARIO
# -----------------------------------

def listar_permisos_usuario(
    usuario_id
):

    db = SessionLocal()

    try:

        permisos = (
            db.query(Permiso.codigo)
            .join(
                UsuarioPermiso,
                UsuarioPermiso.permiso_id ==
                Permiso.id
            )
            .filter(
                UsuarioPermiso.usuario_id ==
                usuario_id
            )
            .all()
        )

        return [
            permiso[0]
            for permiso in permisos
        ]

    finally:

        db.close()

import logging

from sqlalchemy.orm import joinedload

from database.conexion import SessionLocal

from database.modelos import (
    Usuario,
    Permiso
)

def obtener_permisos_usuario(usuario_id):

    logging.debug(
        f"Obteniendo permisos usuario ID: "
        f"{usuario_id}"
    )

    session = SessionLocal()

    try:

        usuario = (
            session.query(Usuario)
            .options(
                joinedload(
                    Usuario.usuario_permisos
                ).joinedload(
                    UsuarioPermiso.permiso
                )
            )
            .filter(
                Usuario.id == usuario_id
            )
            .first()
        )

        if not usuario:

            logging.warning(
                "Usuario no encontrado."
            )

            return []

        permisos = [
            relacion.permiso
            for relacion
            in usuario.usuario_permisos
        ]

        logging.debug(
            f"Permisos encontrados: "
            f"{len(permisos)}"
        )

        return permisos

    except Exception:

        logging.exception(
            "Error obteniendo permisos usuario"
        )

        return []

    finally:

        session.close()