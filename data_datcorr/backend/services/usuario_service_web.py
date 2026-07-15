import logging

from database.conexion import (
    SessionLocal
)

from database.modelos import (
    Usuario
)

from utils.hash import (
    hash_password
)

# -----------------------------------
# CREAR USUARIO WEB
# -----------------------------------

def crear_usuario_web(

    nombre,
    apellido,
    usuario,
    password,
    rol,
    nivel_seguridad,
    activo=True
):

    logging.debug(
        f"WEB creando usuario: "
        f"{usuario}"
    )

    session = SessionLocal()

    try:

        # -----------------------------
        # VALIDAR DUPLICADO
        # -----------------------------

        existe = (
            session.query(Usuario)
            .filter(
                Usuario.usuario == usuario
            )
            .first()
        )

        if existe:

            logging.warning(
                f"Usuario duplicado: "
                f"{usuario}"
            )

            return {
                "success": False,
                "mensaje": (
                    "Usuario ya existe."
                )
            }

        # -----------------------------
        # HASH PASSWORD
        # -----------------------------

        password_hash = (
            hash_password(password)
        )

        # -----------------------------
        # NUEVO USUARIO
        # -----------------------------

        nuevo_usuario = Usuario(

            nombre=nombre,

            apellido=apellido,

            usuario=usuario,

            password_hash=password_hash,

            rol=rol,

            nivel_seguridad=(
                nivel_seguridad
            ),

            activo=activo,

            es_superusuario=False
        )

        session.add(
            nuevo_usuario
        )

        session.commit()

        session.refresh(
            nuevo_usuario
        )

        logging.debug(
            f"Usuario WEB creado ID: "
            f"{nuevo_usuario.id}"
        )

        return {
            "success": True,
            "mensaje": (
                "Usuario creado."
            ),
            "usuario_id": (
                nuevo_usuario.id
            )
        }

    except Exception as e:

        session.rollback()

        logging.exception(
            "Error creando usuario WEB"
        )

        return {
            "success": False,
            "mensaje": str(e)
        }

    finally:

        session.close()