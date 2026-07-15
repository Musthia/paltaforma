def style_combobox_dark():
    return """
    QComboBox {
        background-color: #567bf3;
        
        
        color: #f0f0f0;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 6px;
        padding-right: 28px; /* espacio para flecha nativa */
    }

    QComboBox:hover {
        border: 1px solid #777;
    }

    QComboBox:focus {
        border: 1px solid #3daee9;
        
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 26px;
        border-left: 1px solid #555;
        background-color: #2b2b2b;
        
        
    }

    QComboBox QAbstractItemView {
        background-color: #000000;
        color: #fbfdfd;
        selection-color: #6fcc7e;
        outline: 0;
    }
    """

def style_pushbutton_dark():
    return """ 
    QPushButton {
    background-color: #455a50;
    color: #ecf0f1;
    border: 1px solid #1a252f;
 
    padding: 6px 12px;
    font-weight: bold;
    font-size: 11px;
    }
    QPushButton:hover {
        background-color: #546e7a;     /* tono más claro al pasar el mouse */
    }
    QPushButton:pressed {
        background-color: #2e4053;     /* más oscuro al presionar */
        border: 2px solid #1a252f;
    }
    QPushButton:disabled {
        background-color: #a7b0b5;
        color: #dfe4e8;
        border: 1px solid #95a5a6;
    } 
    """

def style_dialog_dark():
    return """
    QDialog {
        background-color: #1e1e1e;
    }

    QLabel {
        color: #e0e0e0;
        font-size: 13px;
        background-color: #1e1e1e;
    }

    QLineEdit {
        background-color: #2b2b2b;
        color: #f0f0f0;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 6px;
        selection-background-color: #3daee9;
    }

    QLineEdit:focus {
        border: 1px solid #3daee9;
        background-color: #303030;
    }

    QLineEdit:hover {
        border: 1px solid #777;
    }

    QPushButton {
        background-color: #3a3a3a;
        color: #ffffff;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 8px 14px;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #444;
        border-color: #777;
    }

    QPushButton:pressed {
        background-color: #2f2f2f;
        border-color: #3daee9;
    }
    """

def style_messagebox_dark():
    return """
    QMessageBox {
        background-color: #ffffff;
        color: #ffffff;
        font-size: 13px;
    }

    QMessageBox QLabel {
        color: #110101;
    }

    QMessageBox QPushButton {
        background-color: #3a3a3a;
        color: #ffffff;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 6px 14px;
        min-width: 80px;
    }

    QMessageBox QPushButton:hover {
        background-color: #444;
        border-color: #777;
    }

    QMessageBox QPushButton:pressed {
        background-color: #2f2f2f;
        border-color: #3daee9;
    }
    """

def style_lineedit_error():
    return """
    QLineEdit {
        border: 2px solid #d9534f;
        background-color: #2b2b2b;
        color: #ffffff;
    }
    """

def style_lineedit_validation():
    return """
    QLineEdit[error="true"] {
        border: 1px solid #e53935;
        background-color: #3b1f1f;
        color: #ffffff;
    }
    """
    