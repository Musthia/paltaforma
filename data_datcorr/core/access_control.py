import logging

from core.session_manager import SessionManager
from utils.user_helpers import get_usuario_attr

#print(SessionManager)
#print(dir(SessionManager))

# -----------------------------------
# VALIDAR SESIÓN
# -----------------------------------

def validar_sesion():

    if not SessionManager.validar_sesion():

        logging.warning(
            "Acceso denegado: "
            "sesión inválida."
        )

        return False

    return True

# -----------------------------------
# VALIDAR NIVEL
# -----------------------------------

def validar_nivel(nivel_requerido):

    if not SessionManager.validar_sesion():

        logging.warning("Acceso denegado: sesión inválida.")
        return False

    usuario_actual = SessionManager.obtener_usuario()

    # SUPERUSUARIO BYPASS TOTAL
    if get_usuario_attr(usuario_actual, "es_superusuario", False):

        logging.debug("SUPERUSUARIO: bypass niveles.")
        return True

    nivel_actual = SessionManager.obtener_nivel_seguridad()

    logging.debug(
        f"Validando nivel: actual={nivel_actual} requerido={nivel_requerido}"
    )

    if nivel_actual < nivel_requerido:

        logging.warning(
            f"Nivel insuficiente: {nivel_actual} < {nivel_requerido}"
        )

        return False

    logging.debug("Acceso autorizado por nivel.")
    return True

def usuario():
    return SessionManager.obtener_usuario()

    get_usuario_attr(usuario(), "rol")