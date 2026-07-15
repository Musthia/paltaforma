from services.auth_service import (
    autenticar_usuario
)

from services.permisos_service import (
    MODULO_USUARIOS,
    MODULO_REPORTES,
    tiene_permiso,
    obtener_descripcion_nivel
)

# -----------------------------------
# LOGIN
# -----------------------------------

resultado = autenticar_usuario(
    "fabio",
    "1234"
)

# -----------------------------------
# VALIDAR LOGIN
# -----------------------------------

if resultado["success"]:

    usuario = resultado["usuario"]

    print("\nUSUARIO AUTENTICADO\n")

    print(usuario.nombre)

    print(
        obtener_descripcion_nivel(
            usuario.nivel_seguridad
        )
    )

    # -----------------------------------
    # VALIDAR PERMISOS
    # -----------------------------------

    print("\nPERMISOS\n")

    print(
        "Usuarios:",
        tiene_permiso(
            usuario,
            MODULO_USUARIOS
        )
    )

    print(
        "Reportes:",
        tiene_permiso(
            usuario,
            MODULO_REPORTES
        )
    )