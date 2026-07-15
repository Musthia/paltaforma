from core.session_manager import SessionManager

# =========================
# UI principal (Qt Designer)
# =========================
from ui.AplicacionPrincipal_ui import Ui_MainWindow

from shiboken6 import isValid

# =========================
# PySide6 - Widgets
# =========================
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QMessageBox,
    QInputDialog,
    QTreeView,
    QTableView,
    QVBoxLayout,
    QMenu,
    QWidgetAction,
    QStyledItemDelegate,
    QStyle,
)

# =========================
# PySide6 - Core
# =========================
from PySide6.QtCore import (
    Qt,
    QRect,
    QPoint,
    Signal,
    QSortFilterProxyModel,
)

# =========================
# PySide6 - Gui
# =========================
from PySide6.QtGui import (
    QIcon,
    QAction,
    QColor,
    QStandardItemModel,
    QStandardItem,
)

# =========================
# Controladores / Proyecto
# =========================
from controller.selector_bases import SelectorBasesDialog
from controller.cargador_plantillas import cargar_plantilla

from ui.styles import (
    style_dialog_dark,
    style_pushbutton_dark,
    style_combobox_dark,
)

#from utils import obtener_ruta_bases
from utils.rutas import (
    obtener_ruta_bases
)

from PySide6.QtWidgets import QMessageBox

# =========================
# Librerías estándar
# =========================
import os
import sys
import json
import sqlite3
import subprocess
import logging
import importlib

from core.access_control import (validar_sesion, validar_nivel)

from ventanas.ventana_usuarios import (
    VentanaUsuarios
)

from core.seguridad import (
    validar_permiso
)

from utils.user_helpers import get_usuario_attr

from ui.tree_loader import TreeLoader
from ui.dynamic_form import DynamicForm
from db.router import DatabaseRouter

from db.service import DatabaseService

from db.registry import db_registry
from sqlalchemy import create_engine
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAUNCHER_DATA = os.path.join(BASE_DIR, "launcher_data.json")

#DEBUG = True  # <- Poner False cuando ya esté todo ok
EXTENSIONES_SQLITE = (".db", ".sqlite", ".sqlite3")

def asegurar_carpeta_bases():
    ruta = obtener_ruta_bases()
    if not os.path.exists(ruta):
        os.makedirs(ruta)
    return ruta

def listar_bases_sin_extension():
    """
    Devuelve una lista con los nombres de bases sin extensión.
    """
    ruta = asegurar_carpeta_bases()
    bases = []
    for archivo in os.listdir(ruta):
        nombre, ext = os.path.splitext(archivo)
        if ext.lower() in EXTENSIONES_SQLITE:
            bases.append(nombre)
    return bases

