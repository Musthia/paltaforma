# ui/plantilla_igpj.py

# =========================
# Librerías estándar
# =========================
import os

# =========================
# PySide6 - Widgets
# =========================
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
)

# =========================
# PySide6 - Core
# =========================
from PySide6.QtCore import (
    Qt,
    QFile,
    QTimer,
    QEvent,
    QPoint,
)

# =========================
# PySide6 - Gui
# =========================
from PySide6.QtGui import (
    QStandardItemModel,
    QStandardItem,
)

# =========================
# Qt Designer Loader
# =========================
from PySide6.QtUiTools import QUiLoader

# =========================
# Proyecto / Modelo
# =========================
from core.api_dao import ApiDAOPostgres
from utils.organismos import (
    columnas_para_base,
)

# =========================
# Estilos
# =========================
from ui.styles import (
    style_messagebox_dark,
    style_lineedit_error,
    style_lineedit_validation,
)

# =========================
# Recursos Qt (icons / png)
# =========================
import ui.labels_png_rc


class Plantilla(QWidget):
    CAMPOS_CARGA_POR_ORIGEN = {
        "entidad": [
            "entidad", 
            
        ],
        """  "expediente": [
            "expediente", 
        ],
        """
        "localidad": [
            "localidad", 
            
        ]
    }

    MAPEO_COLUMNAS_DB = {
            "Carpetas": "carpetas",
            "Caja": "caja",
            "Observacion": "observacion",
            "Prefijo": "prefijo",
            "Legajo": "legajoo",
            "Localidad": "localidad",
            "Entidad": "entidad",
            "Año": "anio",
            "Expediente": "expediente",
            "Documento": "documento",
            "Estado": "estado",
            "Ingreso": "ingreso",
            "Egreso": "egreso",         
        }
     
    def __init__(self, base_actual, parent=None):
        super().__init__(parent)

        self.base_actual = base_actual  # ✅ CLAVE

        ruta_ui = os.path.join(
            os.path.dirname(__file__),
            "plantilla_igpj_listado_nuevo.ui"
        )

        loader = QUiLoader()
        archivo_ui = QFile(ruta_ui)
        archivo_ui.open(QFile.ReadOnly)

        self.ui = loader.load(archivo_ui, self)
        archivo_ui.close()

        self._actualizando = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # ---------- ESTILOS ----------
        self.setStyleSheet(style_lineedit_validation())

        # ---------- NAVEGACIÓN ENTER ----------
        self._configurar_navegacion_enter()

        # ---------- FOCO INICIAL ----------
        QTimer.singleShot(
            0,
            self.ui.line_carpetas_listado_nuevo.setFocus
        )

        # ---------- CONEXIÓN DB ----------
        self.dao_pg = ApiDAOPostgres(self.base_actual)

        # ---------- CONEXIÓN BOTÓN ----------
        self.ui.pushButton_guardar_carga_igpj.clicked.connect(
            self.guardar_registro
        )
        
        # ---------- MODELO TREEVIEW (SESION ACTUAL) ----------
        self.modelo_sesion = QStandardItemModel(self)
        self.modelo_sesion.itemChanged.connect(self._item_editado)
        self.modelo_sesion.setHorizontalHeaderLabels([
           "Carpetas", 
           "Caja", 
           "Observacion", 
           "Prefijo", 
           "Legajo", 
           "Localidad",
           "Entidad", 
           "Año", 
           "Expediente", 
           "Documento", 
           "Estado",   
           "Ingreso", 
           "Egreso",
            
        ])

        self.ui.treeView_carga_igpj_listado_nuevo.setModel(self.modelo_sesion)
        self.ui.treeView_carga_igpj_listado_nuevo.setRootIsDecorated(False)
        self.ui.treeView_carga_igpj_listado_nuevo.setAlternatingRowColors(True)

        self.ui.treeView_carga_igpj_listado_nuevo.setFocusPolicy(Qt.StrongFocus)

        # ---------- AUTOCOMPLETADO ----------
        self._init_autocompletado()

    def _init_autocompletado(self):
        self.autocomplete_campos = {
            self.ui.line_entidad_listado_nuevo: "entidad",
            #self.ui.line_expediente_listado_nuevo: "expediente",
            #self.ui.line_departamento_listado_nuevo: "departamento",
           
        }

        self._timer_autocomplete = QTimer(self)
        self._timer_autocomplete.setSingleShot(True)
        self._timer_autocomplete.timeout.connect(
            self._ejecutar_busqueda_autocomplete
        )

        self._texto_pendiente = ""
        self._lineedit_pendiente = None

        self.lista_autocomplete = QListWidget(self)
        self.lista_autocomplete.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Tool
        )
        self.lista_autocomplete.setFocusPolicy(Qt.NoFocus)
        self.lista_autocomplete.setMouseTracking(True)

        self.lista_autocomplete.itemClicked.connect(
            self._autocomplete_item_seleccionado
        )

        self.lista_autocomplete.itemClicked.connect(
            lambda _: self._aceptar_autocomplete()
        )

        self._campo_autocomplete_actual = None

        for lineedit in self.autocomplete_campos:
            lineedit.textEdited.connect(
                lambda texto, le=lineedit: self._buscar_autocomplete(le, texto)
            )

        for line in (
            self.ui.line_entidad_listado_nuevo,
            #self.ui.line_expediente_listado_nuevo,
            #self.ui.line_departamento_listado_nuevo,
            
        ):
            line.installEventFilter(self)   

    def _buscar_autocomplete(self, lineedit, texto):
        if self._actualizando:
            return

        if len(texto) < 1:
            self.lista_autocomplete.hide()
            return

        # Guardamos intención
        self._lineedit_pendiente = lineedit
        self._texto_pendiente = texto

        # Reinicia el debounce
        self._timer_autocomplete.start(250)

    def _ejecutar_busqueda_autocomplete(self):
        if not getattr(self, "base_actual", None):
            self.lista_autocomplete.hide()
            return

        lineedit = self._lineedit_pendiente
        texto = self._texto_pendiente

        if not lineedit or len(texto) < 1:
            return

        columna = self.autocomplete_campos[lineedit]

        try:
            resultados = self.dao_pg.buscar_autocomplete(columna, texto)

        except Exception:
            self.lista_autocomplete.hide()
            return

        if not resultados:
            self.lista_autocomplete.hide()
            return

        self.lista_autocomplete.clear()

        for id_registro, valor in resultados:
            item = QListWidgetItem(str(valor))
            item.setData(Qt.UserRole, id_registro)
            self.lista_autocomplete.addItem(item)

        self._campo_autocomplete_actual = lineedit
        self._mostrar_lista_autocomplete(lineedit)

    def _mostrar_lista_autocomplete(self, lineedit):
        pos = lineedit.mapToGlobal(QPoint(0, lineedit.height()))
        self.lista_autocomplete.move(pos)
        self.lista_autocomplete.setFixedWidth(lineedit.width())
        self.lista_autocomplete.show()

    def _autocomplete_item_seleccionado(self, item):
        id_registro = item.data(Qt.UserRole)
        self.lista_autocomplete.hide()
    
        self._cargar_fila_completa(id_registro)

    def _cargar_fila_completa(self, id_registro):
        if not self._campo_autocomplete_actual:
            return

        columna_origen = self.autocomplete_campos.get(
            self._campo_autocomplete_actual
        )

        if columna_origen not in self.CAMPOS_CARGA_POR_ORIGEN:
            return

        campos_a_cargar = self.CAMPOS_CARGA_POR_ORIGEN[columna_origen]

        try:
            todas_columnas = columnas_para_base(self.base_actual)
            datos = self.dao_pg.cargar_por_id(id_registro, todas_columnas)

            if not datos:
                return

            self._actualizando = True

            # 🔹 Asignación SELECTIVA
            if "carpetas" in campos_a_cargar:
                self.ui.line_carpetas.setText(datos["carpetas"] or "")
            if "caja" in campos_a_cargar:
                self.ui.line_caja.setText(datos["caja"] or "")
            if "observacion" in campos_a_cargar:
                self.ui.line_observaciones.setText(datos["observacion"] or "")
            if "prefijo" in campos_a_cargar:
                self.ui.line_prefijo.setText(datos["prefijo"] or "")
            if "legajo" in campos_a_cargar:
                self.ui.line_legajo.setText(datos["legajo"] or "")
            if "localidad" in campos_a_cargar:
                self.ui.line_localidad.setText(datos["localidad"] or "")
            if "entidad" in campos_a_cargar:
                self.ui.line_denominacion.setText(datos["entidad"] or "")
            if "anio" in campos_a_cargar:
                self.ui.line_anio.setText(datos["anio"] or "")
            if "expediente" in campos_a_cargar:
                self.ui.line_expediente.setText(datos["expediente"] or "")
            if "documento" in campos_a_cargar:
                self.ui.line_documento.setText(datos["documento"] or "")
            if "estado" in campos_a_cargar:
                self.ui.line_estado.setText(datos["estado"] or "")
            if "ingreso" in campos_a_cargar:
                self.ui.line_ingreso.setText(datos["ingreso"] or "")
            if "egreso" in campos_a_cargar:
                self.ui.line_egreso.setText(datos["egreso"] or "")
           
        finally:
            self._actualizando = False
            self.lista_autocomplete.hide()

        self.ui.line_entidad.setFocus()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:

            if not self.lista_autocomplete.isVisible():
                return super().eventFilter(obj, event)

            key = event.key()

            # ESC → cerrar lista
            if key == Qt.Key_Escape:
                self.lista_autocomplete.hide()
                return True

            # ENTER → aceptar selección
            if key in (Qt.Key_Return, Qt.Key_Enter):
                self._aceptar_autocomplete()
                return True

            # ↓ navegar lista
            if key == Qt.Key_Down:
                fila = self.lista_autocomplete.currentRow()
                if fila < self.lista_autocomplete.count() - 1:
                    self.lista_autocomplete.setCurrentRow(fila + 1)
                return True

            # ↑ navegar lista
            if key == Qt.Key_Up:
                fila = self.lista_autocomplete.currentRow()
                if fila > 0:
                    self.lista_autocomplete.setCurrentRow(fila - 1)
                return True

        return super().eventFilter(obj, event)
    
    def _aceptar_autocomplete(self):
        item = self.lista_autocomplete.currentItem()

        # Si no hay selección, tomar el primero
        if not item and self.lista_autocomplete.count() > 0:
            item = self.lista_autocomplete.item(0)

        if not item:
            return

        texto = item.text()
        id_registro = item.data(Qt.UserRole)

        lineedit = self._campo_autocomplete_actual
        if not lineedit:
            return

        # Evita loop de señales
        self._actualizando = True
        lineedit.setText(texto)
        self._actualizando = False

        self.lista_autocomplete.hide()

        # Cargar datos completos del registro
        self._cargar_fila_completa(id_registro)

    def _item_editado(self, item):

        if self._actualizando:
            return

        id_registro = item.data(Qt.UserRole)
        if id_registro is None:
            return

        columna = item.column()
        nuevo_valor = item.text()

        nombre_visible = self.modelo_sesion.horizontalHeaderItem(columna).text()

        if nombre_visible not in self.MAPEO_COLUMNAS_DB:
            return

        columna_db = self.MAPEO_COLUMNAS_DB[nombre_visible]

        try:
            self._actualizando = True

            self.dao_pg.actualizar(
                id_registro=id_registro,
                columna=columna_db,
                valor=nuevo_valor
            )

            print(
                f"UPDATE OK -> ID:{id_registro} | "
                f"{columna_db} = {nuevo_valor}"
            )

            # ✅ AVISO VISUAL
            self._mostrar_aviso("✔ Cambios guardados", tiempo_ms=2500)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al actualizar",
                str(e)
            )

        finally:
            self._actualizando = False

    def _configurar_navegacion_enter(self):
        campos = [
            self.ui.line_carpetas_listado_nuevo,
            
            self.ui.line_observaciones_listado_nuevo,
            self.ui.line_prefijo_listado_nuevo,
            self.ui.line_documento_listado_nuevo,
            self.ui.line_estado_listado_nuevo,

            self.ui.line_ingreso_listado_nuevo,
            self.ui.line_egreso_listado_nuevo,

            self.ui.line_anio_listado_nuevo,
            self.ui.line_expediente_listado_nuevo,

            self.ui.line_caja_listado_nuevo,

            self.ui.line_entidad_listado_nuevo,

            self.ui.line_legajo_listado_nuevo,
            self.ui.line_localidad_listado_nuevo,
            
            
            
            
            
            
          
            ]

        for actual, siguiente in zip(campos, campos[1:]):
            actual.returnPressed.connect(
                lambda s=siguiente: self._pasar_foco(s)
            )

    def _pasar_foco(self, widget):
        widget.setFocus()
        widget.selectAll()

    def _validar_campos_obligatorios(self):

        campos = [
            ("Carpetas", self.ui.line_carpetas_listado_nuevo),
            ("Caja", self.ui.line_caja_listado_nuevo),
            ("Observacion", self.ui.line_observaciones_listado_nuevo),
            ("Prefijo", self.ui.line_prefijo_listado_nuevo),
            ("Legajo", self.ui.line_legajo_listado_nuevo),
            ("Localidad", self.ui.line_localidad_listado_nuevo),
            ("Entidad", self.ui.line_entidad_listado_nuevo),
            ("Año", self.ui.line_anio_listado_nuevo),
            ("Expediente", self.ui.line_expediente_listado_nuevo),
            ("Documento", self.ui.line_documento_listado_nuevo),
            ("Estado", self.ui.line_estado_listado_nuevo),
            ("Ingreso", self.ui.line_ingreso_listado_nuevo),
            ("Egreso", self.ui.line_egreso_listado_nuevo),
       
        ]

        for nombre, widget in campos:
            widget.setProperty("error", False)
            widget.style().unpolish(widget)
            widget.style().polish(widget)

            if not widget.text().strip():
                widget.setProperty("error", True)
                widget.style().unpolish(widget)
                widget.style().polish(widget)

                QMessageBox.warning(
                    self,
                    "Campo obligatorio",
                    f"El campo «{nombre}» no puede estar vacío."
                )
                widget.setFocus()
                widget.selectAll()
                return False

        return True

    def guardar_registro(self):
        if not self._validar_campos_obligatorios():
            return   # ❌ corta el guardado
    
        try:
            datos = [
                self.ui.line_carpetas_listado_nuevo.text(),
                self.ui.line_caja_listado_nuevo.text(),
                self.ui.line_observaciones_listado_nuevo.text(),
                self.ui.line_prefijo_listado_nuevo.text(),
                self.ui.line_legajo_listado_nuevo.text(),
                self.ui.line_localidad_listado_nuevo.text(),
                self.ui.line_entidad_listado_nuevo.text(),
                self.ui.line_anio_listado_nuevo.text(),
                self.ui.line_expediente_listado_nuevo.text(),
                self.ui.line_documento_listado_nuevo.text(),
                self.ui.line_estado_listado_nuevo.text(),
                self.ui.line_ingreso_listado_nuevo.text(),
                self.ui.line_egreso_listado_nuevo.text()
                          
            ]
    
            # ---- INSERTAR EN DB Y OBTENER ID ----
            id_registro = self.dao_pg.insertar(**dict(zip(columnas_para_base(self.base_actual), datos)))

            # ---- CREAR FILA ----
            fila = []

            for valor in datos:
                item = QStandardItem(valor)
                item.setEditable(True)

                # 🔑 Guardamos el ID en cada celda
                item.setData(id_registro, Qt.UserRole)

                fila.append(item)

            self.modelo_sesion.appendRow(fila)
    
            self.limpiar_campos()
    
        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error al guardar")
            msg.setText(str(e))
            msg.setStyleSheet(style_messagebox_dark())
            msg.exec()

    def _mostrar_aviso(self, texto, tiempo_ms=2000):
        """
        Aviso visual temporal tipo 'toast'
        """

        # 🔒 Si existe un aviso previo, eliminarlo de forma segura
        if hasattr(self, "_label_aviso") and self._label_aviso is not None:
            try:
                self._label_aviso.deleteLater()
            except RuntimeError:
                pass
            self._label_aviso = None

        label = QLabel(texto, self)
        label.setAlignment(Qt.AlignCenter)

        label.setStyleSheet("""
            QLabel {
                background-color: #2e7d32;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)

        label.adjustSize()

        # 📍 Posición
        x = self.width() - label.width() - 20
        y = self.height() - label.height() - 20
        label.move(x, y)

        label.show()

        self._label_aviso = label  # ✅ nueva referencia válida

        QTimer.singleShot(
            tiempo_ms,
            lambda: self._cerrar_aviso()
        )

    def _cerrar_aviso(self):
        if hasattr(self, "_label_aviso") and self._label_aviso is not None:
            try:
                self._label_aviso.deleteLater()
            except RuntimeError:
                pass
            self._label_aviso = None

    def limpiar_campos(self):
        #self.ui.line_carpetas_listado_nuevo.clear()
        #self.ui.line_caja_listado_nuevo.clear()
        #self.ui.line_observaciones_listado_nuevo.clear()
        #self.ui.line_prefijo_listado_nuevo.clear()
        self.ui.line_legajo_listado_nuevo.clear()
        self.ui.line_localidad_listado_nuevo.clear()
        self.ui.line_entidad_listado_nuevo.clear()
        #self.ui.line_anio_listado_nuevo.clear()
        #self.ui.line_expediente_listado_nuevo.clear()        
        #self.ui.line_documento_listado_nuevo.clear()
        #self.ui.line_estado_listado_nuevo.clear()
        #self.ui.line_ingreso_listado_nuevo.clear()
        #self.ui.line_egreso_listado_nuevo.clear()

        self.ui.line_entidad_listado_nuevo.setFocus()

    def eliminar_registro(self):
        index = self.ui.treeView_carga_ips.currentIndex()

        if not index.isValid():
            return  # nada seleccionado, no molestamos

        fila = index.row()

        item = self.modelo_sesion.item(fila, 0)
        id_registro = item.data(Qt.UserRole)

        if id_registro is None:
            return  # fila inválida o corrupta

        confirmar = QMessageBox.question(
            self,
            "Eliminar registro",
            "¿Eliminar definitivamente este registro?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmar != QMessageBox.Yes:
            return

        try:
            # DB
            self.dao_pg.eliminar(id_registro)

            # TreeView (solo esta sesión)
            self.modelo_sesion.removeRow(fila)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al eliminar",
                str(e)
            )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.eliminar_registro()
            return

        super().keyPressEvent(event)