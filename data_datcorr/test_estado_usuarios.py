from services.usuario_service import (
    listar_usuarios_activos,
    listar_usuarios_inactivos
)

# -----------------------------------
# ACTIVOS
# -----------------------------------

print("\nUSUARIOS ACTIVOS\n")

usuarios_activos = (
    listar_usuarios_activos()
)

for usuario in usuarios_activos:

    print(
        usuario.id,
        usuario.nombre,
        usuario.usuario,
        usuario.activo
    )

# -----------------------------------
# INACTIVOS
# -----------------------------------

print("\nUSUARIOS INACTIVOS\n")

usuarios_inactivos = (
    listar_usuarios_inactivos()
)

for usuario in usuarios_inactivos:

    print(
        usuario.id,
        usuario.nombre,
        usuario.usuario,
        usuario.activo
    )