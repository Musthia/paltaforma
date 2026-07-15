from services.usuario_service import (
    obtener_usuario_por_id
)

usuario = obtener_usuario_por_id(1)

print("\nUSUARIO\n")

if usuario:

    print(usuario.id)
    print(usuario.nombre)
    print(usuario.apellido)
    print(usuario.usuario)
    print(usuario.rol)
    print(usuario.nivel_seguridad)
    print(usuario.activo)

else:

    print("Usuario no encontrado.")