# ----------------------------
# Ventana Principal
# ----------------------------
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        logging.debug("Inicializando ventana principal...")

        # -----------------------------------
        # VALIDAR SESIÓN
        # -----------------------------------

        if not validar_sesion():

            logging.warning("Intento acceso sin sesión.")

            QMessageBox.critical(
                self,
                "Sesión inválida",
                "Debe iniciar sesión para acceder al sistema."
            )

            self.close()
            return

        # -----------------------------------
        # VALIDAR NIVEL MÍNIMO
        # -----------------------------------

        if not validar_nivel(1):

            logging.warning("Nivel insuficiente para ingresar.")

            QMessageBox.critical(
                self,
                "Acceso denegado",
                "No posee permisos para ingresar al sistema."
            )

            SessionManager.logout()
            self.close()
            return

        logging.debug("Acceso autorizado a ventana principal.")

        # -----------------------------------
        # USUARIO ACTUAL
        # -----------------------------------

        self.usuario_actual = SessionManager.obtener_usuario()

        # -----------------------------------
        # DATOS USUARIO (SAFE HYBRID)
        # -----------------------------------

        nombre = get_usuario_attr(self.usuario_actual, "nombre", "")
        apellido = get_usuario_attr(self.usuario_actual, "apellido", "")
        rol = get_usuario_attr(self.usuario_actual, "rol", "")
        nivel_seguridad = get_usuario_attr(self.usuario_actual, "nivel_seguridad", 0)

        # -----------------------------------
        # UI
        # -----------------------------------

        if hasattr(self, "label_usuario"):
            self.label_usuario.setText(
                f"{nombre} {apellido} - {rol}"
            )

        self.nombre_usuario = nombre
        self.rol = rol
        self.nivel_seguridad = nivel_seguridad
        
        self.router = DatabaseRouter()
        self.loader = TreeLoader(self.router)
        
        self.db_service = DatabaseService()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.base_actual = None  # 👈 CLAVE

        self.ui.entry_consultar.textChanged.connect(self.actualizar_resaltado)
        
        self.ui.combo_bases.activated.connect(self.on_base_changed)

        self.ui.combo_bases.activated.connect(lambda: self.ui.entry_consultar.setFocus())

        
        self.ui.combo_bases.activated.connect( lambda: self.ui.entry_consultar.setFocus() ) 
        self.ui.combo_bases.currentIndexChanged.connect( lambda: print("COMBO CAMBIÓ:", self.ui.combo_bases.currentText()) )
        
        self.ui.combo_bases.setCurrentIndex(-1)
        self.ui.combo_bases.setPlaceholderText("Seleccione una opción")

        self.ui.boton_cerrar_sesion.clicked.connect(
            self.cerrar_sesion
        )

        # 🔌 CONEXIÓN DEL BOTÓN
        self.ui.pushButton_carga_datos.clicked.connect(
            self.on_pushButton_carga_datos_clicked
        )

        self.ui.boton_adm_usuar.clicked.connect(
            self.abrir_administracion_usuarios
        )

        self.colores_columnas = {
            "n_lote": QColor(180, 0, 255, 140),
            #"cuit": QColor(255, 200, 200, 140),
            "hh.cc": QColor(200, 25, 200, 140),
            "expediente": QColor(200, 25, 200, 140),
            "documento": QColor(0, 230, 150, 140),
            "denominacion": QColor(0, 20, 255, 140),
        }

        self.pestanas_consulta = {
            "nombre_base": {
                "widget": QWidget,
                "view": QTableView,
                "model": QStandardItemModel
            }
        }
        
        # Ícono de la ventana
        self.setWindowIcon(QIcon("img/datcorr.ico"))

        # Asegurar que exista central widget si el UI no lo define
        if not self.centralWidget():
            widget_central = QWidget()
            self.setCentralWidget(widget_central)

        # Diccionario: base -> (treeview, model, proxy)
        self.pestanas_resultados = {}

        # Conectar búsqueda
        self.ui.entry_consultar.returnPressed.connect(self.buscar_en_base)

        self.ui.pushButton_consulta_bases.clicked.connect(
            self.consultar_base_seleccionada
        )

        self.pestanas_consulta = {}

        # Ruta de base de datos (aún no usada, pero válida)
        self.db_path = "database/User_data.db"

        # cargar bases al iniciar
        self.cargar_bases_en_combo()
        
        self.ruta_aplicaciones = os.path.join(os.getcwd(), "aplicaciones")
        self.launcher_data = self.cargar_launcher_data()

        #self.ui.pushButton_aplicaciones.clicked.connect(
        #    self.mostrar_launcher
        #)

        self.ui.tabwidget_resultados_consulta.setTabsClosable(True)
        self.ui.tabwidget_resultados_consulta.tabCloseRequested.connect(
            self.cerrar_pestana_resultado
        )
        
    def inicializar_engine_base(self, base=None):

        if base is None:
            base = self.base_actual

        if not base:
            logging.error("No hay base seleccionada")
            return

        postgres_bases = {
            "IPS",
            "PEDIATRICO",
            "IGPJ",
            "IGPJ TXT LISTADO",
            "IGPJ_LISTADO_NUEVO",
            "MATERNIDAD",
            "ESCRIBANIA"
        }

        if base in postgres_bases:

            engine = create_engine(
                f"postgresql+psycopg2://"
                f"{os.getenv('DB_USER')}:"
                f"{os.getenv('DB_PASSWORD')}@"
                f"{os.getenv('DB_HOST')}:"
                f"{os.getenv('DB_PORT')}/"
                f"{os.getenv('DB_NAME')}"
            )

        else:

            ruta = os.path.join(
                self.obtener_ruta_bases(),
                f"{base}.db"
            )

            engine = create_engine(f"sqlite:///{ruta}")

        db_registry.set_engine(engine)

        logging.debug(f"[ENGINE SETEADO] {base}")
        print("[ENGINE OK]", engine)
        
    def on_base_changed(self, index=None):

        base = self.ui.combo_bases.currentText()
        self.base_actual = base

        print("[BASE SELECCIONADA]", base)

        # 🔥 ESTO ES LO QUE TE FALTA
        self.inicializar_engine_base()

        from db.registry import db_registry
        print("[ENGINE DESPUÉS]", db_registry.get_engine())

    def abrir_administracion_usuarios(self):

        # -----------------------------------
        # VALIDAR PERMISO
        # -----------------------------------
    
        if not validar_permiso(
            self,
            "ADMIN_USUARIOS",
            (
                "No posee permisos "
                "para administrar usuarios."
            )
        ):
            return
    
        logging.debug(
            "Abriendo administración usuarios..."
        )
    
        dialogo = VentanaUsuarios(
            parent=self
        )
    
        dialogo.exec()

    def cerrar_sesion(self):

        respuesta = QMessageBox.question(
            self,
            "Cerrar sesión",
            "¿Desea cerrar la sesión actual?"
        )
    
        if respuesta != QMessageBox.Yes:
        
            return
    
        logging.debug(
            "Iniciando cierre de sesión..."
        )
    
        # -----------------------------------
        # FINALIZAR SESIÓN GLOBAL
        # -----------------------------------
    
        SessionManager.logout()
    
        logging.debug(
            "Sesión finalizada correctamente."
        )
    
        # -----------------------------------
        # CERRAR VENTANA PRINCIPAL
        # -----------------------------------
    
        self.close()
    
        # -----------------------------------
        # VOLVER A LOGIN
        # -----------------------------------
    
        from base_datcorr import InicioSesion
    
        self.login = InicioSesion()
    
        self.login.show()
    
        logging.debug(
            "Ventana login restaurada."
        )

    def cerrar_pestana_resultado(self, index):

        widget = self.ui.tabwidget_resultados_consulta.widget(index)

        if widget is None:
            return

        # Eliminar del diccionario
        for base, datos in list(self.pestanas_resultados.items()):
            if datos["contenedor"] == widget:
                del self.pestanas_resultados[base]
                break

        self.ui.tabwidget_resultados_consulta.removeTab(index)

        if widget:
            widget.deleteLater()

    def cargar_launcher_data(self):
        if not os.path.exists(LAUNCHER_DATA):
            return {"favoritos": [], "recientes": []}

        with open(LAUNCHER_DATA, "r", encoding="utf-8") as f:
            return json.load(f)


    def guardar_launcher_data(self):
        with open(LAUNCHER_DATA, "w", encoding="utf-8") as f:
            json.dump(self.launcher_data, f, indent=4)

    def mostrar_launcher(self):
        menu = QMenu(self)

        # Buscador
        buscador = QLineEdit()
        buscador.setPlaceholderText("Buscar aplicación...")
        buscador.setClearButtonEnabled(True)

        buscador_action = QWidgetAction(self)
        buscador_action.setDefaultWidget(buscador)
        menu.addAction(buscador_action)

        menu.addSeparator()

        archivos = [
            f for f in os.listdir(self.ruta_aplicaciones)
            if f.lower().endswith((".lnk", ".exe"))
        ]

        def refrescar_menu(texto=""):
            menu.clear()
            menu.addAction(buscador_action)
            menu.addSeparator()

            texto = texto.lower()

            def agregar_seccion(titulo, lista):
                if not lista:
                    return
                menu.addSection(titulo)
                for ruta in lista:
                    if texto and texto not in os.path.basename(ruta).lower():
                        continue
                    self.crear_accion_app(menu, ruta)

            # Favoritos
            agregar_seccion(
                "⭐ Favoritos",
                self.launcher_data["favoritos"]
            )

            # Recientes
            agregar_seccion(
                "🕘 Recientes",
                self.launcher_data["recientes"]
            )

            # Todas
            todas = [
                os.path.join(self.ruta_aplicaciones, f)
                for f in archivos
                if os.path.join(self.ruta_aplicaciones, f)
                not in self.launcher_data["favoritos"]
            ]

            agregar_seccion("📦 Aplicaciones", todas)

        buscador.textChanged.connect(refrescar_menu)

        refrescar_menu()

        #boton = self.ui.pushButton_aplicaciones
        #pos = boton.mapToGlobal(QPoint(0, boton.height()))
        #menu.exec(pos)

    def crear_accion_app(self, menu, ruta):
        nombre = os.path.splitext(os.path.basename(ruta))[0]
        icono = QIcon(ruta)

        accion = QAction(icono, nombre, self)

        accion.triggered.connect(
            lambda checked=False, r=ruta: self.abrir_app(r)
        )

        # Menú contextual
        submenu = QMenu()

        abrir_admin = QAction("Abrir como administrador", self)
        abrir_admin.triggered.connect(
            lambda checked=False, r=ruta: self.abrir_como_admin(r)
        )

        fav = QAction("⭐ Agregar / Quitar favorito", self)
        fav.triggered.connect(
            lambda checked=False, r=ruta: self.toggle_favorito(r)
        )

        submenu.addAction(abrir_admin)
        submenu.addAction(fav)

        accion.setMenu(submenu)
        menu.addAction(accion)

    def abrir_app(self, ruta):
        subprocess.Popen(ruta, shell=True)

        if ruta in self.launcher_data["recientes"]:
            self.launcher_data["recientes"].remove(ruta)

        self.launcher_data["recientes"].insert(0, ruta)
        self.launcher_data["recientes"] = self.launcher_data["recientes"][:5]

        self.guardar_launcher_data()

    def abrir_como_admin(self, ruta):
        comando = f'Start-Process "{ruta}" -Verb RunAs'
        subprocess.Popen(
            ["powershell", "-Command", comando],
            shell=True
        )

    def toggle_favorito(self, ruta):
        if ruta in self.launcher_data["favoritos"]:
            self.launcher_data["favoritos"].remove(ruta)
        else:
            self.launcher_data["favoritos"].append(ruta)

        self.guardar_launcher_data()

    def _cerrar_pestana_consulta(self, index):
        widget = self.ui.tabwidget_resultados_consulta.widget(index)

        if widget is None:
            return

        base_a_eliminar = None
        for base, info in self.pestanas_consulta.items():
            if info["widget"] is widget:
                base_a_eliminar = base
                break

        if base_a_eliminar:
            info = self.pestanas_consulta[base_a_eliminar]

            # 🧠 Guardar en caché (modelo u otros datos útiles)
            self.cache_pestanas[base_a_eliminar] = {
                "model": info.get("model"),
                # podés agregar más cosas:
                # "filtros": ...
                # "scroll": ...
            }

            # ❌ eliminar de pestañas activas
            del self.pestanas_consulta[base_a_eliminar]

        # ❌ quitar del tab
        self.ui.tabwidget_resultados_consulta.removeTab(index)
        widget.deleteLater()

    def consultar_base_seleccionada(self):
        
        base = self.base_actual
        tabla = "Datcorr_database"

        schema = self.mapear_base_a_schema(base)

        resultados, columnas = self.db_service.consultar(
            schema=schema,
            table=tabla
        )

        self.crear_o_actualizar_pestana(
            base,
            columnas,
            resultados
        )

        if not os.path.exists(ruta_db):
            QMessageBox.warning(
                self,
                "Base no encontrada",
                f"No existe la base:\n{ruta_db}"
            )
            return

        # 🟢 1. SI YA ESTÁ ABIERTA → solo activar
        if base in self.pestanas_consulta:
            info = self.pestanas_consulta[base]
            widget = info["widget"]

            if not isValid(widget):
                # widget muerto → limpiar
                del self.pestanas_consulta[base]
            else:
                index = self.ui.tabwidget_resultados_consulta.indexOf(widget)

                if index != -1:
                    self.ui.tabwidget_resultados_consulta.setCurrentIndex(index)

                    self._cargar_datos_tabla(
                        base,
                        info["model"],
                        ruta_db=ruta_db
                    )
                    return

        # 🟡 2. SI ESTÁ EN CACHÉ (fue cerrada)
        if hasattr(self, "cache_pestanas") and base in self.cache_pestanas:
            cache = self.cache_pestanas[base]

            self._crear_pestana_consulta(
                base,
                ruta_db=ruta_db,
                model=cache.get("model")  # reutiliza modelo
            )

            # ❌ limpiar caché
            del self.cache_pestanas[base]
            return

        # 🔵 3. SI NO EXISTE → crear nueva
        self._crear_pestana_consulta(
            base,
            ruta_db=ruta_db
        )

    def _crear_pestana_consulta(self, base, ruta_db):
        from PySide6.QtWidgets import QMessageBox

        # 🔁 Si la pestaña ya existe → enfocar y refrescar
        if base in self.pestanas_consulta:

            pestaña = self.pestanas_consulta[base]
            self.ui.tabwidget_resultados_consulta.setCurrentWidget(
                pestaña["widget"]
            )
            self._cargar_datos_tabla(
                base,
                pestaña["model"],
                ruta_db
            )
            return

        if not os.path.exists(ruta_db):
            QMessageBox.warning(
                self,
                "ERROR",
                f"No existe la base:\n{ruta_db}"
            )
            return

        # ---------- CONSULTA DB ----------
        try:
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(Datcorr_database)")
            columnas_info = cursor.fetchall()

            columnas = [
                col[1] for col in columnas_info
                if col[1].lower() not in ("id", "id_datcorr_database")
            ]

            cursor.execute(f"""
                SELECT id_datcorr_database, {", ".join(columnas)}
                FROM Datcorr_database
            """)

            resultados = cursor.fetchall()
            conn.close()

        except Exception as e:
            logging.exception(e)
            QMessageBox.critical(
                self,
                "ERROR",
                str(e)
            )
            return

        cantidad = len(resultados)

        # ---------- UI ----------
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)

        view = QTableView()
        view.setAlternatingRowColors(True)
        view.setSortingEnabled(True)
        view.setSelectionBehavior(QTableView.SelectRows)
        view.setEditTriggers(QTableView.NoEditTriggers)

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(columnas)

        view.setModel(model)
        layout.addWidget(view)

        # ---------- CARGA DE DATOS ----------
        for fila in resultados:
            id_registro = fila[0]
            datos = fila[1:]

            items = []
            for valor in datos:
                texto = "" if valor is None else str(valor)
                item = QStandardItem(texto)
                item.setEditable(False)
                item.setData(id_registro, Qt.UserRole)
                items.append(item)

            model.appendRow(items)

        # ---------- TÍTULO ----------
        titulo = f"DATABASE {base} ({cantidad})"
        self.ui.tabwidget_resultados_consulta.addTab(contenedor, titulo)
        self.ui.tabwidget_resultados_consulta.setCurrentWidget(contenedor)

        # ---------- REGISTRO ----------
        self.pestanas_consulta[base] = {
            "widget": contenedor,
            "view": view,
            "model": model,
            "ruta_db": ruta_db   # 👈 clave
        }

    def _cargar_datos_tabla(self, base, model, ruta_db):
        from PySide6.QtWidgets import QMessageBox

        model.clear()

        if not os.path.exists(ruta_db):
            QMessageBox.warning(
                self,
                "ERROR",
                f"No existe la base:\n{ruta_db}"
            )
            return

        try:
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Datcorr_database")
            filas = cursor.fetchall()

            columnas = [desc[0] for desc in cursor.description]
            conn.close()

        except Exception as e:
            logging.exception(e)
            QMessageBox.critical(
                self,
                "ERROR",
                str(e)
            )
            return

        model.setColumnCount(len(columnas))
        model.setHorizontalHeaderLabels(columnas)

        for fila in filas:
            items = []
            for valor in fila:
                texto = "" if valor is None else str(valor)
                item = QStandardItem(texto)
                item.setEditable(False)

                if texto.isdigit():
                    item.setData(int(texto), Qt.UserRole)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setData(texto.lower(), Qt.UserRole)

                items.append(item)

            model.appendRow(items)


    def on_pushButton_carga_datos_clicked(self):
        from PySide6.QtWidgets import QMessageBox

        self.dialogo_bases = SelectorBasesDialog(self)

        self.dialogo_bases.btn_aceptar.clicked.connect(
            self._procesar_base_seleccionada
        )

        self.dialogo_bases.show()   # ❗ NO exec()

    def _procesar_base_seleccionada(self):
        from PySide6.QtWidgets import QMessageBox

        base = self.dialogo_bases.base_seleccionada()

        if not base:
            QMessageBox.warning(
                self,
                "DEBUG",
                "No se seleccionó ninguna base"
            )
            return

        cargar_plantilla(
            nombre_base=base,
            tabwidget=self.ui.tabwidget_resultados_consulta,
            parent=self
        )

        self.dialogo_bases.close()

    def enfocar_entry_busqueda(self):
        if self.ui.combo_bases.currentText():
            self.ui.entry_consultar.setFocus()

    def cargar_bases_en_combo(self):
        from PySide6.QtWidgets import QMessageBox
        #from utils import obtener_ruta_bases
        from utils.rutas import (
            obtener_ruta_bases
        )

        self.ui.combo_bases.blockSignals(True)
        self.ui.combo_bases.clear()
        self.ui.combo_bases.setStyleSheet(style_combobox_dark())

        # DEBUG: ruta real de bases
        ruta_bases = obtener_ruta_bases()

        if not os.path.exists(ruta_bases):
            QMessageBox.warning(
                self,
                "ERROR",
                f"No existe la carpeta bases_g:\n{ruta_bases}"
            )
            self.ui.combo_bases.blockSignals(False)
            return

        # Listar bases reales
        bases = [
            os.path.splitext(f)[0]
            for f in os.listdir(ruta_bases)
            if f.lower().endswith(".db")
        ]

        for base in bases:
            self.ui.combo_bases.addItem(base)

        self.ui.combo_bases.blockSignals(False)

        # 👉 Seleccionar la primera base si existe
        if bases:
            self.ui.combo_bases.setCurrentIndex(-1)
            self.ui.combo_bases.setPlaceholderText("Seleccione una opción")
            self.ui.combo_bases.setFocus()

    def buscar_en_base(self):

        # -----------------------------------
        # VALIDAR ACCESO
        # -----------------------------------

        logging.debug(
            "Validando acceso a búsqueda..."
        )

        if not validar_nivel(1):
        
            logging.warning(
                "Acceso denegado "
                "a búsqueda."
            )

            QMessageBox.warning(
                self,
                "Acceso denegado",
                (
                    "No posee permisos "
                    "para realizar búsquedas."
                )
            )

            return

        logging.debug(
            "Acceso autorizado "
            "a búsqueda."
        )


        criterio = self.ui.entry_consultar.text().strip()
        base = self.ui.combo_bases.currentText().strip()

        logging.debug(f"[BUSCAR] criterio='{criterio}' base='{base}'")

        if not criterio or not base:
            logging.debug("[BUSCAR] criterio o base vacíos")
            return

        self.base_actual = base  # 👈 GARANTIZA estado consistente

        ruta_db = os.path.join(obtener_ruta_bases(), f"{base}.db")
        logging.debug(f"[BUSCAR] ruta_db={ruta_db}")

        if not os.path.exists(ruta_db):
            logging.error(f"[BUSCAR] NO existe la base: {ruta_db}")
            return  # 👈 solo consola, sin QMessageBox

        try:
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(Datcorr_database)")
            columnas_info = cursor.fetchall()

            columnas = [
                col[1] for col in columnas_info
                if col[1].lower() != "id_datcorr_database"
            ]

            if not columnas:
                logging.warning("[BUSCAR] no se detectaron columnas")
                return

            where = " OR ".join([f"{c} LIKE ?" for c in columnas])
            parametros = [f"%{criterio}%"] * len(columnas)

            query = f"""
                SELECT id_datcorr_database, {", ".join(columnas)}
                FROM Datcorr_database
                WHERE {where}
            """

            cursor.execute(query, parametros)
            resultados = cursor.fetchall()
            conn.close()

            logging.debug(f"[BUSCAR] filas encontradas={len(resultados)}")

            if not resultados:
                QMessageBox.information(
                    self,
                    "Sin resultados",
                    f"No se encontraron coincidencias en la base '{base}'."
                )
                return
                logging.info("[BUSCAR] sin resultados")
                return

            self.crear_o_actualizar_pestana(
                base=base,
                columnas=columnas,
                resultados=resultados
            )

        except Exception:
            logging.exception("[BUSCAR] Error inesperado")


        except Exception as e:
            logging.exception("[BUSCAR] Error inesperado")
            QMessageBox.critical(self, "Error", str(e))

    def crear_o_actualizar_pestana(self, base, columnas, resultados):

        if base in self.pestanas_resultados:

            datos_tab = self.pestanas_resultados[base]
            contenedor = datos_tab["contenedor"]
            tree = datos_tab["tree"]
            model = datos_tab["model"]
            delegate = datos_tab["delegate"]

            model.clear()

            cantidad = len(resultados)
            titulo = f"RESULTADO {base} ({cantidad})"

            index_tab = self.ui.tabwidget_resultados_consulta.indexOf(contenedor)
            if index_tab != -1:
                self.ui.tabwidget_resultados_consulta.setTabText(index_tab, titulo)

            delegate.set_criterio(self.ui.entry_consultar.text())

        else:

            contenedor = QWidget()
            layout = QVBoxLayout(contenedor)

            contenedor.setStyleSheet("""
                QWidget {
                    background-color: #80ccff;   /* elegí el color */
                }
            """)

            tree = QTreeView()
            layout.addWidget(tree)

            model = QStandardItemModel()
            proxy = QSortFilterProxyModel()
            proxy.setSourceModel(model)
            proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
            proxy.setFilterKeyColumn(-1)
            proxy.setSortRole(Qt.UserRole)

            tree.setModel(proxy)

            delegate = ResaltadoCoincidenciaDelegate(
                self.ui.entry_consultar.text(),
                self.colores_columnas,
                tree
            )
            tree.setItemDelegate(delegate)

            tree.setAlternatingRowColors(True)
            tree.setSortingEnabled(True)
            tree.setEditTriggers(QTreeView.NoEditTriggers)

            header = tree.header()
            header.setSectionsClickable(True)
            header.setSortIndicatorShown(True)

            tree.setStyleSheet("""
            QHeaderView::section {
                background-color: #cfcfcf;
                color: #000020;
                padding: 4px;
                border: 1px solid #d7d7d7;
                font-weight: bold;
            }
            QHeaderView::section:hover {
                background-color: #debef1;
            }

            QHeaderView::section:checked {
                background-color: #aedfff;
            }
            """)            
            
            #tree.doubleClicked.connect(self.on_row_double_click)
            tree.doubleClicked.connect(
                lambda index, b=base: self.editar_fila(index, b)
            )            

            cantidad = len(resultados)
            titulo = f"RESULTADO {base} ({cantidad})"

            self.ui.tabwidget_resultados_consulta.addTab(contenedor, titulo)

            self.pestanas_resultados[base] = {
                "contenedor": contenedor,
                "tree": tree,
                "model": model,
                "proxy": proxy,
                "delegate": delegate
            }

        # -----------------------------------------
        # CONFIGURAR HEADERS (SIEMPRE)
        # -----------------------------------------

        model.setColumnCount(len(columnas))
        model.setHorizontalHeaderLabels(columnas)

        # -----------------------------------------
        # CARGAR DATOS (SIEMPRE)
        # -----------------------------------------

        for fila in resultados:

            id_registro = fila[0]
            datos = fila[1:]

            items = []

            for valor in datos:
                texto = "" if valor is None else str(valor)
                item = QStandardItem(texto)
                item.setEditable(False)

                if texto.isdigit():
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    item.setData(int(texto), Qt.UserRole)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    item.setData(texto.lower(), Qt.UserRole)

                items.append(item)

            if items:
                items[0].setData(id_registro, Qt.UserRole)

            model.appendRow(items)

        tree.resizeColumnToContents(0)
        # Ocultar columna ID
        #tree.setColumnHidden(0, True)
        
    """ def on_row_double_click(self, index):

        # -----------------------------------
        # 1. OBTENER FILA SELECCIONADA
        # -----------------------------------
        row = index.row()

        # -----------------------------------
        # 2. EXTRAER DATOS DEL TREEVIEW
        # -----------------------------------
        data = {}

        for col in range(tree.columnCount()):

            header = tree.horizontalHeaderItem(col).text()

            value = tree.item(row, col).text()

            data[header] = value

        # -----------------------------------
        # 3. ABRIR FORMULARIO DINÁMICO
        # -----------------------------------
        self.ui.open_dynamic_form(data) """

    def editar_fila(self, index, base):

        # -----------------------------------
        # VALIDAR ACCESO EDICIÓN
        # -----------------------------------
        
        logging.debug(
            "Validando acceso a edición..."
        )

        # -----------------------------------
        # VALIDAR SESIÓN
        # -----------------------------------

        usuario = SessionManager.obtener_usuario()

        if not usuario:

            logging.warning(
                "Edición denegada: sin sesión."
            )

            QMessageBox.critical(
                self,
                "Sesión inválida",
                "Debe iniciar sesión."
            )

            return

        logging.debug(
            f"USUARIO ACTUAL = {usuario}"
        )

        logging.debug(
            f"ES SUPERUSUARIO = "
            f"{get_usuario_attr(usuario, 'es_superusuario')}"
        )

        # -----------------------------------
        # VALIDAR PERMISO EDITAR
        # -----------------------------------

        if not SessionManager.tiene_permiso(
            "EDITAR"
        ):

            logging.warning(
                f"Usuario '{get_usuario_attr(usuario, 'usuario')}'"
                f"sin permiso EDITAR."
            )

            QMessageBox.warning(
                self,
                "Permiso denegado",
                (
                    "No posee permisos "
                    "para editar registros."
                )
            )

            return

        logging.debug(
            "Acceso autorizado a edición."
        )

        if base not in self.pestanas_resultados:
            return

        datos_tab = self.pestanas_resultados[base]

        tree = datos_tab["tree"]
        model = datos_tab["model"]
        proxy = datos_tab["proxy"]

        index_source = proxy.mapToSource(index)
        fila = index_source.row()

        if fila < 0:
            return

        # ID real del registro
        item_id = model.item(fila, 0)
        if item_id is None:
            return

        id_registro = item_id.data(Qt.UserRole)

        columnas = [
            model.headerData(i, Qt.Horizontal)
            for i in range(model.columnCount())
        ]

        valores = [
            model.item(fila, i).text()
            for i in range(model.columnCount())
        ]

        # ---------- RUTA DB ----------
        if base not in self.pestanas_resultados:
            return

        if db_registry.get_engine() is None:
            QMessageBox.warning(
                self,
                "Sistema no inicializado",
                "Seleccione una base antes de editar."
            )
            return

        # ---------- CREAR DIÁLOGO ----------
        self.ventana_edicion = VentanaEdicionRegistro(
            base=base,
            id_registro=id_registro,
            columnas=columnas,
            valores=valores,
            schema=self.mapear_base_a_schema(base),
            table="Datcorr_database",
            db_service=self.db_service,
            parent=self
        )

        self.ventana_edicion.datos_actualizados.connect(
            self.actualizar_fila_treeview
        )

        self.ventana_edicion.exec()
        
    def mapear_base_a_schema(self, base):

        mapa = {
            "IPS": "ips",
            "PEDIATRICO": "pediatrico",
            "IGPJ_LISTADO_NUEVO": "igpj_listado_nuevo",
            "IGPJ TXT LISTADO": "igpj_txt_listado",
            "IGPJ": "igpj",
            "MATERNIDAD": "maternidad",
            "ESCRIBANIA": "escribania"
        }

        return mapa.get(base)

    def closeEvent(self, event):

        logging.debug(
            "Cierre aplicación detectado."
        )

        SessionManager.logout()

        logging.debug(
            "Sesión invalidada "
            "por cierre aplicación."
        )

        event.accept()

    def actualizar_fila_treeview(self, base, id_registro, datos_actualizados):
        
        print("ACTUALIZAR TREEVIEW")
        print("BASE:", base)
        print("ID:", id_registro)
        print("DATOS:", datos_actualizados)

        datos = self.pestanas_resultados.get(base)
        if not datos:
            return

        model = datos["model"]
        
        print("HEADERS DEL MODEL:")

        for i in range(model.columnCount()):
            print(
                i,
                model.headerData(i, Qt.Horizontal)
            )

        for fila in range(model.rowCount()):
            item_id = model.item(fila, 0).data(Qt.UserRole)

            if item_id == id_registro:
                
                print(
                    "TREE ID:",
                    item_id,
                    "BUSCANDO:",
                    id_registro
                )

                for col_index in range(model.columnCount()):

                    nombre_col = model.headerData(
                        col_index,
                        Qt.Horizontal
                    )

                    print(
                        "HEADER:",
                        nombre_col,
                        "EXISTE:",
                        nombre_col in datos_actualizados
                    )

                    if nombre_col in datos_actualizados:
                    
                        print(
                            "ACTUALIZANDO:",
                            nombre_col,
                            "->",
                            datos_actualizados[nombre_col]
                        )

                        model.item(
                            fila,
                            col_index
                        ).setText(
                            datos_actualizados[nombre_col]
                        )
                break

    def actualizar_resaltado(self, texto):

        index = self.ui.tabwidget_resultados_consulta.currentIndex()
        if index == -2:
            return

        widget_actual = self.ui.tabwidget_resultados_consulta.widget(index)

        for base, datos in self.pestanas_resultados.items():

            tree = datos["tree"]
            delegate = datos["delegate"]
            contenedor = datos["contenedor"]

            if contenedor == widget_actual:
                delegate.set_criterio(texto)
                tree.viewport().update()
                break

