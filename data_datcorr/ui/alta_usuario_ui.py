# -*- coding: utf-8 -*-

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog,
    QGridLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QTableView)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(500, 350)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_nivel = QLabel(Dialog)
        self.label_nivel.setObjectName(u"label_nivel")
        self.gridLayout.addWidget(self.label_nivel, 2, 4, 1, 1)

        self.lineEdit_pass_alta = QLineEdit(Dialog)
        self.lineEdit_pass_alta.setObjectName(u"lineEdit_pass_alta")
        self.lineEdit_pass_alta.setEchoMode(QLineEdit.EchoMode.Password)
        self.gridLayout.addWidget(self.lineEdit_pass_alta, 1, 6, 1, 1)

        self.pushButton_cancelar = QPushButton(Dialog)
        self.pushButton_cancelar.setObjectName(u"pushButton_cancelar")
        self.gridLayout.addWidget(self.pushButton_cancelar, 5, 6, 1, 1)

        self.label_activo = QLabel(Dialog)
        self.label_activo.setObjectName(u"label_activo")
        self.gridLayout.addWidget(self.label_activo, 3, 4, 1, 1)

        self.label_nombre = QLabel(Dialog)
        self.label_nombre.setObjectName(u"label_nombre")
        self.gridLayout.addWidget(self.label_nombre, 0, 0, 1, 1)

        self.pushButton_guardar = QPushButton(Dialog)
        self.pushButton_guardar.setObjectName(u"pushButton_guardar")
        self.gridLayout.addWidget(self.pushButton_guardar, 5, 0, 1, 1)

        self.label_apellido = QLabel(Dialog)
        self.label_apellido.setObjectName(u"label_apellido")
        self.gridLayout.addWidget(self.label_apellido, 0, 4, 1, 1)

        self.lineEdit_apellido_alta = QLineEdit(Dialog)
        self.lineEdit_apellido_alta.setObjectName(u"lineEdit_apellido_alta")
        self.gridLayout.addWidget(self.lineEdit_apellido_alta, 0, 6, 1, 1)

        self.label_pass = QLabel(Dialog)
        self.label_pass.setObjectName(u"label_pass")
        self.gridLayout.addWidget(self.label_pass, 1, 4, 1, 1)

        self.label_usuario = QLabel(Dialog)
        self.label_usuario.setObjectName(u"label_usuario")
        self.gridLayout.addWidget(self.label_usuario, 1, 0, 1, 1)

        self.lineEdit_nombre_alta = QLineEdit(Dialog)
        self.lineEdit_nombre_alta.setObjectName(u"lineEdit_nombre_alta")
        self.gridLayout.addWidget(self.lineEdit_nombre_alta, 0, 2, 1, 1)

        self.tableViewlistar_usuarios_altas = QTableView(Dialog)
        self.tableViewlistar_usuarios_altas.setObjectName(u"tableViewlistar_usuarios_altas")
        self.gridLayout.addWidget(self.tableViewlistar_usuarios_altas, 4, 0, 1, 7)

        self.lineEdit_usuario_alta = QLineEdit(Dialog)
        self.lineEdit_usuario_alta.setObjectName(u"lineEdit_usuario_alta")
        self.gridLayout.addWidget(self.lineEdit_usuario_alta, 1, 2, 1, 1)

        self.label_rol = QLabel(Dialog)
        self.label_rol.setObjectName(u"label_rol")
        self.gridLayout.addWidget(self.label_rol, 2, 0, 1, 1)

        self.spinBox_nivel_alta = QSpinBox(Dialog)
        self.spinBox_nivel_alta.setObjectName(u"spinBox_nivel_alta")
        self.spinBox_nivel_alta.setMinimum(1)
        self.spinBox_nivel_alta.setMaximum(10)
        self.gridLayout.addWidget(self.spinBox_nivel_alta, 2, 6, 1, 1)

        self.checkBox_activo_alta = QCheckBox(Dialog)
        self.checkBox_activo_alta.setObjectName(u"checkBox_activo_alta")
        self.gridLayout.addWidget(self.checkBox_activo_alta, 3, 6, 1, 1)

        self.comboBox_rol_alta = QComboBox(Dialog)
        self.comboBox_rol_alta.setObjectName(u"comboBox_rol_alta")
        self.gridLayout.addWidget(self.comboBox_rol_alta, 2, 2, 1, 1)

        self.label_email = QLabel(Dialog)
        self.label_email.setObjectName(u"label_email")
        self.gridLayout.addWidget(self.label_email, 3, 0, 1, 1)

        self.lineEdit_email_alta = QLineEdit(Dialog)
        self.lineEdit_email_alta.setObjectName(u"lineEdit_email_alta")
        self.gridLayout.addWidget(self.lineEdit_email_alta, 3, 2, 1, 1)

        self.retranslateUi(Dialog)
        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Alta Usuario", None))
        self.label_nivel.setText(QCoreApplication.translate("Dialog", u"Nivel:", None))
        self.pushButton_cancelar.setText(QCoreApplication.translate("Dialog", u"Cancelar", None))
        self.label_activo.setText(QCoreApplication.translate("Dialog", u"Activo:", None))
        self.label_nombre.setText(QCoreApplication.translate("Dialog", u"Nombre:", None))
        self.pushButton_guardar.setText(QCoreApplication.translate("Dialog", u"Guardar", None))
        self.label_apellido.setText(QCoreApplication.translate("Dialog", u"Apellido:", None))
        self.label_pass.setText(QCoreApplication.translate("Dialog", u"Password:", None))
        self.label_usuario.setText(QCoreApplication.translate("Dialog", u"Usuario:", None))
        self.label_rol.setText(QCoreApplication.translate("Dialog", u"Rol:", None))
        self.checkBox_activo_alta.setText(QCoreApplication.translate("Dialog", u"Usuario Activo", None))
        self.label_email.setText(QCoreApplication.translate("Dialog", u"Email:", None))
