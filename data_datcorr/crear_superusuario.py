from database.conexion import SessionLocal

from database.modelos import Usuario

from utils.hash import hash_password

# -----------------------------------
# SESION
# -----------------------------------

session = SessionLocal()

try:

    # -----------------------------------
    # VERIFICAR EXISTENCIA
    # -----------------------------------

    existe = (
        session.query(Usuario)
        .filter(
            Usuario.es_superusuario == True
        )
        .first()
    )

    if existe:

        print(
            "Ya existe un superusuario."
        )

    else:

        nuevo = Usuario(

            nombre="Sistema",

            apellido="Master",

            usuario="Musthia",

            password_hash=hash_password(
                "0611"
            ),

            rol="SUPERADMIN",

            nivel_seguridad=999,

            activo=True,

            es_superusuario=True
        )

        session.add(nuevo)

        session.commit()

        print(
            "SUPERUSUARIO CREADO"
        )

finally:

    session.close()