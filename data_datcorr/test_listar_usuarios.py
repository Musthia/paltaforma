from services.usuario_service import (
    listar_usuarios
)

print("\nLISTA USUARIOS\n")

usuarios = listar_usuarios()

for usuario in usuarios:

    print(
        usuario.id,
        usuario.nombre,
        usuario.apellido,
        usuario.usuario,
        usuario.rol,
        usuario.nivel_seguridad,
        usuario.activo
    )