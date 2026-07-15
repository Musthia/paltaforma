import bcrypt

from database.session import SessionLocal
from database.modelos import Usuario

# -----------------------------------
# CREAR HASH PASSWORD
# -----------------------------------

def generar_hash_password(password: str) -> str:

    password_bytes = password.encode("utf-8")

    hash_bytes = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hash_bytes.decode("utf-8")


# -----------------------------------
# VERIFICAR PASSWORD
# -----------------------------------

def verificar_password(
    password: str,
    password_hash: str
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


# -----------------------------------
# CREAR USUARIO
# -----------------------------------

def crear_usuario(
    nombre,
    apellido,
    usuario,
    password,
    rol,
    nivel_seguridad=1
):

    session = SessionLocal()

    try:

        # -----------------------------------
        # VERIFICAR SI EXISTE
        # -----------------------------------

        usuario_existente = session.query(
            Usuario
        ).filter(
            Usuario.usuario == usuario
        ).first()

        if usuario_existente:

            print(
                f"\nERROR: el usuario "
                f"'{usuario}' ya existe.\n"
            )

            return

        # -----------------------------------
        # HASH PASSWORD
        # -----------------------------------

        password_hash = generar_hash_password(
            password
        )

        # -----------------------------------
        # CREAR OBJETO
        # -----------------------------------

        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            usuario=usuario,
            password_hash=password_hash,
            rol=rol,
            nivel_seguridad=nivel_seguridad,
            activo=True
        )

        # -----------------------------------
        # GUARDAR
        # -----------------------------------

        session.add(nuevo_usuario)

        session.commit()

        print(
            f"\nUsuario '{usuario}' "
            f"creado correctamente.\n"
        )

    except Exception as e:

        session.rollback()

        print("\nERROR CREANDO USUARIO\n")
        print(e)

    finally:

        session.close()


# -----------------------------------
# LISTAR USUARIOS
# -----------------------------------

def listar_usuarios():

    session = SessionLocal()

    try:

        usuarios = session.query(
            Usuario
        ).all()

        print("\nLISTA USUARIOS\n")

        for usuario in usuarios:

            print(
                usuario.id,
                usuario.nombre,
                usuario.apellido,
                usuario.usuario,
                usuario.rol,
                usuario.nivel_seguridad,
                usuario.activo
            )

    finally:

        session.close()


# -----------------------------------
# BUSCAR USUARIO
# -----------------------------------

def buscar_usuario(usuario_busqueda):

    session = SessionLocal()

    try:

        usuario = session.query(
            Usuario
        ).filter(
            Usuario.usuario == usuario_busqueda
        ).first()

        return usuario

    finally:

        session.close()