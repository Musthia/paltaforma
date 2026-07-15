from database.crud.crud_usuarios import (
    buscar_usuario,
    verificar_password
)

# -----------------------------------
# AUTENTICAR USUARIO
# -----------------------------------

def autenticar_usuario(
    usuario_input,
    password_input
):

    # -----------------------------------
    # BUSCAR USUARIO
    # -----------------------------------

    usuario = buscar_usuario(
        usuario_input
    )

    # -----------------------------------
    # NO EXISTE
    # -----------------------------------

    if not usuario:

        return {
            "success": False,
            "mensaje": "Usuario no existe."
        }

    # -----------------------------------
    # USUARIO INACTIVO
    # -----------------------------------

    if not usuario.activo:

        return {
            "success": False,
            "mensaje": "Usuario inactivo."
        }

    # -----------------------------------
    # VALIDAR PASSWORD
    # -----------------------------------

    password_ok = verificar_password(
        password_input,
        usuario.password_hash
    )

    if not password_ok:

        return {
            "success": False,
            "mensaje": "Password incorrecta."
        }

    # -----------------------------------
    # LOGIN EXITOSO
    # -----------------------------------

    return {
        "success": True,
        "mensaje": "Login correcto.",
        "usuario": usuario
    }