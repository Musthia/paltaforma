from datetime import datetime
import logging

from services.usuarios_permisos_service import usuario_tiene_permiso

from utils.user_helpers import get_usuario_attr

from core.api_client import ApiClient
from core.api_database_client import ApiDatabaseClient
from core.api_reportes_client import ApiReportesClient
from core.api_usuarios_client import ApiUsuariosClient


class SessionManager:

    _usuario_actual = None
    _fecha_login = None
    _sesion_activa = False
    _permisos = []
    _api_client = None
    _db_client = None
    _reportes_client = None
    _usuarios_client = None

    # -----------------------------------
    # LOGIN
    # -----------------------------------

    @classmethod
    def login(cls, usuario: dict):

        cls._usuario_actual = usuario
        cls._fecha_login = datetime.now()
        cls._sesion_activa = True

        logging.debug(
            f"Sesión iniciada: "
            f"{get_usuario_attr(usuario,'usuario')}"
        )

    @classmethod
    def sync_from_api(cls):
        if not cls._api_client:
            return False
        try:
            data = cls._api_client.get("/auth/me")
            if data.get("success") is False:
                return False
            cls._usuario_actual = {
                "id": data.get("id"),
                "usuario": data.get("usuario"),
                "nombre": data.get("nombre"),
                "apellido": data.get("apellido"),
                "rol": data.get("rol"),
                "nivel_seguridad": data.get("nivel_seguridad", 0),
                "es_superusuario": data.get("es_superusuario", False),
            }
            cls._permisos = data.get("permisos", [])
            cls._sesion_activa = True
            return True
        except Exception:
            logging.warning("sync_from_api falló", exc_info=True)
            return False

    # -----------------------------------
    # VALIDAR SESIÓN
    # -----------------------------------

    @classmethod
    def validar_sesion(cls):

        return bool(cls._sesion_activa and cls._usuario_actual)    

    # -----------------------------------
    # LOGOUT
    # -----------------------------------

    @classmethod
    def logout(cls):

        cls._usuario_actual = None
        cls._fecha_login = None
        cls._sesion_activa = False
        cls._permisos = []

        logging.debug("Sesión finalizada")

    # -----------------------------------
    # OBTENER USUARIO
    # -----------------------------------

    @classmethod
    def obtener_usuario(cls):
        return cls._usuario_actual

    """ # -----------------------------------
    # VALIDAR SESIÓN
    # -----------------------------------

    @classmethod
    def hay_sesion(cls):
        return cls._sesion_activa
 """
    # -----------------------------------
    # FECHA LOGIN
    # -----------------------------------

    @classmethod
    def obtener_fecha_login(cls):
        return cls._fecha_login

    # -----------------------------------
    # NIVEL SEGURIDAD
    # -----------------------------------

    @classmethod
    def obtener_nivel_seguridad(cls):

        if not cls._usuario_actual:
            return 0

        return get_usuario_attr(
            cls._usuario_actual,
            "nivel_seguridad",
            0
        )

    # -----------------------------------
    # ROL
    # -----------------------------------

    @classmethod
    def obtener_rol(cls):

        if not cls._usuario_actual:
            return None

        return get_usuario_attr(
            cls._usuario_actual,
            "rol"
        )

    # -----------------------------------
    # PERMISOS
    # -----------------------------------

    @classmethod
    def tiene_permiso(cls, codigo_permiso):

        if not cls._usuario_actual:
            return False

        if cls.es_superusuario():
            return True

        if codigo_permiso in cls._permisos:
            return True

        return usuario_tiene_permiso(
            cls._usuario_actual.get("id"),
            codigo_permiso
        )
            
    @classmethod
    def es_superusuario(cls):

        if not cls._usuario_actual:
            return False

        return get_usuario_attr(
            cls._usuario_actual,
            "es_superusuario",
            False
        )

    @classmethod
    def obtener_usuario_id(cls):

        if not cls._usuario_actual:
            return None

        return get_usuario_attr(
            cls._usuario_actual,
            "id"
        )

    @classmethod
    def set_api_client(cls, client: ApiClient):
        cls._api_client = client
        cls._db_client = ApiDatabaseClient(client)
        cls._reportes_client = ApiReportesClient(client)
        cls._usuarios_client = ApiUsuariosClient(client)

    @classmethod
    def get_api_client(cls) -> ApiClient:
        return cls._api_client

    @classmethod
    def get_db_client(cls) -> ApiDatabaseClient:
        return cls._db_client

    @classmethod
    def get_reportes_client(cls) -> ApiReportesClient:
        return cls._reportes_client

    @classmethod
    def get_usuarios_client(cls) -> ApiUsuariosClient:
        return cls._usuarios_client