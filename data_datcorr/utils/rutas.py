import sys
import os

def obtener_ruta_bases():

    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, "bases_g")

def obtener_ruta_db(base):

    return os.path.join(
        obtener_ruta_bases(),
        f"{base}.db"
    )