from pathlib import Path
import re

CARPETAS = [
Path("ventanas"),
Path("core"),
Path("services"),
]

PATRONES = [

# atributos usuario
r"\.nombre\b",
r"\.apellido\b",
r"\.rol\b",
r"\.nivel_seguridad\b",
r"\.es_superusuario\b",
r"\.activo\b",
r"\.usuario\b",
r"\.id\b",

# acceso directo a objetos
r"usuario\.",
r"usuario_actual\.",
r"usuario_db\.",
r"self\.usuario\.",


]

for carpeta in CARPETAS:


    if not carpeta.exists():
        continue
    
    for archivo in carpeta.rglob("*.py"):
    
        try:
            texto = archivo.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        except Exception:
            continue
        
        lineas = texto.splitlines()
    
        for nro, linea in enumerate(
            lineas,
            start=1
        ):
    
            for patron in PATRONES:
            
                if re.search(
                    patron,
                    linea
                ):
    
                    print(
                        f"{archivo}:{nro}"
                    )
    
                    print(
                        f"    {linea.strip()}"
                    )
    
                    print()