class VentanaEdicionRegistro(QDialog):

    datos_actualizados = Signal(str, int, dict)

    def __init__(self, 
                 base, 
                 id_registro, 
                 columnas, 
                 valores, 
                 schema, table, 
                 db_service, 
                 parent=None):
        
        super().__init__(parent)

        # Ícono de la ventana
        self.setWindowIcon(QIcon("img/datcorr.ico"))

        # Tamaño fijo exacto
        self.resize(550, 500)

        from PySide6.QtWidgets import QMessageBox
        import os
        import logging

        # ---------- ASIGNACIONES PRIMERO ----------
        self.base = base
        self.id_registro = id_registro

        # NUEVO SISTEMA HÍBRIDO
        self.schema = schema
        self.table = table
        self.db_service = db_service
        
        # Determina si estamos usando PostgreSQL
        self.usar_postgres = (
            self.schema is not None
            and self.table is not None
            and self.db_service is not None
        )

        self.campos = {}

        # ---------- VALIDACIÓN ----------
        if self.usar_postgres:

            logging.debug(
                f"[EDICION] PostgreSQL "
                f"{self.schema}.{self.table}"
            )

        else:
        
            if (
                not isinstance(self.ruta_db, str)
                or not os.path.exists(self.ruta_db)
            ):

                logging.error(
                    f"[EDICION] ruta_db inválida: "
                    f"{self.ruta_db}"
                )

                QMessageBox.critical(
                    self,
                    "ERROR DE CONFIGURACIÓN",
                    "Ruta de base inválida"
                )

                self.reject()
                return
        logging.debug(f"[EDICION] Usando DB: {self.schema if self.usar_postgres else self.ruta_db}")

        # ---------- UI ----------
        self.setStyleSheet(style_dialog_dark())
        self.setWindowTitle(f"Editar registro - {base}")

        layout = QFormLayout(self)

        for col, val in zip(columnas, valores):
            if col.lower() in ("id", "id_datcorr_database"):
                continue

            label = QLabel(col)
            entry = QLineEdit("" if val is None else str(val))

            # SOLO LECTURA
            if col.lower() == "registro":
                entry.setReadOnly(True)
                entry.setStyleSheet("""
                    QLineEdit {
                        background-color: #2e2e2e;
                        color: #9e9e9e;
                    }
                """)

            layout.addRow(label, entry)
            self.campos[col] = entry
            
            print("ENGINE:", db_registry.get_engine())

        btn_guardar = QPushButton("Guardar cambios")
        btn_guardar.setStyleSheet(style_pushbutton_dark())
        btn_guardar.clicked.connect(self.guardar_cambios)
        btn_guardar.setAutoDefault(False)

        layout.addRow(btn_guardar) 

    def guardar_cambios(self):

        columnas = list(self.campos.keys())
        valores = [self.campos[c].text() for c in columnas]

        datos_actualizados = dict(zip(columnas, valores))

        # -----------------------------
        # POSTGRESQL (HÍBRIDO NUEVO)
        # -----------------------------
        if self.usar_postgres:

            try:

                self.db_service.actualizar(
                    schema=self.schema,
                    table=self.table,
                    id_field="id_Datcorr_database",
                    id_value=self.id_registro,
                    data=datos_actualizados
                )

                self.datos_actualizados.emit(
                    self.base,
                    self.id_registro,
                    datos_actualizados
                )

                self.accept()

            except Exception as e:

                logging.exception(e)

                QMessageBox.critical(
                    self,
                    "ERROR",
                    str(e)
                )

            return

        # -----------------------------
        # SQLITE LEGACY (NO TOCAR)
        # -----------------------------
        try:

            import sqlite3

            set_clause = ", ".join([f"{c}=?" for c in columnas])

            query = f"""
                UPDATE Datcorr_database
                SET {set_clause}
                WHERE id_datcorr_database = ?
            """

            conn = sqlite3.connect(self.ruta_db)
            cursor = conn.cursor()

            cursor.execute(query, valores + [self.id_registro])
            conn.commit()
            conn.close()

            self.datos_actualizados.emit(
                self.base,
                self.id_registro,
                datos_actualizados
            )

            self.accept()

        except Exception as e:

            logging.exception(e)

            QMessageBox.critical(
                self,
                "ERROR",
                str(e)
            )
        
            return

