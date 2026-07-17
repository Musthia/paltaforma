import os

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
    QHeaderView, QWidget, QFormLayout, QLineEdit, QDateEdit,
    QGroupBox, QGridLayout, QFrame, QFileDialog,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon

from core.session_manager import SessionManager


class ReportesViewer(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Reportes")
        self.setWindowIcon(QIcon("img/datcorr.ico"))
        self.resize(1000, 700)

        self._consultas = []
        self._consulta_actual = None
        self._filtros_widgets = {}
        self._datos = []
        self._columnas = []

        layout = QVBoxLayout(self)

        # KPIs
        self._kpis_group = QGroupBox("Indicadores")
        kpi_layout = QGridLayout(self._kpis_group)
        self._kpi_labels = {}
        for i, (key, label) in enumerate([
            ("total_registros", "Total Registros"),
            ("usuarios_activos", "Usuarios Activos"),
            ("total_usuarios", "Total Usuarios"),
            ("alertas_pendientes", "Alertas Pendientes"),
        ]):
            lbl = QLabel("--")
            lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976d2;")
            self._kpi_labels[key] = lbl
            kpi_layout.addWidget(QLabel(label), 0, i)
            kpi_layout.addWidget(lbl, 1, i)
        layout.addWidget(self._kpis_group)

        # Selector de reporte
        sel_layout = QHBoxLayout()
        sel_layout.addWidget(QLabel("Reporte:"))
        self._combo_reporte = QComboBox()
        self._combo_reporte.setMinimumWidth(300)
        self._combo_reporte.currentIndexChanged.connect(self._on_reporte_changed)
        sel_layout.addWidget(self._combo_reporte)
        self._btn_generar = QPushButton("Generar")
        self._btn_generar.clicked.connect(self._generar)
        sel_layout.addWidget(self._btn_generar)
        layout.addLayout(sel_layout)

        # Filtros dinámicos
        self._filtros_frame = QFrame()
        self._filtros_layout = QHBoxLayout(self._filtros_frame)
        layout.addWidget(self._filtros_frame)

        # Tabla de resultados
        self._tabla = QTableWidget()
        self._tabla.setAlternatingRowColors(True)
        self._tabla.horizontalHeader().setStretchLastSection(True)
        self._tabla.setSortingEnabled(True)
        layout.addWidget(self._tabla)

        # Export buttons
        exp_layout = QHBoxLayout()
        self._btn_csv = QPushButton("CSV")
        self._btn_csv.clicked.connect(lambda: self._exportar("csv"))
        self._btn_xlsx = QPushButton("XLSX")
        self._btn_xlsx.clicked.connect(lambda: self._exportar("xlsx"))
        self._btn_pdf = QPushButton("PDF")
        self._btn_pdf.clicked.connect(lambda: self._exportar("pdf"))
        for b in (self._btn_csv, self._btn_xlsx, self._btn_pdf):
            b.setEnabled(False)
            exp_layout.addWidget(b)
        layout.addLayout(exp_layout)

        self._cargar_consultas()
        self._cargar_kpis()

    def _cargar_consultas(self):
        client = SessionManager.get_reportes_client()
        if not client:
            return
        data = client.listar_consultas()
        if not isinstance(data, dict):
            return
        if not data.get("success", True):
            QMessageBox.warning(self, "Reportes", data.get("mensaje", "Error al cargar reportes"))
            return
        self._consultas = data.get("consultas", [])
        self._combo_reporte.clear()
        self._combo_reporte.addItem("-- Seleccionar --", None)
        for c in self._consultas:
            self._combo_reporte.addItem(f"{c['nombre']} — {c['descripcion']}", c["id"])

    def _cargar_kpis(self):
        client = SessionManager.get_reportes_client()
        if not client:
            return
        data = client.kpis()
        if isinstance(data, dict) and data.get("success", True):
            for key, lbl in self._kpi_labels.items():
                val = data.get(key, "--")
                if val is not None:
                    lbl.setText(str(val))

    def _on_reporte_changed(self, idx):
        consulta_id = self._combo_reporte.currentData()
        self._consulta_actual = None
        self._tabla.setRowCount(0)
        self._tabla.setColumnCount(0)
        for b in (self._btn_csv, self._btn_xlsx, self._btn_pdf):
            b.setEnabled(False)

        # Limpiar filtros viejos
        for w in list(self._filtros_widgets.values()):
            w.deleteLater() if hasattr(w, "deleteLater") else None
            if isinstance(w, dict):
                for sub in w.values():
                    sub.deleteLater() if hasattr(sub, "deleteLater") else None
        self._filtros_widgets = {}

        if not consulta_id:
            return

        for c in self._consultas:
            if c["id"] == consulta_id:
                self._consulta_actual = c
                break

        if not self._consulta_actual:
            return

        filtros = self._consulta_actual.get("filtros", [])
        for f in filtros:
            fkey = f["key"]
            ftype = f["tipo"]
            if ftype == "date":
                de = QDateEdit()
                de.setCalendarPopup(True)
                de.setDate(QDate.currentDate())
                de.setDisplayFormat("yyyy-MM-dd")
                self._filtros_widgets[fkey] = de
                self._filtros_layout.addWidget(QLabel(f["label"]))
                self._filtros_layout.addWidget(de)
            elif ftype == "text":
                le = QLineEdit()
                le.setPlaceholderText(f["label"])
                self._filtros_widgets[fkey] = le
                self._filtros_layout.addWidget(QLabel(f["label"]))
                self._filtros_layout.addWidget(le)
            elif ftype == "select":
                cb = QComboBox()
                for opt in f.get("opciones", []):
                    cb.addItem(opt["texto"], opt["valor"])
                self._filtros_widgets[fkey] = cb
                self._filtros_layout.addWidget(QLabel(f["label"]))
                self._filtros_layout.addWidget(cb)

    def _generar(self):
        if not self._consulta_actual:
            QMessageBox.warning(self, "Sin reporte", "Seleccione un reporte.")
            return

        consulta_id = self._consulta_actual["id"]
        filtros = {}
        for key, widget in self._filtros_widgets.items():
            if isinstance(widget, QDateEdit):
                val = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QComboBox):
                val = widget.currentData()
            elif isinstance(widget, QLineEdit):
                val = widget.text().strip()
            else:
                val = ""
            if val:
                filtros[key] = val

        client = SessionManager.get_reportes_client()
        if not client:
            return

        data = client.ejecutar_consulta(consulta_id, **filtros)
        if not isinstance(data, dict):
            QMessageBox.critical(self, "Error", "Respuesta inválida del servidor")
            return

        if not data.get("success", True):
            QMessageBox.critical(self, "Error", data.get("mensaje", "Error al ejecutar reporte"))
            return

        self._columnas = data.get("columnas", [])
        self._datos = data.get("datos", [])

        self._tabla.setColumnCount(len(self._columnas))
        self._tabla.setHorizontalHeaderLabels(self._columnas)
        self._tabla.setRowCount(len(self._datos))

        for row_idx, row_data in enumerate(self._datos):
            for col_idx, col_name in enumerate(self._columnas):
                val = row_data.get(col_name, "")
                item = QTableWidgetItem(str(val) if val is not None else "")
                self._tabla.setItem(row_idx, col_idx, item)

        self._tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        has_data = len(self._datos) > 0
        for b in (self._btn_csv, self._btn_xlsx, self._btn_pdf):
            b.setEnabled(has_data)

    def _exportar(self, formato):
        if not self._consulta_actual:
            return
        consulta_id = self._consulta_actual["id"]

        filtros = {}
        for key, widget in self._filtros_widgets.items():
            if isinstance(widget, QDateEdit):
                val = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QComboBox):
                val = widget.currentData()
            elif isinstance(widget, QLineEdit):
                val = widget.text().strip()
            else:
                val = ""
            if val:
                filtros[key] = val

        default_name = f"reporte_{consulta_id}.{formato}"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar reporte", default_name,
            f"*.{formato}" if formato != "csv" else "CSV (*.csv)"
        )
        if not file_path:
            return

        client = SessionManager.get_reportes_client()
        if not client:
            return

        raw = client.exportar_consulta(consulta_id, formato=formato, **filtros)
        if isinstance(raw, dict) and not raw.get("success", True):
            QMessageBox.critical(self, "Error", raw.get("mensaje", "Error al exportar"))
            return

        try:
            with open(file_path, "wb") as f:
                if isinstance(raw, bytes):
                    f.write(raw)
                else:
                    f.write(raw.encode("utf-8"))
            QMessageBox.information(self, "Exportar", f"Reporte guardado en:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{e}")