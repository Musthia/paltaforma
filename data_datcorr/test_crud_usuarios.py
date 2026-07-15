from database.crud.crud_usuarios import (
    crear_usuario,
    listar_usuarios,
    buscar_usuario,
    verificar_password
)

# -----------------------------------
# CREAR USUARIO
# -----------------------------------

crear_usuario(
    nombre="Fabio",
    apellido="Eduardo",
    usuario="fabio",
    password="1234",
    rol="Administrador",
    nivel_seguridad=10
)

# -----------------------------------
# LISTAR
# -----------------------------------

listar_usuarios()

# -----------------------------------
# BUSCAR
# -----------------------------------

usuario = buscar_usuario("fabio")

if usuario:

    print("\nUSUARIO ENCONTRADO\n")

    print(usuario.nombre)
    print(usuario.usuario)

    # -----------------------------------
    # VERIFICAR PASSWORD
    # -----------------------------------

    password_ok = verificar_password(
        "1234",
        usuario.password_hash
    )

    print("\nPASSWORD CORRECTA:")
    print(password_ok)