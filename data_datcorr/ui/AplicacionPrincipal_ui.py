# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AplicacionPrincipal.ui'
##
## Created by: Qt User Interface Compiler version 6.10.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QTabWidget, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1037, 750)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setSizeIncrement(QSize(1, 1))
        MainWindow.setBaseSize(QSize(0, 0))
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        brush1 = QBrush(QColor(226, 255, 244, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, brush)
        MainWindow.setPalette(palette)
        icon = QIcon()
        icon.addFile(u"../../Users/archivodatcorrsa/.designer/img/Escudo.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(99.000000000000000)
        MainWindow.setStyleSheet(u"\n"
"background-color: rgb(226, 255, 244);")
        self.menu_ayuda = QAction(MainWindow)
        self.menu_ayuda.setObjectName(u"menu_ayuda")
        icon1 = QIcon()
        icon1.addFile(u"../../Users/archivodatcorrsa/visor_viernes/img/whastapp.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.menu_ayuda.setIcon(icon1)
        self.actionManejo_de_Usuarios = QAction(MainWindow)
        self.actionManejo_de_Usuarios.setObjectName(u"actionManejo_de_Usuarios")
        self.actionSalir = QAction(MainWindow)
        self.actionSalir.setObjectName(u"actionSalir")
        self.actionSalir.setCheckable(True)
        self.actionVersion_1_0 = QAction(MainWindow)
        self.actionVersion_1_0.setObjectName(u"actionVersion_1_0")
        self.actionImagenes = QAction(MainWindow)
        self.actionImagenes.setObjectName(u"actionImagenes")
        self.actionBase_De_Datos = QAction(MainWindow)
        self.actionBase_De_Datos.setObjectName(u"actionBase_De_Datos")
        self.actionDatcorr = QAction(MainWindow)
        self.actionDatcorr.setObjectName(u"actionDatcorr")
        self.actionDatcorr_2 = QAction(MainWindow)
        self.actionDatcorr_2.setObjectName(u"actionDatcorr_2")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        palette1 = QPalette()
        brush2 = QBrush(QColor(0, 0, 0, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush2)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush2)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        self.centralwidget.setPalette(palette1)
        font = QFont()
        font.setBold(True)
        self.centralwidget.setFont(font)
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setSpacing(2)
        self.gridLayout_2.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.mi_data_cons = QLabel(self.centralwidget)
        self.mi_data_cons.setObjectName(u"mi_data_cons")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.mi_data_cons.sizePolicy().hasHeightForWidth())
        self.mi_data_cons.setSizePolicy(sizePolicy1)
        self.mi_data_cons.setMaximumSize(QSize(303, 15))
        palette2 = QPalette()
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush2)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush1)
        palette2.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush2)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush1)
        palette2.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush2)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette2.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        self.mi_data_cons.setPalette(palette2)
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(False)
        self.mi_data_cons.setFont(font1)
        self.mi_data_cons.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.mi_data_cons.setStyleSheet(u"QLabel[subtitulo=\"true\"] {\n"
"background-color: transparent;\n"
"  \n"
"    border-bottom: 1px solid #b0bec5;\n"
"    padding-bottom: 2px;\n"
"}\n"
"")
        self.mi_data_cons.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.mi_data_cons, 7, 1, 1, 1)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setMinimumSize(QSize(2, 0))
        self.line.setMidLineWidth(11)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line, 0, 0, 1, 7)

        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setSpacing(2)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.tabwidget_resultados_consulta = QTabWidget(self.centralwidget)
        self.tabwidget_resultados_consulta.setObjectName(u"tabwidget_resultados_consulta")
        sizePolicy1.setHeightForWidth(self.tabwidget_resultados_consulta.sizePolicy().hasHeightForWidth())
        self.tabwidget_resultados_consulta.setSizePolicy(sizePolicy1)
        self.tabwidget_resultados_consulta.setMaximumSize(QSize(16777215, 16777215))
        font2 = QFont()
        font2.setFamilies([u"Tahoma"])
        font2.setPointSize(11)
        font2.setBold(True)
        self.tabwidget_resultados_consulta.setFont(font2)
        self.tabwidget_resultados_consulta.setStyleSheet(u"QTabBar::tab {\n"
"    background-color:#dfe6cf;\n"
"    color: black;\n"
"    font-weight: bold;\n"
"    padding: 9px 14px;\n"
"    margin-top: 2px;\n"
"    border-top-left-radius: 38px;\n"
"    border-top-right-radius: 38px;\n"
"    border: 2px solid #1a252f;\n"
"    border-bottom: none;\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    background-color:#605b78;\n"
"    color: white;\n"
"    margin-top: 0px;\n"
"    border-bottom: 2px solid #34495e;\n"
"}\n"
"background-color: rgb(182, 182, 182);\n"
"")
        self.tabwidget_resultados_consulta.setTabPosition(QTabWidget.TabPosition.North)
        self.tabwidget_resultados_consulta.setTabShape(QTabWidget.TabShape.Triangular)
        self.tabwidget_resultados_consulta.setElideMode(Qt.TextElideMode.ElideLeft)
        self.tabwidget_resultados_consulta.setUsesScrollButtons(False)
        self.tabwidget_resultados_consulta.setDocumentMode(True)
        self.tabwidget_resultados_consulta.setMovable(False)
        self.tabwidget_resultados_consulta.setTabBarAutoHide(False)

        self.gridLayout_8.addWidget(self.tabwidget_resultados_consulta, 0, 0, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout_8, 12, 0, 1, 7)

        self.entry_consultar = QLineEdit(self.centralwidget)
        self.entry_consultar.setObjectName(u"entry_consultar")
        sizePolicy.setHeightForWidth(self.entry_consultar.sizePolicy().hasHeightForWidth())
        self.entry_consultar.setSizePolicy(sizePolicy)
        palette3 = QPalette()
        brush3 = QBrush(QColor(26, 37, 47, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush3)
        brush4 = QBrush(QColor(207, 216, 220, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush4)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush3)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush3)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush4)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush4)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush)
        brush5 = QBrush(QColor(26, 37, 47, 128))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush5)
