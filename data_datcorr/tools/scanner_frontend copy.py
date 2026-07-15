from pathlib import Path
import re

RAIZ = Path(".")

PATRONES = [
    r"obtener_usuario_actual(",
    
]

IGNORAR = {
    "venv",
    ".git",
    "__pycache__",
    "src_old",
}

for archivo in RAIZ.rglob("*.py"):

    if any(x in archivo.parts for x in IGNORAR):
        continue

    try:
        texto = archivo.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except Exception:
        continue

    lineas = texto.splitlines()

    for nro, linea in enumerate(lineas, start=1):

        for patron in PATRONES:

            if re.search(patron, linea):

                print(
                    f"{archivo}:{nro}"
                )
                print(
                    f"    {linea.strip()}"
                )
                print()