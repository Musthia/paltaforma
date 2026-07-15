from backend.services.usuarios_service import (
    listar_usuarios_web
)

usuarios = listar_usuarios_web()

print("\nUSUARIOS WEB\n")

for usuario in usuarios:

    print(
        usuario.id,
        usuario.usuario,
        usuario.rol
    )