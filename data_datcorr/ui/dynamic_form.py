# ui/dynamic_form.py

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton
)


class DynamicForm(QDialog):

    def __init__(self, router, schema, table, data):
        super().__init__()

        self.router = router
        self.schema = schema
        self.table = table
        self.data = data

        self.inputs = {}

        self.setWindowTitle("Editar Registro")

        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.build_form()

    def build_form(self):

        # -----------------------------------
        # CREAR CAMPOS DINÁMICOS
        # -----------------------------------
        for key, value in self.data.items():

            input_field = QLineEdit()
            input_field.setText(str(value))

            self.inputs[key] = input_field

            self.layout.addRow(key, input_field)

        # -----------------------------------
        # BOTÓN GUARDAR
        # -----------------------------------
        btn = QPushButton("Guardar")
        btn.clicked.connect(self.save_data)

        self.layout.addRow(btn)

    def save_data(self):

        # -----------------------------------
        # ARMAR DATA EDITADA
        # -----------------------------------
        updated_data = {
            key: field.text()
            for key, field in self.inputs.items()
        }

        # -----------------------------------
        # ID (OBLIGATORIO)
        # -----------------------------------
        record_id = updated_data.get("id_Datcorr_database")

        # -----------------------------------
        # ACTUALIZAR BD
        # -----------------------------------
        self.router.update_by_id(
            self.schema,
            self.table,
            "id_Datcorr_database",
            record_id,
            updated_data
        )

        self.accept()