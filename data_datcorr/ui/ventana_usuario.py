# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ventana_usuario.ui'
##
## Created by: Qt User Interface Compiler version 6.10.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QPushButton,
    QSizePolicy, QTableView, QWidget)

class Ui_VentanaUsuarios(object):
    def setupUi(self, VentanaUsuarios):
        if not VentanaUsuarios.objectName():
            VentanaUsuarios.setObjectName(u"VentanaUsuarios")
        VentanaUsuarios.resize(400, 300)
        self.gridLayout = QGridLayout(VentanaUsuarios)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_desactivar_usuario = QPushButton(VentanaUsuarios)
        self.pushButton_desactivar_usuario.setObjectName(u"pushButton_desactivar_usuario")

        self.gridLayout.addWidget(self.pushButton_desactivar_usuario, 1, 3, 1, 1)

        self.tableViewlistar_usuarios = QTableView(VentanaUsuarios)
        self.tableViewlistar_usuarios.setObjectName(u"tableViewlistar_usuarios")

        self.gridLayout.addWidget(self.tableViewlistar_usuarios, 0, 0, 1, 4)

        self.pushButton_actualizar_usuarios = QPushButton(VentanaUsuarios)
        self.pushButton_actualizar_usuarios.setObjectName(u"pushButton_actualizar_usuarios")

        self.gridLayout.addWidget(self.pushButton_actualizar_usuarios, 1, 0, 1, 1)

        self.pushButton_activar_usuario = QPushButton(VentanaUsuarios)
        self.pushButton_activar_usuario.setObjectName(u"pushButton_activar_usuario")

        self.gridLayout.addWidget(self.pushButton_activar_usuario, 1, 1, 1, 2)

        self.pushButton_editar_usuario = QPushButton(VentanaUsuarios)
        self.pushButton_editar_usuario.setObjectName(u"pushButton_editar_usuario")

        self.gridLayout.addWidget(self.pushButton_editar_usuario, 2, 0, 1, 1)

        self.pushButton_permiso_usuario = QPushButton(VentanaUsuarios)
        self.pushButton_permiso_usuario.setObjectName(u"pushButton_permiso_usuario")

        self.gridLayout.addWidget(self.pushButton_permiso_usuario, 2, 3, 1, 1)

        self.pushButton_nuevo_usuario = QPushButton(VentanaUsuarios)
        self.pushButton_nuevo_usuario.setObjectName(u"pushButton_nuevo_usuario")

        self.gridLayout.addWidget(self.pushButton_nuevo_usuario, 2, 1, 1, 1)


        self.retranslateUi(VentanaUsuarios)

        QMetaObject.connectSlotsByName(VentanaUsuarios)
    # setupUi

    def retranslateUi(self, VentanaUsuarios):
        VentanaUsuarios.setWindowTitle(QCoreApplication.translate("VentanaUsuarios", u"Manejo De Usuarios", None))
        self.pushButton_desactivar_usuario.setText(QCoreApplication.translate("VentanaUsuarios", u"Desactivar Usuario", None))
        self.pushButton_actualizar_usuarios.setText(QCoreApplication.translate("VentanaUsuarios", u"Actualizar Usuario", None))
        self.pushButton_activar_usuario.setText(QCoreApplication.translate("VentanaUsuarios", u"Activar Usuario", None))
        self.pushButton_editar_usuario.setText(QCoreApplication.translate("VentanaUsuarios", u"Editar", None))
        self.pushButton_permiso_usuario.setText(QCoreApplication.translate("VentanaUsuarios", u"Permisos de Usuario", None))
        self.pushButton_nuevo_usuario.setText(QCoreApplication.translate("VentanaUsuarios", u"Nuevo", None))
    # retranslateUi

