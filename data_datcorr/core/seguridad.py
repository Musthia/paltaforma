from PySide6.QtWidgets import QMessageBox
from core.session_manager import SessionManager
from utils.user_helpers import get_usuario_attr
import logging


# -----------------------------------
# VALIDAR PERMISO (CORE ERP)
# -----------------------------------

def validar_permiso(parent, permiso, mensaje=None):

    logging.debug(f"Validando permiso: {permiso}")

    # -----------------------------------
    # VALIDAR SESIÓN ACTIVA
    # -----------------------------------

    if not SessionManager.validar_sesion():

        logging.warning("Sesión inválida.")

        QMessageBox.critical(
            parent,
            "Sesión",
            "Debe iniciar sesión para continuar."
        )

        return False

    # -----------------------------------
    # OBTENER USUARIO ACTUAL (HÍBRIDO SAFE)
    # -----------------------------------

    usuario_actual = SessionManager.obtener_usuario()

    # -----------------------------------
    # SUPERUSUARIO (BY-PASS TOTAL)
    # -----------------------------------

    if get_usuario_attr(usuario_actual, "es_superusuario", False):

        logging.debug("SUPERUSUARIO: bypass permisos.")

        return True

    # -----------------------------------
    # VALIDAR PERMISO ESPECÍFICO
    # -----------------------------------

    if not SessionManager.tiene_permiso(permiso):

        logging.warning(f"Permiso denegado: {permiso}")

        QMessageBox.warning(
            parent,
            "Permiso denegado",
            mensaje or f"No posee permisos para: {permiso}"
        )

        return False

    # -----------------------------------
    # ACCESO AUTORIZADO
    # -----------------------------------

    logging.debug(f"Permiso autorizado: {permiso}")

    return True


# -----------------------------------
# VALIDAR NIVEL DE SEGURIDAD
# -----------------------------------

def validar_nivel(parent, nivel_requerido):

    if not SessionManager.validar_sesion():

        QMessageBox.critical(
            parent,
            "Sesión",
            "Debe iniciar sesión para continuar."
        )

        return False

    usuario_actual = SessionManager.obtener_usuario()

    # SUPERUSUARIO BYPASS
    if get_usuario_attr(usuario_actual, "es_superusuario", False):

        logging.debug("SUPERUSUARIO: bypass niveles.")

        return True

    nivel_actual = SessionManager.obtener_nivel_seguridad()

    logging.debug(
        f"Validando nivel: "
        f"actual={nivel_actual} "
        f"requerido={nivel_requerido}"
    )

    if nivel_actual < nivel_requerido:

        logging.warning(
            f"Nivel insuficiente: "
            f"{nivel_actual} < {nivel_requerido}"
        )

        QMessageBox.warning(
            parent,
            "Acceso restringido",
            "No posee nivel de seguridad suficiente."
        )

        return False

    logging.debug("Acceso autorizado por nivel.")

    return True


# -----------------------------------
# VALIDAR ACCESO SIMPLE
# -----------------------------------

def validar_sesion():

    return SessionManager.validar_sesion()