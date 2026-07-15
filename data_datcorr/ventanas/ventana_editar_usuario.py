import logging

from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
    QLineEdit
)

from ui.editar_usuario_ui import (
    Ui_EditarUsuario
)

from PySide6.QtCore import Signal

from core.session_manager import SessionManager

from config.app_config import (
    MODO_DESARROLLO
)

from utils.user_helpers import get_usuario_attr

class VentanaEditarUsuario(QDialog):

    usuario_actualizado = Signal()
    
    def __init__(
        self,
        usuario,
        parent=None
    ):

        super().__init__(parent)

        self.ui = Ui_EditarUsuario()

        self.ui.setupUi(self)

        # -----------------------------------
        # USUARIO
        # -----------------------------------

        self.usuario = usuario

        # -----------------------------------
        # CONFIGURAR UI
        # -----------------------------------

        self.configurar_ui()

        # -----------------------------------
        # CARGAR DATOS
        # -----------------------------------

        self.cargar_datos_usuario()        

        # -----------------------------------
        # CONEXIONES
        # -----------------------------------

        self.ui.pushButton_cancelar.clicked.connect(
            self.reject
        )

        self.ui.pushButton_guardar.clicked.connect(
            self.guardar_usuario
        )

        self.ui.pushButton_reset_pass.clicked.connect(
            self.reset_password
        )

    def reset_password(self):

        nueva_password = "Temp1234"

        client = SessionManager.get_usuarios_client()
        resultado = client.actualizar_usuario(
            get_usuario_attr(self.usuario, "id"),
            {"password": nueva_password}
        )

        if resultado["success"]:

            logging.debug(
                f"Password reseteada: "
                f"{get_usuario_attr(self.usuario, 'usuario')}"
            )

            QMessageBox.information(
                self,
                "Reset Password",
                (
                    "Nueva contraseña temporal:\n\n"
                    f"{nueva_password}"
                )
            )

        else:

            QMessageBox.critical(
                self,
                "Error",
                resultado["mensaje"]
            )

    # -----------------------------------
    # CONFIGURAR UI
    # -----------------------------------

    def configurar_ui(self):

        self.ui.lineEdit_password.setEchoMode(
            QLineEdit.Password
        )

        self.ui.comboBox_rol.addItems([
            "Administrador",
            "Supervisor",
            "Operador",
            "Consulta"
        ])

    def guardar_usuario(self):

        # -----------------------------------
        # PROTEGER SUPERUSUARIO
        # -----------------------------------

        if (
            get_usuario_attr(self.usuario, "es_superusuario", False)
            and not MODO_DESARROLLO
        ):
            QMessageBox.warning(
                self,
                "Protegido",
                "No puede modificar un superusuario."
            )
            return

        # -----------------------------------
        # CAPTURAR DATOS
        # -----------------------------------

        nombre = self.ui.lineEdit_nombre.text().strip()
        apellido = self.ui.lineEdit_apellido.text().strip()
        usuario_texto = self.ui.lineEdit_usuario.text().strip()
        email = self.ui.lineEdit_email.text().strip()
        rol = self.ui.comboBox_rol.currentText()
        nivel = self.ui.spinBox_nivel.value()
        activo = self.ui.checkBox_activo.isChecked()
        password = self.ui.lineEdit_password.text().strip() or None

        # -----------------------------------
        # VALIDACIONES
        # -----------------------------------

        if not nombre.strip():

            QMessageBox.warning(
                self,
                "Validación",
                "Ingrese nombre."
            )

            return

        if not usuario_texto.strip():

            QMessageBox.warning(
                self,
                "Validación",
                "Ingrese usuario."
            )

            return

        # -----------------------------------
        # ACTUALIZAR
        # -----------------------------------

        client = SessionManager.get_usuarios_client()
        data = {
            "nombre": nombre,
            "apellido": apellido,
            "usuario": usuario_texto,
            "rol": rol,
            "nivel_seguridad": nivel,
            "activo": activo
        }
        if email:
            data["email"] = email
        if password:
            data["password"] = password

        resultado = client.actualizar_usuario(
            get_usuario_attr(self.usuario, "id"),
            data
        )

        # -----------------------------------
        # RESPUESTA
        # -----------------------------------

        if resultado["success"]:

            logging.debug(
                f"Usuario actualizado: "
                f"{usuario_texto}"
            )

            QMessageBox.information(
                self,
                "Usuario",
                resultado["mensaje"]
            )

            self.usuario_actualizado.emit()

            self.accept()

        else:

            QMessageBox.critical(
                self,
                "Error",
                resultado["mensaje"]
            )

    # -----------------------------------
    # CARGAR DATOS
    # -----------------------------------

    def cargar_datos_usuario(self):

        logging.debug(
            f"Cargando usuario edición: "
            f"{get_usuario_attr(self.usuario,'usuario')}"
        )

        u = self.usuario

        self.ui.lineEdit_nombre.setText(get_usuario_attr(u, "nombre", ""))
        self.ui.lineEdit_apellido.setText(get_usuario_attr(u, "apellido", ""))
        self.ui.lineEdit_usuario.setText(get_usuario_attr(u, "usuario", ""))
        self.ui.lineEdit_email.setText(get_usuario_attr(u, "email", ""))
        self.ui.comboBox_rol.setCurrentText(get_usuario_attr(u, "rol", ""))
        self.ui.spinBox_nivel.setValue(get_usuario_attr(u, "nivel_seguridad", 0))
        self.ui.checkBox_activo.setChecked(get_usuario_attr(u, "activo", True))
        self.ui.lineEdit_password.clear()
