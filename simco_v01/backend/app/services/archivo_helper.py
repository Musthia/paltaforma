import os
import shutil
import uuid

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def guardar_archivo(archivo) -> tuple[str, str] | None:
    if not archivo or not archivo.filename:
        return None

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(archivo.filename)[1]
    nombre_unico = f"{uuid.uuid4().hex}{ext}"
    ruta = os.path.join(UPLOAD_DIR, nombre_unico)

    with open(ruta, "wb") as f:
        shutil.copyfileobj(archivo.file, f)

    return archivo.filename, nombre_unico
