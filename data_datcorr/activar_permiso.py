from services.usuarios_permisos_service import (
    asignar_permiso_usuario
)

resultado = asignar_permiso_usuario(
    1,
    "EDITAR"
)

print(resultado)