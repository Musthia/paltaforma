from PySide6.QtWidgets import QMainWindow, QMessageBox, QApplication, QInputDialog, QLineEdit
from PySide6.QtGui import QIcon
import sys
import logging
from dotenv import load_dotenv
load_dotenv()

from services.permisos_service import (
    obtener_descripcion_nivel
)

from ui.inicio_sesion_ui import Ui_MainWindow
from ventana_principal import VentanaPrincipal

from core.session_manager import SessionManager
from core.api_client import ApiClient

# from db.registry import initialize_postgres


# -----------------------------------
# LOGGING
# -----------------------------------

def configurar_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


configurar_logging()


def iniciar_aplicacion_principal():
    ventana = VentanaPrincipal()
    ventana.show()
    return ventana


# ===================================
# LOGIN WINDOW
# ===================================

class InicioSesion(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ventana_principal = None

        # 🔵 API CLIENTE GLOBAL
        self.api = ApiClient("http://127.0.0.1:8000")

        self.setWindowIcon(QIcon("img/Datcorr.ico"))

        self.ui.boton_iniciar_sesion.clicked.connect(
            self.validar_login
        )
        self.ui.boton_recuperar_contrasena.clicked.connect(
            self.recuperar_contrasena
        )

    # ===================================
    # LOGIN
    # ===================================

    def validar_login(self):

        self.ui.entry_usuario.setFocus()
    
        usuario_input = self.ui.entry_usuario.text().strip()
        password_input = self.ui.entry_contrasena.text()
    
        # -----------------------------------
        # LOGIN VIA API
        # -----------------------------------
    
        resultado = self.api.post("/auth/login", {
            "username": usuario_input,
            "password": password_input
        })
    
        # -----------------------------------
        # VALIDACIÓN ERROR
        # -----------------------------------
    
        if not resultado or not resultado.get("success"):
        
            mensaje = resultado.get("mensaje", "Error de conexión")
    
            QMessageBox.critical(
                self,
                "Error Login",
                mensaje
            )
            return
    
        # -----------------------------------
        # USUARIO API (SIEMPRE DICT)
        # -----------------------------------

        usuario_api = resultado.get("user", {})

        # -----------------------------------
        # GUARDAR SESIÓN
        # -----------------------------------

        SessionManager.login({
            "id": usuario_api.get("id"),
            "usuario": usuario_api.get("username"),
            "nombre": usuario_api.get("full_name", ""),
            "apellido": "",
            "rol": usuario_api.get("role"),
            "nivel_seguridad": usuario_api.get("nivel_seguridad"),
            "es_superusuario": usuario_api.get("is_superuser", False)
        })
    
        # -----------------------------------
        # TOKENS
        # -----------------------------------

        self.api.set_tokens(
            resultado.get("access_token"),
            resultado.get("refresh_token")
        )

        # -----------------------------------
        # API CLIENT EN SESSION MANAGER
        # -----------------------------------

        SessionManager.set_api_client(self.api)

        # -----------------------------------
        # SYNC /auth/me (permisos actualizados)
        # -----------------------------------

        SessionManager.sync_from_api()

        # -----------------------------------
        # UI INFO
        # -----------------------------------
    
        nombre_usuario = usuario_api.get("full_name", usuario_api.get("nombre", ""))
        rol = usuario_api.get("role", "")
        nivel = usuario_api.get("nivel_seguridad", 0)
    
        descripcion_nivel = obtener_descripcion_nivel(nivel)
    
        #QMessageBox.information(
        #    self,
        #    "Inicio de Sesión",
        #    f"Bienvenido {nombre_usuario}\n\nRol: {rol}\nNivel: {descripcion_nivel}"
        #)
    
        # -----------------------------------
        # ABRIR SISTEMA
        # -----------------------------------
        
        # initialize_postgres()   # Engine global desactivado — todo vía API

        if rol == "consulta":
            import webbrowser
            from urllib.parse import urlencode
            token = resultado.get("access_token", "")
            refresh = resultado.get("refresh_token", "")
            params = {"token": token}
            if refresh:
                params["refresh_token"] = refresh
            webbrowser.open("http://localhost:8000/simco/?" + urlencode(params))
            QMessageBox.information(self, "Acceso",
                "Tu rol solo tiene acceso a SIMCO.\nSe abrirá en el navegador.")
            return

        self.hide()
        self.ventana_principal = iniciar_aplicacion_principal()

    # ===================================
    # RECUPERAR CONTRASEÑA
    # ===================================

    def recuperar_contrasena(self):

        email, ok = QInputDialog.getText(
            self,
            "Recuperar Contraseña",
            "Ingrese su correo electrónico:",
            QLineEdit.EchoMode.Normal
        )

        if not ok or not email:
            return

        resultado = self.api.post("/auth/forgot-password", {
            "email": email.strip()
        })

        if resultado and resultado.get("success"):

            QMessageBox.information(
                self,
                "Recuperar Contraseña",
                "Si el correo está registrado, recibirá "
                "un enlace para restablecer su contraseña."
            )

        else:

            mensaje = resultado.get(
                "mensaje",
                "Error al enviar solicitud"
            )

            QMessageBox.critical(
                self,
                "Error",
                mensaje
            )


# ===================================
# MAIN
# ===================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = InicioSesion()
    ventana.show()
    sys.exit(app.exec())