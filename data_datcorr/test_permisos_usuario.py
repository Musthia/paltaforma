from services.usuarios_permisos_service import (

    asignar_permiso_usuario,

    usuario_tiene_permiso,

    quitar_permiso_usuario,

    listar_permisos_usuario

)

# -----------------------------------
# USUARIO TEST
# -----------------------------------

USUARIO_ID = 1

# -----------------------------------
# ASIGNAR PERMISOS
# -----------------------------------

print("\nASIGNANDO PERMISOS\n")

resultado = asignar_permiso_usuario(
    USUARIO_ID,
    "CONSULTAR"
)

print(resultado)

resultado = asignar_permiso_usuario(
    USUARIO_ID,
    "EDITAR"
)

print(resultado)

# -----------------------------------
# VALIDAR PERMISOS
# -----------------------------------

print("\nVALIDANDO PERMISOS\n")

print(
    "CONSULTAR:",
    usuario_tiene_permiso(
        USUARIO_ID,
        "CONSULTAR"
    )
)

print(
    "EDITAR:",
    usuario_tiene_permiso(
        USUARIO_ID,
        "EDITAR"
    )
)

print(
    "ELIMINAR:",
    usuario_tiene_permiso(
        USUARIO_ID,
        "ELIMINAR"
    )
)

# -----------------------------------
# QUITAR PERMISO
# -----------------------------------

print("\nQUITANDO PERMISO EDITAR\n")

resultado = quitar_permiso_usuario(
    USUARIO_ID,
    "EDITAR"
)

print(resultado)

# -----------------------------------
# REVALIDAR
# -----------------------------------

print("\nVALIDANDO NUEVAMENTE\n")

print(
    "EDITAR:",
    usuario_tiene_permiso(
        USUARIO_ID,
        "EDITAR"
    )
)

# -----------------------------------
# LISTAR PERMISOS
# -----------------------------------

print("\nLISTA PERMISOS USUARIO\n")

permisos = listar_permisos_usuario(
    USUARIO_ID
)

for permiso in permisos:

    print(
        f"✔ {permiso}"
    )

print("\nASIGNANDO ADMIN_USUARIOS\n")

resultado = asignar_permiso_usuario(
    usuario_id=1,
    codigo_permiso="ADMIN_USUARIOS"
)

print(resultado)    