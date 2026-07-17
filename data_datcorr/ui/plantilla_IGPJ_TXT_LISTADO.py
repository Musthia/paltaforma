from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QTreeView, QListWidget, QListWidgetItem,
)
from PySide6.QtCore import Qt, QTimer, QEvent, QPoint
from PySide6.QtGui import QStandardItemModel, QStandardItem

from core.api_dao import ApiDAOPostgres
from utils.organismos import columnas_para_base
from ui.styles import (
    style_messagebox_dark,
    style_lineedit_error,
    style_lineedit_validation,
)
import ui.labels_png_rc


class Plantilla(QWidget):
    CAMPOS_CARGA_POR_ORIGEN = {
        "entidad": ["entidad"],
        "localidad": ["localidad"],
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
        self.base_actual = base_actual

        self._build_ui()
        self._actualizando = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.setStyleSheet(style_lineedit_validation())
        self._configurar_navegacion_enter()
        QTimer.singleShot(0, self.ui.line_carpetas.setFocus)

        self.dao_pg = ApiDAOPostgres(self.base_actual)
        self.ui.pushButton_guardar.clicked.connect(self.guardar_registro)

        self.modelo_sesion = QStandardItemModel(self)
        self.modelo_sesion.itemChanged.connect(self._item_editado)
        self.modelo_sesion.setHorizontalHeaderLabels([
            "Carpetas", "Caja", "Observacion", "Prefijo", "Legajo",
            "Localidad", "Entidad", "Año", "Expediente", "Documento",
            "Estado", "Ingreso", "Egreso",
        ])

        self.ui.treeView_resultados.setModel(self.modelo_sesion)
        self.ui.treeView_resultados.setRootIsDecorated(False)
        self.ui.treeView_resultados.setAlternatingRowColors(True)
        self.ui.treeView_resultados.setFocusPolicy(Qt.StrongFocus)

        self._init_autocompletado()

    def _build_ui(self):
        self.ui = QWidget()
        grid = QGridLayout(self.ui)

        self.ui.line_carpetas = QLineEdit()
        self.ui.line_caja = QLineEdit()
        self.ui.line_observaciones = QLineEdit()
        self.ui.line_prefijo = QLineEdit()
        self.ui.line_legajo = QLineEdit()
        self.ui.line_localidad = QLineEdit()
        self.ui.line_entidad = QLineEdit()
        self.ui.line_anio = QLineEdit()
        self.ui.line_expediente = QLineEdit()
        self.ui.line_documento = QLineEdit()
        self.ui.line_estado = QLineEdit()
        self.ui.line_ingreso = QLineEdit()
        self.ui.line_egreso = QLineEdit()

        campos = [
            ("CARPETAS:", self.ui.line_carpetas),
            ("CAJA:", self.ui.line_caja),
            ("OBSERVACION:", self.ui.line_observaciones),
            ("PREFIJO:", self.ui.line_prefijo),
            ("LEGAJO:", self.ui.line_legajo),
            ("LOCALIDAD:", self.ui.line_localidad),
            ("ENTIDAD:", self.ui.line_entidad),
            ("AÑO:", self.ui.line_anio),
            ("EXPEDIENTE:", self.ui.line_expediente),
            ("DOCUMENTO:", self.ui.line_documento),
            ("ESTADO:", self.ui.line_estado),
            ("INGRESO:", self.ui.line_ingreso),
            ("EGRESO:", self.ui.line_egreso),
        ]
        for i, (text, le) in enumerate(campos):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: bold; font-size: 12px; padding-bottom: 2px;")
            grid.addWidget(lbl, i, 0)
            grid.addWidget(le, i, 1)

        btn_row = grid.rowCount()
        self.ui.pushButton_guardar = QPushButton("Guardar")
        self.ui.pushButton_guardar.setStyleSheet("background-color: #2e7d32; color: white; padding: 6px 16px; border-radius: 4px;")
        grid.addWidget(self.ui.pushButton_guardar, btn_row, 0, 1, 2)

        tree_row = grid.rowCount()
        self.ui.treeView_resultados = QTreeView()
        self.ui.treeView_resultados.setMinimumHeight(200)
        grid.addWidget(self.ui.treeView_resultados, tree_row, 0, 1, 2)

        self._estilizar_campos()

    def _estilizar_campos(self):
        style = """
            QLineEdit {
                background-color: #cfd8dc;
                border: 2px solid #455a64;
                padding: 4px 10px;
                color: #000012;
                font-size: 13px;
                border-top-color: #a7b1b7;
                border-left-color: #a7b1b7;
                border-right-color: #2e3d45;
                border-bottom-color: #2e3d45;
            }
        """
        for widget in self.findChildren(QLineEdit):
            widget.setStyleSheet(style)

    def _init_autocompletado(self):
        self.autocomplete_campos = {
            self.ui.line_entidad: "entidad",
        }
        self._timer_autocomplete = QTimer(self)
        self._timer_autocomplete.setSingleShot(True)
        self._timer_autocomplete.timeout.connect(self._ejecutar_busqueda_autocomplete)
        self._texto_pendiente = ""
        self._lineedit_pendiente = None

        self.lista_autocomplete = QListWidget(self)
        self.lista_autocomplete.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.lista_autocomplete.setFocusPolicy(Qt.NoFocus)
        self.lista_autocomplete.setMouseTracking(True)
        self.lista_autocomplete.itemClicked.connect(self._autocomplete_item_seleccionado)
        self.lista_autocomplete.itemClicked.connect(lambda _: self._aceptar_autocomplete())
        self._campo_autocomplete_actual = None

        for lineedit in self.autocomplete_campos:
            lineedit.textEdited.connect(
                lambda texto, le=lineedit: self._buscar_autocomplete(le, texto)
            )
        for line in (self.ui.line_entidad,):
            line.installEventFilter(self)

    def _buscar_autocomplete(self, lineedit, texto):
        if self._actualizando:
            return
        if len(texto) < 1:
            self.lista_autocomplete.hide()
            return
        self._lineedit_pendiente = lineedit
        self._texto_pendiente = texto
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
        columna_origen = self.autocomplete_campos.get(self._campo_autocomplete_actual)
        if columna_origen not in self.CAMPOS_CARGA_POR_ORIGEN:
            return
        campos_a_cargar = self.CAMPOS_CARGA_POR_ORIGEN[columna_origen]
        try:
            todas_columnas = columnas_para_base(self.base_actual)
            datos = self.dao_pg.cargar_por_id(id_registro, todas_columnas)
            if not datos:
                return
            self._actualizando = True
            m = {
                "carpetas": self.ui.line_carpetas,
                "caja": self.ui.line_caja,
                "observacion": self.ui.line_observaciones,
                "prefijo": self.ui.line_prefijo,
                "legajo": self.ui.line_legajo,
                "localidad": self.ui.line_localidad,
                "entidad": self.ui.line_entidad,
                "anio": self.ui.line_anio,
                "expediente": self.ui.line_expediente,
                "documento": self.ui.line_documento,
                "estado": self.ui.line_estado,
                "ingreso": self.ui.line_ingreso,
                "egreso": self.ui.line_egreso,
            }
            for campo in campos_a_cargar:
                if campo in m and datos.get(campo):
                    m[campo].setText(str(datos[campo]) or "")
        finally:
            self._actualizando = False
            self.lista_autocomplete.hide()
        if hasattr(self.ui, 'line_entidad'):
            self.ui.line_entidad.setFocus()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if not self.lista_autocomplete.isVisible():
                return super().eventFilter(obj, event)
            key = event.key()
            if key == Qt.Key_Escape:
                self.lista_autocomplete.hide()
                return True
            if key in (Qt.Key_Return, Qt.Key_Enter):
                self._aceptar_autocomplete()
                return True
            if key == Qt.Key_Down:
                fila = self.lista_autocomplete.currentRow()
                if fila < self.lista_autocomplete.count() - 1:
                    self.lista_autocomplete.setCurrentRow(fila + 1)
                return True
            if key == Qt.Key_Up:
                fila = self.lista_autocomplete.currentRow()
                if fila > 0:
                    self.lista_autocomplete.setCurrentRow(fila - 1)
                return True
        return super().eventFilter(obj, event)

    def _aceptar_autocomplete(self):
        item = self.lista_autocomplete.currentItem()
        if not item and self.lista_autocomplete.count() > 0:
            item = self.lista_autocomplete.item(0)
        if not item:
            return
        texto = item.text()
        id_registro = item.data(Qt.UserRole)
        lineedit = self._campo_autocomplete_actual
        if not lineedit:
            return
        self._actualizando = True
        lineedit.setText(texto)
        self._actualizando = False
        self.lista_autocomplete.hide()
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
            self.dao_pg.actualizar(id_registro=id_registro, columna=columna_db, valor=nuevo_valor)
            self._mostrar_aviso("Cambios guardados", tiempo_ms=2500)
        except Exception as e:
            QMessageBox.critical(self, "Error al actualizar", str(e))
        finally:
            self._actualizando = False

    def _configurar_navegacion_enter(self):
        campos = [
            self.ui.line_carpetas, self.ui.line_caja, self.ui.line_observaciones,
            self.ui.line_prefijo, self.ui.line_legajo, self.ui.line_localidad,
            self.ui.line_entidad, self.ui.line_anio, self.ui.line_expediente,
            self.ui.line_documento, self.ui.line_estado, self.ui.line_ingreso,
            self.ui.line_egreso,
        ]
        for actual, siguiente in zip(campos, campos[1:]):
            actual.returnPressed.connect(lambda s=siguiente: self._pasar_foco(s))

    def _pasar_foco(self, widget):
        widget.setFocus()
        widget.selectAll()

    def _validar_campos_obligatorios(self):
        campos = [
            ("Carpetas", self.ui.line_carpetas),
            ("Caja", self.ui.line_caja),
            ("Observacion", self.ui.line_observaciones),
            ("Prefijo", self.ui.line_prefijo),
            ("Legajo", self.ui.line_legajo),
            ("Localidad", self.ui.line_localidad),
            ("Entidad", self.ui.line_entidad),
            ("Año", self.ui.line_anio),
            ("Expediente", self.ui.line_expediente),
            ("Documento", self.ui.line_documento),
            ("Estado", self.ui.line_estado),
            ("Ingreso", self.ui.line_ingreso),
            ("Egreso", self.ui.line_egreso),
        ]
        for nombre, widget in campos:
            widget.setProperty("error", False)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            if not widget.text().strip():
                widget.setProperty("error", True)
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                QMessageBox.warning(self, "Campo obligatorio", f"El campo «{nombre}» no puede estar vacío.")
                widget.setFocus()
                widget.selectAll()
                return False
        return True

    def guardar_registro(self):
        if not self._validar_campos_obligatorios():
            return
        try:
            datos = [
                self.ui.line_carpetas.text(), self.ui.line_caja.text(),
                self.ui.line_observaciones.text(), self.ui.line_prefijo.text(),
                self.ui.line_legajo.text(), self.ui.line_localidad.text(),
                self.ui.line_entidad.text(), self.ui.line_anio.text(),
                self.ui.line_expediente.text(), self.ui.line_documento.text(),
                self.ui.line_estado.text(), self.ui.line_ingreso.text(),
                self.ui.line_egreso.text(),
            ]
            id_registro = self.dao_pg.insertar(**dict(zip(columnas_para_base(self.base_actual), datos)))
            fila = []
            for valor in datos:
                item = QStandardItem(valor)
                item.setEditable(True)
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
                background-color: #2e7d32; color: white;
                padding: 8px 16px; border-radius: 6px; font-weight: bold;
            }
        """)
        label.adjustSize()
        x = self.width() - label.width() - 20
        y = self.height() - label.height() - 20
        label.move(x, y)
        label.show()
        self._label_aviso = label
        QTimer.singleShot(tiempo_ms, lambda: self._cerrar_aviso())

    def _cerrar_aviso(self):
        if hasattr(self, "_label_aviso") and self._label_aviso is not None:
            try:
                self._label_aviso.deleteLater()
            except RuntimeError:
                pass
            self._label_aviso = None

    def limpiar_campos(self):
        self.ui.line_legajo.clear()
        self.ui.line_localidad.clear()
        self.ui.line_entidad.clear()
        self.ui.line_entidad.setFocus()

    def eliminar_registro(self):
        index = self.ui.treeView_resultados.currentIndex()
        if not index.isValid():
            return
        fila = index.row()
        item = self.modelo_sesion.item(fila, 0)
        id_registro = item.data(Qt.UserRole)
        if id_registro is None:
            return
        confirmar = QMessageBox.question(
            self, "Eliminar registro",
            "¿Eliminar definitivamente este registro?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmar != QMessageBox.Yes:
            return
        try:
            self.dao_pg.eliminar(id_registro)
            self.modelo_sesion.removeRow(fila)
        except Exception as e:
            QMessageBox.critical(self, "Error al eliminar", str(e))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.eliminar_registro()
            return
        super().keyPressEvent(event)
