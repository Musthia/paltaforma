# -----------------------------------
# NIVELES MÍNIMOS POR MÓDULO
# -----------------------------------

MODULO_CONSULTAS = 1

MODULO_CARGAS = 3

MODULO_REPORTES = 5

MODULO_USUARIOS = 10

MODULO_CONFIGURACION = 10

from utils.user_helpers import get_usuario_attr


# -----------------------------------
# VALIDAR NIVEL SEGURIDAD
# -----------------------------------

def tiene_nivel(
    usuario,
    nivel_requerido
):

    return (
        get_usuario_attr(
            usuario,
            "nivel_seguridad",
            0
        )
        >= nivel_requerido
    )


# -----------------------------------
# VALIDAR ACCESO MÓDULO
# -----------------------------------

def tiene_permiso(
    usuario,
    modulo_requerido
):

    return (
        get_usuario_attr(
            usuario,
            "nivel_seguridad",
            0
        )
        >= modulo_requerido
    )


# -----------------------------------
# OBTENER DESCRIPCIÓN NIVEL
# -----------------------------------

def obtener_descripcion_nivel(
    nivel
):

    if nivel >= 10:
        return "Administrador"

    elif nivel >= 5:
        return "Supervisor"

    elif nivel >= 3:
        return "Operador"

    return "Consulta"

from database.conexion import SessionLocal

from database.modelos import Permiso

# -----------------------------------
# LISTAR PERMISOS
# -----------------------------------

def listar_permisos():

    db = SessionLocal()

    try:

        permisos = (
            db.query(Permiso)
            .order_by(Permiso.codigo)
            .all()
        )

        return permisos

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()