#endif
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush3)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush4)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush3)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush3)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush4)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush4)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush5)
#endif
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush3)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush4)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush3)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush3)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush4)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush4)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette3.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush5)
#endif
        self.entry_consultar.setPalette(palette3)
        font3 = QFont()
        font3.setFamilies([u"Calibri"])
        font3.setPointSize(15)
        font3.setWeight(QFont.Black)
        font3.setItalic(False)
        self.entry_consultar.setFont(font3)
        self.entry_consultar.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.entry_consultar.setAcceptDrops(False)
        self.entry_consultar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.entry_consultar.setAutoFillBackground(False)
        self.entry_consultar.setStyleSheet(u"QLineEdit {\n"
"    background-color: #cfd8dc;\n"
"    border: 1px solid #455a64;\n"
"\n"
"\n"
"    color: #1a252f;\n"
"\n"
"    /* relieve simulado */\n"
"    border-top-color: #a7b1b7;   /* borde superior m\u00e1s claro */\n"
"    border-left-color: #a7b1b7;  /* borde izquierdo m\u00e1s claro */\n"
"    border-right-color: #2e3d45; /* borde derecho m\u00e1s oscuro */\n"
"    border-bottom-color: #2e3d45;\n"
"}\n"
"\n"
"QLineEdit:focus {\n"
"    background-color: #b0bec5;\n"
"    border: 2px solid #2e4053;\n"
"    color: #0f1419;\n"
"    outline: none;\n"
"}")
        self.entry_consultar.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.entry_consultar.setMaxLength(32768)
        self.entry_consultar.setFrame(True)
        self.entry_consultar.setEchoMode(QLineEdit.EchoMode.Normal)
        self.entry_consultar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entry_consultar.setDragEnabled(True)
        self.entry_consultar.setCursorMoveStyle(Qt.CursorMoveStyle.VisualMoveStyle)

        self.gridLayout_2.addWidget(self.entry_consultar, 7, 2, 1, 1)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setStyleSheet(u"background-color: rgb(255, 170, 127);")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy2)
        self.line_2.setMinimumSize(QSize(0, 10))
        self.line_2.setLineWidth(100)
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_2, 1, 0, 1, 1)

        self.pushButton_consulta_bases = QPushButton(self.frame)
        self.pushButton_consulta_bases.setObjectName(u"pushButton_consulta_bases")
        self.pushButton_consulta_bases.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_consulta_bases.setStyleSheet(u"QPushButton {\n"
"    background-color:#9b759e;\n"
"    color: #ecf0f1;\n"
"    border: 1px solid #1a252f;\n"
" \n"
"    padding: 6px 12px;\n"
"    font-weight: bold;\n"
"    font-size: 11px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #948d76;     /* tono m\u00e1s claro al pasar el mouse */\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #bab9b5;     /* m\u00e1s oscuro al presionar */\n"
"    border: 2px solid #1a252f;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #a7b0b5;\n"
"    color: #dfe4e8;\n"
"    border: 1px solid #95a5a6;\n"
"}")

        self.gridLayout.addWidget(self.pushButton_consulta_bases, 0, 0, 1, 1)

        self.pushButton_carga_datos = QPushButton(self.frame)
        self.pushButton_carga_datos.setObjectName(u"pushButton_carga_datos")
        self.pushButton_carga_datos.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_carga_datos.setStyleSheet(u"QPushButton {\n"
"    background-color: #455a50;\n"
"    color: #ecf0f1;\n"
"    border: 1px solid #1a252f;\n"
" \n"
"    padding: 6px 12px;\n"
"    font-weight: bold;\n"
"    font-size: 11px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #546e7a;     /* tono m\u00e1s claro al pasar el mouse */\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #2e4053;     /* m\u00e1s oscuro al presionar */\n"
"    border: 2px solid #1a252f;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #a7b0b5;\n"
"    color: #dfe4e8;\n"
"    border: 1px solid #95a5a6;\n"
"}")

        self.gridLayout.addWidget(self.pushButton_carga_datos, 2, 0, 1, 1)

        self.boton_cerrar_sesion = QPushButton(self.frame)
        self.boton_cerrar_sesion.setObjectName(u"boton_cerrar_sesion")
        self.boton_cerrar_sesion.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.boton_cerrar_sesion.setStyleSheet(u"QPushButton {\n"
"    background-color: #455a50;\n"
"    color: #ecf0f1;\n"
"    border: 1px solid #1a252f;\n"
" \n"
"    padding: 6px 12px;\n"
"    font-weight: bold;\n"
"    font-size: 11px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #546e7a;     /* tono m\u00e1s claro al pasar el mouse */\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #2e4053;     /* m\u00e1s oscuro al presionar */\n"
"    border: 2px solid #1a252f;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #a7b0b5;\n"
"    color: #dfe4e8;\n"
"    border: 1px solid #95a5a6;\n"
"}")

        self.gridLayout.addWidget(self.boton_cerrar_sesion, 0, 1, 1, 1)

        self.line_4 = QFrame(self.frame)
        self.line_4.setObjectName(u"line_4")
        sizePolicy2.setHeightForWidth(self.line_4.sizePolicy().hasHeightForWidth())
        self.line_4.setSizePolicy(sizePolicy2)
        self.line_4.setMinimumSize(QSize(0, 10))
        self.line_4.setLineWidth(100)
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_4, 1, 1, 1, 1)

        self.boton_adm_usuar = QPushButton(self.frame)
        self.boton_adm_usuar.setObjectName(u"boton_adm_usuar")
        self.boton_adm_usuar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.boton_adm_usuar.setStyleSheet(u"QPushButton {\n"
"    background-color: #455a50;\n"
"    color: #ecf0f1;\n"
"    border: 1px solid #1a252f;\n"
" \n"
"    padding: 6px 12px;\n"
"    font-weight: bold;\n"
"    font-size: 11px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #546e7a;     /* tono m\u00e1s claro al pasar el mouse */\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #2e4053;     /* m\u00e1s oscuro al presionar */\n"
"    border: 2px solid #1a252f;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #a7b0b5;\n"
"    color: #dfe4e8;\n"
"    border: 1px solid #95a5a6;\n"
"}")

        self.gridLayout.addWidget(self.boton_adm_usuar, 2, 1, 1, 1)


        self.gridLayout_2.addWidget(self.frame, 7, 5, 2, 1)

        self.combo_bases = QComboBox(self.centralwidget)
        self.combo_bases.setObjectName(u"combo_bases")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.combo_bases.sizePolicy().hasHeightForWidth())
        self.combo_bases.setSizePolicy(sizePolicy3)
        palette4 = QPalette()
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush1)
        palette4.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush1)
        palette4.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette4.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        self.combo_bases.setPalette(palette4)
        self.combo_bases.setStyleSheet(u"")
        self.combo_bases.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.combo_bases.setMinimumContentsLength(0)

        self.gridLayout_2.addWidget(self.combo_bases, 7, 0, 1, 1)

        self.line_3 = QFrame(self.centralwidget)
        self.line_3.setObjectName(u"line_3")
        sizePolicy2.setHeightForWidth(self.line_3.sizePolicy().hasHeightForWidth())
        self.line_3.setSizePolicy(sizePolicy2)
        self.line_3.setMinimumSize(QSize(0, 10))
        self.line_3.setLineWidth(100)
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_3, 8, 0, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabwidget_resultados_consulta.setCurrentIndex(-1)
        self.combo_bases.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Base de Datos", None))
        self.menu_ayuda.setText(QCoreApplication.translate("MainWindow", u"Datcorr", None))
        self.actionManejo_de_Usuarios.setText(QCoreApplication.translate("MainWindow", u"Manejo de Usuarios", None))
        self.actionSalir.setText(QCoreApplication.translate("MainWindow", u"Salir", None))
        self.actionVersion_1_0.setText(QCoreApplication.translate("MainWindow", u"Version: 1.0", None))
        self.actionImagenes.setText(QCoreApplication.translate("MainWindow", u"Imagenes", None))
        self.actionBase_De_Datos.setText(QCoreApplication.translate("MainWindow", u"Base De Datos", None))
        self.actionDatcorr.setText(QCoreApplication.translate("MainWindow", u"Datcorr", None))
        self.actionDatcorr_2.setText(QCoreApplication.translate("MainWindow", u"Datcorr", None))
        self.mi_data_cons.setText(QCoreApplication.translate("MainWindow", u"Dato de Consulta", None))
