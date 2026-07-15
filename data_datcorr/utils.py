# utils.py
import sys
import os

def obtener_ruta_bases():
    """
    Para bases de datos EXTERNAS (bases_g al lado del exe)
    """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, "bases_g")

def obtener_ruta_db(base):
    """
    Devuelve la ruta absoluta a la base seleccionada
    """
    return os.path.join(obtener_ruta_bases(), f"{base}.db")