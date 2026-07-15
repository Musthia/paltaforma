from services.usuarios_permisos_service import (
    obtener_permisos_usuario
)

print("\nPERMISOS USUARIO\n")

permisos = obtener_permisos_usuario(1)

for permiso in permisos:

    print(
        permiso.id,
        permiso.codigo
    )