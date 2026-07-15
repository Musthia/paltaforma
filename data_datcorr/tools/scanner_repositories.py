from pathlib import Path
import re

RAIZ = Path(".")

PATRONES_CLAVE = [
    r"class\s+\w+Repository\s*\(",   # clases repo
    r"SessionLocal",                 # acceso directo a DB
    r"db\.query",
    r"session\.query",
    r"\.close\(\)"                   # lifecycle inconsistente
]

IGNORAR = {
    "venv",
    ".git",
    "__pycache__",
}

CARPETAS_OBJETIVO = {
    "repositories",
    "services",
    "database",
}

for archivo in RAIZ.rglob("*.py"):

    if not any(folder in str(archivo) for folder in CARPETAS_OBJETIVO):
        continue

    if any(x in archivo.parts for x in IGNORAR):
        continue

    try:
        texto = archivo.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    for i, linea in enumerate(texto.splitlines(), 1):

        for patron in PATRONES_CLAVE:

            if re.search(patron, linea):

                print(f"{archivo}:{i}")
                print(f"    {linea.strip()}")
                print()