class ResaltadoCoincidenciaDelegate(QStyledItemDelegate):
    def __init__(self, criterio="", colores_por_columna=None, parent=None):
        super().__init__(parent)
        self.criterio = criterio.lower()
        self.colores = colores_por_columna or {}

    def set_criterio(self, texto):
        self.criterio = texto.lower()

    def paint(self, painter, option, index):
        painter.save()
        try:
            texto = index.data()
            if texto is None:
                return

            texto_str = str(texto)
            texto_lower = texto_str.lower()

            # 🔹 nombre REAL de la columna
            nombre_col = index.model().headerData(
                index.column(), Qt.Horizontal
            )

            # 🔹 color según nombre
            color_resaltado = self.colores.get(
                nombre_col,
                QColor(255, 230, 150, 140)  # color por defecto
            )

            # Fondo normal / selección
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
                painter.setPen(option.palette.highlightedText().color())
            else:
                painter.fillRect(option.rect, option.palette.base())
                painter.setPen(option.palette.text().color())

            # Texto
            painter.drawText(
                option.rect.adjusted(4, 0, -4, 0),
                Qt.AlignVCenter | Qt.AlignLeft,
                texto_str
            )

            # Resaltado parcial
            if self.criterio:
                inicio = texto_lower.find(self.criterio)
                if inicio != -1:
                    fm = option.fontMetrics
                    x = option.rect.x() + 4 + fm.horizontalAdvance(texto_str[:inicio])
                    ancho = fm.horizontalAdvance(
                        texto_str[inicio:inicio + len(self.criterio)]
                    )

                    painter.fillRect(
                        QRect(
                            x,
                            option.rect.y() + 2,
                            ancho,
                            option.rect.height() - 4
                        ),
                        color_resaltado
                    )
        finally:
            painter.restore()

# ----------------------------
# Inicio de la aplicación
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())