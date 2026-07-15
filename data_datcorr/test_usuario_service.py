from services.usuario_service import (
    actualizar_usuario,
    cambiar_password,
    cambiar_estado_usuario
)

from services.auth_service import (
    autenticar_usuario
)

from database.crud.crud_usuarios import (
    buscar_usuario
)

# -----------------------------------
# BUSCAR USUARIO
# -----------------------------------

usuario = buscar_usuario("fabio")

if not usuario:

    print("\nUsuario no encontrado.\n")

    exit()

print("\nUSUARIO ORIGINAL\n")

print(usuario.nombre)
print(usuario.apellido)
print(usuario.rol)
print(usuario.nivel_seguridad)
print(usuario.activo)

# -----------------------------------
# ACTUALIZAR USUARIO
# -----------------------------------

resultado_update = actualizar_usuario(
    usuario_id=usuario.id,
    nombre="Fabio Actualizado",
    apellido="Developer",
    rol="Supervisor",
    nivel_seguridad=5
)

print("\nUPDATE\n")

print(resultado_update)

# -----------------------------------
# CAMBIAR PASSWORD
# -----------------------------------

resultado_password = cambiar_password(
    usuario.id,
    "5678"
)

print("\nCAMBIO PASSWORD\n")

print(resultado_password)

# -----------------------------------
# DESACTIVAR USUARIO
# -----------------------------------

resultado_desactivar = cambiar_estado_usuario(
    usuario.id,
    False
)

print("\nDESACTIVAR\n")

print(resultado_desactivar)

# -----------------------------------
# PROBAR LOGIN DESACTIVADO
# -----------------------------------

resultado_login = autenticar_usuario(
    "fabio",
    "5678"
)

print("\nLOGIN USUARIO DESACTIVADO\n")

print(resultado_login)

# -----------------------------------
# REACTIVAR USUARIO
# -----------------------------------

resultado_activar = cambiar_estado_usuario(
    usuario.id,
    True
)

print("\nREACTIVAR\n")

print(resultado_activar)

# -----------------------------------
# LOGIN FINAL
# -----------------------------------

resultado_login_final = autenticar_usuario(
    "fabio",
    "5678"
)

print("\nLOGIN FINAL\n")

print(resultado_login_final)

# -----------------------------------
# DATOS FINALES
# -----------------------------------

usuario_actualizado = buscar_usuario(
    "fabio"
)

print("\nUSUARIO FINAL\n")

print(usuario_actualizado.nombre)
print(usuario_actualizado.apellido)
print(usuario_actualizado.rol)
print(usuario_actualizado.nivel_seguridad)
print(usuario_actualizado.activo)