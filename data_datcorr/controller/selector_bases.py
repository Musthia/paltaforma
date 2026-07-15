# controller/selector_bases.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QComboBox, QPushButton, QMessageBox
)

from ui.styles import style_combobox_dark
from ui.styles import style_pushbutton_dark


class SelectorBasesDialog(QDialog):
    """
    Diálogo no modal para seleccionar una base de datos desde PostgreSQL
    """

    def __init__(self, bases_disponibles=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Seleccionar base de datos")
        self.setMinimumWidth(300)

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Seleccione una base de datos:")
        self.combo_bases = QComboBox()
        self.combo_bases.setStyleSheet(style_combobox_dark())

        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_aceptar.setStyleSheet(style_pushbutton_dark())

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo_bases)
        self.layout.addWidget(self.btn_aceptar)

        self._cargar_bases(bases_disponibles)

    def _cargar_bases(self, bases_disponibles=None):

        bases = bases_disponibles or []

        if not bases:
            QMessageBox.information(
                self,
                "Sin bases",
                "No se encontraron bases de datos en PostgreSQL"
            )
            return

        self.combo_bases.addItems(bases)

    def base_seleccionada(self):
        base = self.combo_bases.currentText()

        return base
