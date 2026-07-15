# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'usuarios.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QTreeView, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(550, 350)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(550, 350))
        MainWindow.setMaximumSize(QSize(550, 350))
        icon = QIcon()
        icon.addFile(u"../img/Escudo.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setEnabled(False)
        self.label.setGeometry(QRect(-30, -10, 651, 371))
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label.setAutoFillBackground(True)
        self.label.setLineWidth(0)
        self.label.setPixmap(QPixmap(u"../img/autenticacion_de_usuario.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(False)
        self.treeView_usuarios = QTreeView(self.centralwidget)
        self.treeView_usuarios.setObjectName(u"treeView_usuarios")
        self.treeView_usuarios.setGeometry(QRect(70, 50, 401, 211))
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(100, 0, 331, 31))
        font = QFont()
        font.setFamilies([u"Algerian"])
        font.setPointSize(14)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setScaledContents(False)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(0, 270, 551, 46))
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.nombre_usuario_label = QLabel(self.widget)
        self.nombre_usuario_label.setObjectName(u"nombre_usuario_label")
        self.nombre_usuario_label.setEnabled(True)

        self.gridLayout.addWidget(self.nombre_usuario_label, 0, 0, 1, 1)

        self.usuario_usuario_label = QLabel(self.widget)
        self.usuario_usuario_label.setObjectName(u"usuario_usuario_label")
        self.usuario_usuario_label.setEnabled(True)

        self.gridLayout.addWidget(self.usuario_usuario_label, 0, 3, 1, 1)

        self.entry_usuario_nombre = QLineEdit(self.widget)
        self.entry_usuario_nombre.setObjectName(u"entry_usuario_nombre")

        self.gridLayout.addWidget(self.entry_usuario_nombre, 1, 0, 1, 2)

        self.entry_usuarios_apellido = QLineEdit(self.widget)
        self.entry_usuarios_apellido.setObjectName(u"entry_usuarios_apellido")

        self.gridLayout.addWidget(self.entry_usuarios_apellido, 1, 2, 1, 1)

        self.entry_usuario_usuario = QLineEdit(self.widget)
        self.entry_usuario_usuario.setObjectName(u"entry_usuario_usuario")

        self.gridLayout.addWidget(self.entry_usuario_usuario, 1, 3, 1, 1)

        self.entry_usuario_contrasena = QLineEdit(self.widget)
        self.entry_usuario_contrasena.setObjectName(u"entry_usuario_contrasena")

        self.gridLayout.addWidget(self.entry_usuario_contrasena, 1, 4, 1, 1)

        self.entry_usuario_rol = QLineEdit(self.widget)
        self.entry_usuario_rol.setObjectName(u"entry_usuario_rol")

        self.gridLayout.addWidget(self.entry_usuario_rol, 1, 5, 1, 2)

        self.apellido_usuarios_label = QLabel(self.widget)
        self.apellido_usuarios_label.setObjectName(u"apellido_usuarios_label")
        self.apellido_usuarios_label.setEnabled(True)

        self.gridLayout.addWidget(self.apellido_usuarios_label, 0, 2, 1, 1)

        self.contarsena_usuario_label = QLabel(self.widget)
        self.contarsena_usuario_label.setObjectName(u"contarsena_usuario_label")
        self.contarsena_usuario_label.setEnabled(True)

        self.gridLayout.addWidget(self.contarsena_usuario_label, 0, 4, 1, 1)

        self.rol_usuario_label = QLabel(self.widget)
        self.rol_usuario_label.setObjectName(u"rol_usuario_label")
        self.rol_usuario_label.setEnabled(True)

        self.gridLayout.addWidget(self.rol_usuario_label, 0, 5, 1, 2)

        self.widget1 = QWidget(self.centralwidget)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(11, 320, 531, 26))
        self.gridLayout_2 = QGridLayout(self.widget1)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.boton_agregar_usuario = QPushButton(self.widget1)
        self.boton_agregar_usuario.setObjectName(u"boton_agregar_usuario")

        self.gridLayout_2.addWidget(self.boton_agregar_usuario, 0, 0, 1, 1)

        self.boton_editar_usuario = QPushButton(self.widget1)
        self.boton_editar_usuario.setObjectName(u"boton_editar_usuario")

        self.gridLayout_2.addWidget(self.boton_editar_usuario, 0, 1, 1, 1)

        self.boton_eliminar_usuario = QPushButton(self.widget1)
        self.boton_eliminar_usuario.setObjectName(u"boton_eliminar_usuario")

        self.gridLayout_2.addWidget(self.boton_eliminar_usuario, 0, 2, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Manejo de Usuarios", None))
        self.nombre_usuario_label.setText(QCoreApplication.translate("MainWindow", u"Nombre:", None))
        self.usuario_usuario_label.setText(QCoreApplication.translate("MainWindow", u"Usuario:", None))
        self.apellido_usuarios_label.setText(QCoreApplication.translate("MainWindow", u"Apellido:", None))
        self.contarsena_usuario_label.setText(QCoreApplication.translate("MainWindow", u"Contrase\u00f1a:", None))
        self.rol_usuario_label.setText(QCoreApplication.translate("MainWindow", u"Rol:", None))
        self.boton_agregar_usuario.setText(QCoreApplication.translate("MainWindow", u"Agregar Usuario", None))
        self.boton_editar_usuario.setText(QCoreApplication.translate("MainWindow", u"Editar Usuario", None))
        self.boton_eliminar_usuario.setText(QCoreApplication.translate("MainWindow", u"Eliminar Usuario", None))
    # retranslateUi

