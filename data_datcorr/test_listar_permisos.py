from services.permisos_service import (
    listar_permisos
)

print(
    "\nLISTA PERMISOS\n"
)

permisos = listar_permisos()

for permiso in permisos:

    print(
        permiso.id,
        permiso.codigo
    )