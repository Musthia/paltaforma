from services.auth_service import (
    autenticar_usuario
)

# -----------------------------------
# LOGIN TEST
# -----------------------------------

resultado = autenticar_usuario(
    "fabio",
    "1234"
)

print("\nRESULTADO LOGIN\n")

print(resultado)

# -----------------------------------
# MOSTRAR DATOS
# -----------------------------------

if resultado["success"]:

    usuario = resultado["usuario"]

    print("\nUSUARIO AUTENTICADO\n")

    print(usuario.nombre)
    print(usuario.rol)
    print(usuario.nivel_seguridad)