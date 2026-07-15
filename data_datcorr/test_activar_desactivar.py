from services.usuario_service import (
    activar_usuario,
    desactivar_usuario,
    obtener_usuario_por_id
)

# -----------------------------------
# USUARIO TEST
# -----------------------------------

USUARIO_ID = 1

# -----------------------------------
# DESACTIVAR
# -----------------------------------

print("\nDESACTIVANDO USUARIO\n")

resultado = desactivar_usuario(
    USUARIO_ID
)

print(resultado)

# -----------------------------------
# VALIDAR ESTADO
# -----------------------------------

usuario = obtener_usuario_por_id(
    USUARIO_ID
)

print(
    "ACTIVO:",
    usuario.activo
)

# -----------------------------------
# ACTIVAR
# -----------------------------------

print("\nACTIVANDO USUARIO\n")

resultado = activar_usuario(
    USUARIO_ID
)

print(resultado)

# -----------------------------------
# VALIDAR NUEVAMENTE
# -----------------------------------

usuario = obtener_usuario_por_id(
    USUARIO_ID
)

print(
    "ACTIVO:",
    usuario.activo
)