import logging

from database.conexion import SessionLocal
from database.modelos import Usuario
from utils.hash import hash_password
from config.app_config import MODO_DESARROLLO

from repositories.usuarios_repository import UsuariosRepository

repo = UsuariosRepository()

# -----------------------------------
# SERIALIZACIÓN (NO ORM)
# -----------------------------------

def usuario_to_dict(usuario):

    if not usuario:
        return None

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "usuario": usuario.usuario,
        "rol": usuario.rol,
        "nivel_seguridad": usuario.nivel_seguridad,
        "activo": usuario.activo,
        "es_superusuario": usuario.es_superusuario
    }

# -----------------------------------

# LISTAR USUARIOS (DICT)

# -----------------------------------

def listar_usuarios_dict():

    usuarios = listar_usuarios()

    return [

        usuario_to_dict(usuario)

        for usuario

        in usuarios
    ]

# -----------------------------------

# OBTENER USUARIO POR ID (DICT)

# -----------------------------------

def obtener_usuario_por_id_dict(
    usuario_id
    ):

    
    usuario = obtener_usuario_por_id(
        usuario_id
    )

    return usuario_to_dict(
        usuario
    )



# -----------------------------------

# LISTAR USUARIOS ACTIVOS (DICT)

# -----------------------------------

def listar_usuarios_activos_dict():


    usuarios = listar_usuarios_activos()

    return [

        usuario_to_dict(usuario)

        for usuario

        in usuarios
    ]


# -----------------------------------

# LISTAR USUARIOS INACTIVOS (DICT)

# -----------------------------------

def listar_usuarios_inactivos_dict():


    usuarios = listar_usuarios_inactivos()

    return [

        usuario_to_dict(usuario)

        for usuario

        in usuarios
    ]


# -----------------------------------

# -----------------------------------
# ACTUALIZAR USUARIO
# -----------------------------------

def actualizar_usuario(
    usuario_id,
    nombre,
    apellido,
    usuario,
    rol,
    nivel_seguridad,
    activo,
    password=None
):

    try:

        usuario_db = repo.get_by_id(usuario_id)

        if not usuario_db:
            return {
                "success": False,
                "mensaje": "Usuario no encontrado."
            }

        usuario_db.nombre = nombre
        usuario_db.apellido = apellido
        usuario_db.usuario = usuario
        usuario_db.rol = rol
        usuario_db.nivel_seguridad = nivel_seguridad
        usuario_db.activo = activo

        if password:
            usuario_db.password_hash = hash_password(password)

        repo.update()

        logging.debug(f"Usuario actualizado: {usuario}")

        return {
            "success": True,
            "mensaje": "Usuario actualizado."
        }

    except Exception as e:

        logging.exception("Error actualizando usuario")

        return {
            "success": False,
            "mensaje": str(e)
        }

    finally:
        repo.close()

# -----------------------------------
# CAMBIAR PASSWORD
# -----------------------------------

def cambiar_password(
    usuario_id,
    nueva_password
):
    session = SessionLocal()

    try:

        usuario = (
            session.query(Usuario)
            .filter(
                Usuario.id == usuario_id
            )
            .first()
        )

        if not usuario:

            return {
                "success": False,
                "mensaje": "Usuario no encontrado."
            }

        usuario.password_hash = (
            hash_password(
                nueva_password
            )
        )

        session.commit()

        return {
            "success": True,
            "mensaje": "Password actualizada."
        }

    except Exception as e:

        session.rollback()

        return {
            "success": False,
            "mensaje": str(e)
        }

    finally:

        session.close()


# -----------------------------------
# ACTIVAR / DESACTIVAR
# -----------------------------------

def cambiar_estado_usuario(
    usuario_id,
    activo
):

    session = SessionLocal()

    try:

        usuario = session.query(
            Usuario
        ).filter(
            Usuario.id == usuario_id
        ).first()

        if not usuario:

            return {
                "success": False,
                "mensaje": "Usuario no encontrado."
            }

        usuario.activo = activo

        session.commit()

        estado = (
            "activado"
            if activo
            else "desactivado"
        )

        return {
            "success": True,
            "mensaje": f"Usuario {estado}."
        }

    except Exception as e:

        session.rollback()

        return {
            "success": False,
            "mensaje": str(e)
        }

    finally:

        session.close()

# -----------------------------------
# LISTAR USUARIOS
# -----------------------------------

def listar_usuarios():

    repo = UsuariosRepository()

    try:
        return repo.get_all()

    finally:
        repo.close()


# -----------------------------------
# OBTENER USUARIO POR ID
# -----------------------------------

def obtener_usuario_por_id(usuario_id):

    try:

        return repo.get_by_id(usuario_id)

    finally:

        repo.close()
# -----------------------------------
# LISTAR USUARIOS ACTIVOS
# -----------------------------------

def listar_usuarios_activos():

    db = SessionLocal()

    try:

        usuarios = (
            db.query(Usuario)
            .filter(
                Usuario.activo == True
            )
            .order_by(
                Usuario.id.asc()
            )
            .all()
        )

        return usuarios

    finally:

        db.close()

# -----------------------------------
# LISTAR USUARIOS INACTIVOS
# -----------------------------------

def listar_usuarios_inactivos():

    db = SessionLocal()

    try:

        usuarios = (
            db.query(Usuario)
            .filter(
                Usuario.activo == False
            )
            .order_by(
                Usuario.id.asc()
            )
            .all()
        )

        return usuarios

    finally:

        db.close()    

def desactivar_usuario(usuario_id):

    session = SessionLocal()

    try:

        usuario = session.query(
            Usuario
        ).filter(
            Usuario.id == usuario_id
        ).first()

        if not usuario:

            return {
                "success": False,
                "mensaje": "Usuario no encontrado."
            }

        usuario.activo = False

        session.commit()

        return {
            "success": True,
            "mensaje": "Usuario desactivado."
        }

    except Exception as e:

        session.rollback()

        return {
            "success": False,
            "mensaje": str(e)
        }

    finally:

        session.close()

def activar_usuario(usuario_id):

    session = SessionLocal()

    try:

        usuario = session.query(
            Usuario
        ).filter(
            Usuario.id == usuario_id
        ).first()

        if not usuario:

            return {
                "success": False,
                "mensaje": "Usuario no encontrado."
            }

        usuario.activo = True

        session.commit()

        return {
            "success": True,
            "mensaje": "Usuario activado."
        }

    except Exception as e:

        session.rollback()

        return {
            "success": False,
            "mensaje": str(e)
        }

    finally:

        session.close()

def crear_usuario(
    nombre,
    apellido,
    usuario,
    password,
    rol,
    nivel_seguridad,
    activo=True
):

    try:

        # validar existencia
        existente = repo.session.query(Usuario).filter(
            Usuario.usuario == usuario
        ).first()

        if existente:

            return {
                "success": False,
                "mensaje": "El usuario ya existe."
            }

        nuevo = Usuario(
            nombre=nombre,
            apellido=apellido,
            usuario=usuario,
            password_hash=hash_password(password),
            rol=rol,
            nivel_seguridad=nivel_seguridad,
            activo=activo,
            es_superusuario=False
        )

        repo.create(nuevo)

        return {
            "success": True,
            "mensaje": "Usuario creado."
        }

    except Exception as e:

        logging.exception("Error creando usuario")

        return {
            "success": False,
            "mensaje": str(e)
        }

    finally:
        repo.close()