#if QT_CONFIG(tooltip)
        self.entry_consultar.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-weight:700;\">DATO DE CONSULTA</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.entry_consultar.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_consulta_bases.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-weight:700;\">BASE DE<br/>DATOS<br/>DATCORR</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_consulta_bases.setText(QCoreApplication.translate("MainWindow", u"Base de Datos", None))
#if QT_CONFIG(tooltip)
        self.pushButton_carga_datos.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">INICIAR SESION <br/>DE <br/>CARGA DE DATOS</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_carga_datos.setText(QCoreApplication.translate("MainWindow", u"Carga de \n"
"Datos", None))
#if QT_CONFIG(tooltip)
        self.boton_cerrar_sesion.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">CERRAR SESION</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.boton_cerrar_sesion.setText(QCoreApplication.translate("MainWindow", u"CERRAR SESION", None))
#if QT_CONFIG(tooltip)
        self.boton_adm_usuar.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">MANEJO<br/>DE<br/>USUARIOS</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.boton_adm_usuar.setText(QCoreApplication.translate("MainWindow", u"Administraci\u00f3n \n"
"Usuarios", None))
#if QT_CONFIG(tooltip)
        self.combo_bases.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-weight:700;\">SELECCIONAR BASE <br/>DE DATOS</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.combo_bases.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Seleccione una Base", None))
    # retranslateUi

