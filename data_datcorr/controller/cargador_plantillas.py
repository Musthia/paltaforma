# controller/cargador_plantillas.py

import importlib
from PySide6.QtWidgets import QMessageBox


def cargar_plantilla(nombre_base, tabwidget, parent=None):
    modulo_nombre = f"ui.plantilla_{nombre_base}"
    #modulo_nombre = f"ui.plantilla_MATERNIDAD"

    try:
        modulo = importlib.import_module(modulo_nombre)
    except ModuleNotFoundError:
        QMessageBox.warning(
            parent,
            "Plantilla no encontrada",
            f"No existe {modulo_nombre}.py"
        )
        return

    if not hasattr(modulo, "Plantilla"):
        QMessageBox.warning(
            parent,
            "Error",
            "La plantilla no contiene la clase 'Plantilla'"
        )
        return

    # 🔎 BUSCAR SI YA EXISTE
    for i in range(tabwidget.count()):
        widget_existente = tabwidget.widget(i)
        if widget_existente.property("base_nombre") == nombre_base:
            tabwidget.setCurrentIndex(i)
            return

    # 🆕 CREAR NUEVA
    #widget = modulo.Plantilla(parent)
    widget = modulo.Plantilla(
        base_actual=nombre_base,
        parent=parent
    )

    widget.setProperty("base_nombre", nombre_base)

    titulo = f"CARGA BASE {nombre_base}"
    tabwidget.addTab(widget, titulo)
    tabwidget.setCurrentWidget(widget)