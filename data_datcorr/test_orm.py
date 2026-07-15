from database.session import SessionLocal
from database.modelos import PruebaUsuario

# -----------------------------------
# CREAR SESIÓN
# -----------------------------------

session = SessionLocal()

try:

    usuarios = session.query(
        PruebaUsuario
    ).all()

    print("\nUSUARIOS:\n")

    for usuario in usuarios:

        print(
            usuario.id,
            usuario.nombre,
            usuario.usuario
        )

finally:

    session.close()