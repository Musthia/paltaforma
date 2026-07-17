import logging

from PySide6.QtWidgets import (
    QDialog,
    QMessageBox
)

from PySide6.QtCore import (
    QStringListModel
)

from ui.permisos_usuario_ui import (
    Ui_EditarUsuario
)

from core.session_manager import SessionManager

from utils.user_helpers import get_usuario_attr

class VentanaPermisosUsuario(QDialog):

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

        logging.debug(
            f"Cargando permisos usuario: "
            f"{get_usuario_attr(usuario,'usuario')}"
        )             

        # -----------------------------------
        # MODELOS
        # -----------------------------------

        self.model_disponibles = (
            QStringListModel()
        )

        self.model_asignados = (
            QStringListModel()
        )

        self.ui.listView_permisos_disponibles.setModel(
            self.model_disponibles
        )

        self.ui.listView_permisos_asignados.setModel(
            self.model_asignados
        )

        # -----------------------------------
        # CARGAR DATOS
        # -----------------------------------

        self.cargar_permisos()  

        self.ui.pushButton_asignar.clicked.connect(
            self.asignar_permiso
        )

        self.ui.pushButton_quitar.clicked.connect(
            self.quitar_permiso
        )

        self.ui.pushButton_guardar.clicked.connect(
            self.guardar_cambios
        )
        self.ui.pushButton_guardar_2.clicked.connect(
            self.guardar_cambios
        )        

    def guardar_cambios(self):

        logging.debug(
            "Guardando cambios permisos usuario..."
        )

        self.accept()

    def asignar_permiso(self):

        index = (
            self.ui
            .listView_permisos_disponibles
            .currentIndex()
        )

        if not index.isValid():

            QMessageBox.warning(
                self,
                "Permisos",
                "Seleccione un permiso."
            )

            return

        permiso = index.data()

        logging.debug(
            f"Asignando permiso: "
            f"{permiso}"
        )

        client = SessionManager.get_usuarios_client()
        resultado = client.asignar_permiso(
            get_usuario_attr(self.usuario, "id"),
            permiso
        )

        if resultado["success"]:

            QMessageBox.information(
                self,
                "Permisos",
                resultado["mensaje"]
            )

            self.cargar_permisos()

        else:

            QMessageBox.warning(
                self,
                "Permisos",
                resultado["mensaje"]
            )

    def quitar_permiso(self):

        index = (
            self.ui
            .listView_permisos_asignados
            .currentIndex()
        )

        if not index.isValid():

            QMessageBox.warning(
                self,
                "Permisos",
                "Seleccione un permiso."
            )

            return

        permiso = index.data()

        logging.debug(
            f"Quitando permiso: "
            f"{permiso}"
        )

        client = SessionManager.get_usuarios_client()
        resultado = client.quitar_permiso(
            get_usuario_attr(self.usuario, "id"),
            permiso
        )

        if resultado["success"]:

            QMessageBox.information(
                self,
                "Permisos",
                resultado["mensaje"]
            )

            self.cargar_permisos()

        else:

            QMessageBox.warning(
                self,
                "Permisos",
                resultado["mensaje"]
            )

    # -----------------------------------
    # CARGAR PERMISOS
    # -----------------------------------

    def cargar_permisos(self):

        logging.debug(
            f"Cargando permisos usuario: "
            f"{get_usuario_attr(self.usuario,'usuario')}"
        )

        client = SessionManager.get_usuarios_client()

        resultado_sistema = client.listar_permisos()
        if isinstance(resultado_sistema, list):
            permisos_sistema = resultado_sistema
        else:
            permisos_sistema = resultado_sistema.get(
                "permisos", []
            )

        resultado_usuario = client.listar_permisos_usuario(
            get_usuario_attr(self.usuario, "id")
        )
        if isinstance(resultado_usuario, list):
            permisos_usuario = resultado_usuario
        else:
            permisos_usuario = resultado_usuario.get(
                "permisos", []
            )

        codigos_usuario = [
            p.get("code", "") if isinstance(p, dict) else p
            for p in permisos_usuario
        ]

        permisos_asignados = []

        permisos_disponibles = []

        for permiso in permisos_sistema:

            codigo = permiso.get("code", "") if isinstance(permiso, dict) else permiso

            if codigo in codigos_usuario:

                permisos_asignados.append(codigo)

            else:

                permisos_disponibles.append(codigo)

        self.model_disponibles = (
            QStringListModel()
        )

        self.model_disponibles.setStringList(
            permisos_disponibles
        )

        self.ui.listView_permisos_disponibles.setModel(
            self.model_disponibles
        )

        self.model_asignados = (
            QStringListModel()
        )

        self.model_asignados.setStringList(
            permisos_asignados
        )

        self.ui.listView_permisos_asignados.setModel(
            self.model_asignados
        )

        logging.debug(
            f"Disponibles: "
            f"{len(permisos_disponibles)} | "
            f"Asignados: "
            f"{len(permisos_asignados)}"
        )