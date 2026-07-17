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
    QToolBar,
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



from PySide6.QtWidgets import QMessageBox

# =========================
# Librerías estándar
# =========================
import os
import sys
import json
import subprocess
import logging
import importlib

from ventanas.ventana_usuarios import (
    VentanaUsuarios
)

from core.seguridad import (
    validar_permiso
)

from utils.user_helpers import get_usuario_attr

from ui.dynamic_form import DynamicForm
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAUNCHER_DATA = os.path.join(BASE_DIR, "launcher_data.json")

#DEBUG = True  # <- Poner False cuando ya esté todo ok

# ----------------------------
# Ventana Principal
# ----------------------------
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        # -----------------------------------
        # VALIDAR SESIÓN
        # -----------------------------------

        if not SessionManager.validar_sesion():

            logging.warning("Intento acceso sin sesión.")

            QMessageBox.critical(
                self,
                "Sesión inválida",
                "Debe iniciar sesión para acceder al sistema."
            )

            self.close()
            return

        if SessionManager.obtener_nivel_seguridad() < 1:

            logging.warning("Nivel insuficiente para ingresar.")

            QMessageBox.critical(
                self,
                "Acceso denegado",
                "No posee permisos para ingresar al sistema."
            )

            SessionManager.logout()
            self.close()
            return

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

        self.nombre_usuario = nombre
        self.rol = rol
        self.nivel_seguridad = nivel_seguridad

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

        self._toolbar = QToolBar("Reportes", self)
        self.addToolBar(self._toolbar)
        self._btn_reportes = QAction(QIcon("img/datcorr.ico"), "Reportes", self)
        self._btn_reportes.triggered.connect(self._abrir_reportes)
        self._toolbar.addAction(self._btn_reportes)

        # statusbar con usuario logueado
        self.label_usuario = QLabel(f"  Usuario: {nombre} {apellido}  ({rol})  ")
        self.statusBar().addPermanentWidget(self.label_usuario)
        
    def on_base_changed(self, index=None):

        base = self.ui.combo_bases.currentText()
        self.base_actual = base

        print("[BASE SELECCIONADA]", base)

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

    def _abrir_reportes(self):
        from ui.reportes_viewer import ReportesViewer
        dialogo = ReportesViewer(parent=self)
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

        logging.debug(
            "[CONSULTA] iniciando"
        )

        base = self.base_actual

        if not base:

            QMessageBox.warning(
                self,
                "Sin selección",
                "Seleccione una base."
            )

            return

        tabla = "Datcorr_database"

        try:

            data = SessionManager.get_db_client().consultar_datos(
                base=base, table=tabla, limit=0
            )

            if not data.get("success"):
                raise Exception(data.get("mensaje", "Error al consultar"))
            
            columnas = data.get("columnas", [])
            resultados = data.get("registros", [])
            total = data.get("total", len(resultados))

            # omitir la primera columna (id_Datcorr_database) en la vista
            self.crear_o_actualizar_pestana(
                base=base,
                columnas=columnas[1:],
                resultados=resultados,
                modo="CONSULTA",
                total=total,
            )

            logging.debug(
                f"[CONSULTA OK] "
                f"{base} "
                f"{len(resultados)} registros"
            )

        except Exception as e:

            logging.exception(e)

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    def on_pushButton_carga_datos_clicked(self):
        from PySide6.QtWidgets import QMessageBox

        data = SessionManager.get_db_client().listar_bases()
        if not data.get("success"):
            QMessageBox.critical(self, "Error", data.get("mensaje", "Error al listar bases"))
            return
        bases_disponibles = [b["nombre"] for b in data.get("bases", [])]

        self.dialogo_bases = SelectorBasesDialog(bases_disponibles, self)

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

        self.ui.combo_bases.blockSignals(True)
        self.ui.combo_bases.clear()
        self.ui.combo_bases.setStyleSheet(style_combobox_dark())

        data = SessionManager.get_db_client().listar_bases()
        bases = [b["nombre"] for b in data.get("bases", [])] if data.get("success") else []

        if not bases:
            QMessageBox.warning(
                self,
                "Sin bases",
                "No se encontraron bases de datos en PostgreSQL."
            )
            self.ui.combo_bases.blockSignals(False)
            return

        for base in bases:
            self.ui.combo_bases.addItem(base)

        self.ui.combo_bases.blockSignals(False)

        if bases:
            self.ui.combo_bases.setCurrentIndex(-1)
            self.ui.combo_bases.setPlaceholderText("Seleccione una opción")
            self.ui.combo_bases.setFocus()

    def buscar_en_base(self):

        # -----------------------------------
        # VALIDAR ACCESO
        # -----------------------------------

        if SessionManager.obtener_nivel_seguridad() < 1:

            logging.warning("Acceso denegado a búsqueda.")

            QMessageBox.warning(
                self,
                "Acceso denegado",
                "No posee permisos para realizar búsquedas."
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

        self.base_actual = base

        try:

            data = SessionManager.get_db_client().buscar_datos(
                base=base, q=criterio
            )

            if not data.get("success"):
                raise Exception(data.get("mensaje", "Error al buscar"))

            resultados = data.get("registros", [])
            logging.debug(f"[BUSCAR] filas encontradas={len(resultados)}")

            if not resultados:
                QMessageBox.information(
                    self,
                    "Sin resultados",
                    f"No se encontraron coincidencias en la base '{base}'."
                )
                return

            columnas = data.get("columnas", [])

            self.crear_o_actualizar_pestana(
                base=base,
                columnas=columnas[1:],
                resultados=resultados,
                modo="BUSQUEDA"
            )

        except Exception:
            logging.exception("[BUSCAR] Error inesperado")
            
    def _crear_fila_modelo(self, fila_bd):
        id_registro = fila_bd[0]
        valores = fila_bd[1:]

        items = []

        for valor in valores:
            item = QStandardItem("" if valor is None else str(valor))
            item.setEditable(False)
            items.append(item)

        # ID oculto en todos los items de la fila
        for item in items:
            item.setData(id_registro, Qt.UserRole)

        return items

    def crear_o_actualizar_pestana(
        self,
        base,
        columnas,
        resultados,
        modo="BUSQUEDA",
        total=None,
    ):
    
        clave = f"{base}_{modo}"
    
        datos_tab = self.pestanas_resultados.get(clave)
    
        # -----------------------------------
        # CREAR PESTAÑA SOLO UNA VEZ
        # -----------------------------------
        if not datos_tab:
        
            contenedor = QWidget()
    
            layout = QVBoxLayout(contenedor)
    
            contenedor.setStyleSheet("""
                QWidget {
                    background-color: #80ccff;
                }
            """)
    
            tree = QTreeView()
    
            layout.addWidget(tree)
    
            model = QStandardItemModel()
    
            proxy = QSortFilterProxyModel()
    
            proxy.setSourceModel(model)
    
            proxy.setFilterCaseSensitivity(
                Qt.CaseInsensitive
            )
    
            proxy.setFilterKeyColumn(-1)
    
            proxy.setSortRole(
                Qt.UserRole
            )
    
            tree.setModel(proxy)
    
            tree.setAlternatingRowColors(True)
    
            tree.setSortingEnabled(True)
    
            tree.setEditTriggers(
                QTreeView.NoEditTriggers
            )
    
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
    
            # -----------------------------------
            # DELEGATE (SE CREA UNA SOLA VEZ)
            # -----------------------------------
    
            delegate = ResaltadoCoincidenciaDelegate(
                self.ui.entry_consultar.text(),
                self.colores_columnas,
                tree
            )
    
            tree.setItemDelegate(delegate)
    
            # -----------------------------------
            # EDICIÓN SOLO EN BÚSQUEDA
            # -----------------------------------
    
            if modo == "BUSQUEDA":
            
                tree.doubleClicked.connect(
                    lambda index, k=clave:
                    self.editar_fila(index, k)
                )
    
            self.ui.tabwidget_resultados_consulta.addTab(
                contenedor,
                f"{modo} {base}"
            )
    
            self.pestanas_resultados[clave] = {
            
                "tree": tree,
                "model": model,
                "proxy": proxy,
                "delegate": delegate,
                "contenedor": contenedor,
                "modo": modo,
                "base": base
            }
    
        # -----------------------------------
        # RECUPERAR OBJETOS EXISTENTES
        # -----------------------------------
    
        datos_tab = self.pestanas_resultados[clave]
    
        tree = datos_tab["tree"]
    
        model = datos_tab["model"]
    
        proxy = datos_tab["proxy"]
    
        delegate = datos_tab["delegate"]
    
        contenedor = datos_tab["contenedor"]
    
        # -----------------------------------
        # ACTUALIZAR CRITERIO RESALTADO
        # -----------------------------------
    
        delegate.set_criterio(
            self.ui.entry_consultar.text()
        )
    
        # -----------------------------------
        # LIMPIAR MODELO
        # -----------------------------------
    
        model.clear()
    
        model.setColumnCount(
            len(columnas)
        )
    
        model.setHorizontalHeaderLabels(
            columnas
        )
    
        # -----------------------------------
        # CARGAR FILAS
        # -----------------------------------
    
        for fila in resultados:
        
            model.appendRow(
                self._crear_fila_modelo(fila)
            )
    
        # -----------------------------------
        # ACTUALIZAR TÍTULO
        # -----------------------------------
    
        cantidad = len(resultados)
        total_str = f" de {total}" if total is not None and total != cantidad else ""

        titulo = (
            f"{modo} "
            f"{base} "
            f"({cantidad}{total_str})"
        )
    
        index_tab = (
            self.ui
            .tabwidget_resultados_consulta
            .indexOf(contenedor)
        )
    
        if index_tab != -1:
        
            self.ui.tabwidget_resultados_consulta.setTabText(
                index_tab,
                titulo
            )
    
            self.ui.tabwidget_resultados_consulta.setCurrentIndex(
                index_tab
            )
    
        # -----------------------------------
        # REFRESH VISUAL QT
        # -----------------------------------
    
        proxy.invalidate()
    
        tree.viewport().update()
    
        model.layoutChanged.emit()
    
    def editar_fila(self, index, clave):

        print("EDITAR_FILA")

        datos_tab = self.pestanas_resultados.get(clave)
        if not datos_tab:
            return

        proxy = datos_tab["proxy"]

        # siempre convertir a source
        index_source = proxy.mapToSource(index)

        fila = index_source.row()

        # obtener modelo REAL
        model = datos_tab["model"]

        # 🔥 ID seguro (desde cualquier columna de la fila)
        id_registro = model.item(fila, 0).data(Qt.UserRole)

        # 🔥 leer datos correctamente (SIN model.item)
        valores = []
        columnas = model.columnCount()

        for col in range(columnas):
            idx = model.index(fila, col)
            valores.append(idx.data())

        headers = [
            model.headerData(i, Qt.Horizontal)
            for i in range(columnas)
        ]

        print("ID:", id_registro)
        print("VALORES:", valores)

        # abrir editor SOLO en BUSQUEDA
        base = datos_tab["base"]

        self.ventana_edicion = VentanaEdicionRegistro(
            base=base,
            id_registro=id_registro,
            columnas=headers,
            valores=valores,
            parent=self
        )

        self.ventana_edicion.datos_actualizados.connect(
            self.actualizar_fila_treeview
        )

        self.ventana_edicion.exec()
        
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

    def actualizar_fila_treeview(self, base, id_registro, datos):
        
        for clave, tab in self.pestanas_resultados.items():
        
            if tab["base"] != base:
                continue
            
            model = tab["model"]
    
            for row in range(model.rowCount()):
            
                item = model.item(row, 0)
    
                if item and item.data(Qt.UserRole) == id_registro:
                
                    for col in range(model.columnCount()):
                        key = model.headerData(col, Qt.Horizontal)
    
                        if key in datos:
                            idx = model.index(row, col)
                            model.setData(idx, datos[key])
    
                    proxy = tab["proxy"]
                    proxy.invalidate()
                    tab["tree"].viewport().update()
    
                    return

    def actualizar_resaltado(self, texto):

        index = self.ui.tabwidget_resultados_consulta.currentIndex()
        if index == -1:
            return

        widget = self.ui.tabwidget_resultados_consulta.widget(index)

        datos = next(
            (d for d in self.pestanas_resultados.values()
             if d["contenedor"] is widget),
            None
        )

        if not datos:
            return

        datos["delegate"].set_criterio(texto)

        view = datos["tree"]
        model = view.model()

        model.layoutChanged.emit()

class VentanaEdicionRegistro(QDialog):

    datos_actualizados = Signal(str, int, dict)

    def __init__(self,
                 base,
                 id_registro,
                 columnas,
                 valores,
                 parent=None):

        super().__init__(parent)

        self.base = base
        self.id_registro = id_registro
        self.campos = {}

        self.setWindowIcon(QIcon("img/datcorr.ico"))
        self.resize(550, 500)

        logging.debug(f"[EDICION] {base} registro {id_registro}")

        self.setStyleSheet(style_dialog_dark())
        self.setWindowTitle(f"Editar registro - {base}")

        layout = QFormLayout(self)

        for col, val in zip(columnas, valores):
            if col.lower() in ("id", "id_datcorr_database"):
                continue

            label = QLabel(col)
            entry = QLineEdit("" if val is None else str(val))

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

        btn_guardar = QPushButton("Guardar cambios")
        btn_guardar.setStyleSheet(style_pushbutton_dark())
        btn_guardar.clicked.connect(self.guardar_cambios)
        btn_guardar.setAutoDefault(False)

        layout.addRow(btn_guardar)

    def guardar_cambios(self):

        datos_actualizados = {
            col: self.campos[col].text() for col in self.campos
        }

        try:

            result = SessionManager.get_db_client().actualizar(
                base=self.base,
                record_id=self.id_registro,
                data=datos_actualizados
            )

            if not result.get("success"):
                raise Exception(result.get("mensaje", "Error al actualizar"))

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