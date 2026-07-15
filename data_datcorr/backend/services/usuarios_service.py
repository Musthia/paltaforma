from sqlalchemy.orm import Session

from sqlalchemy.exc import (
    IntegrityError
)

from database.modelos import Usuario

from database.modelos_roles import UsuarioRol

from utils.hash import hash_password

from backend.core.logger import logger

from sqlalchemy import or_

from typing import Optional

from backend.services.auditoria_service import (
    registrar_auditoria
)

# -----------------------------------
# LISTAR USUARIOS
# -----------------------------------

def listar_usuarios_web(

    db: Session,

    page: int = 1,

    limit: int = 20,

    search: str = "",

    rol: str = "",

    activo: Optional[bool] = None,

    incluir_inactivos: bool = False,

    sort_by: str = "id",

    order: str = "asc"
):

    logger.info(
        "LISTANDO USUARIOS WEB"
    )

    query = db.query(Usuario)

    # -----------------------------
    # FILTRAR ACTIVOS
    # -----------------------------

    if not incluir_inactivos:

        query = query.filter(
            Usuario.activo == True
        )

    # -----------------------------
    # BUSQUEDA TEXTO
    # -----------------------------

    if search:

        texto = f"%{search}%"

        query = query.filter(

            or_(

                Usuario.nombre.ilike(
                    texto
                ),

                Usuario.apellido.ilike(
                    texto
                ),

                Usuario.usuario.ilike(
                    texto
                )
            )
        )

        logger.info(
            f"Busqueda usuarios: "
            f"{search}"
        )

    # -----------------------------
    # FILTRO ROL
    # -----------------------------
    if rol:
    
        query = query.filter(
            Usuario.rol == rol
        )
        logger.info(
            f"Filtro rol: {rol}"
        )

    # -----------------------------
    # FILTRO ACTIVO
    # -----------------------------
    if activo is not None:
    
        query = query.filter(
            Usuario.activo == activo
        )
        logger.info(
            f"Filtro activo: {activo}"
        )

    COLUMNAS_ORDEN_PERMITIDAS = {

        "id": Usuario.id,

        "nombre": Usuario.nombre,

        "apellido": Usuario.apellido,

        "usuario": Usuario.usuario,

        "rol": Usuario.rol,

        "nivel_seguridad": Usuario.nivel_seguridad,

        "activo": Usuario.activo
    }

    # -----------------------------
    # ORDENAMIENTO
    # -----------------------------

    columnas_ordenables = {

        "id": Usuario.id,

        "nombre": Usuario.nombre,

        "apellido": Usuario.apellido,

        "usuario": Usuario.usuario,

        "rol": Usuario.rol,

        "nivel_seguridad": (
            Usuario.nivel_seguridad
        )
    }

    # -----------------------------
    # VALIDAR COLUMNA
    # -----------------------------

    if sort_by not in COLUMNAS_ORDEN_PERMITIDAS:

        logger.warning(
            f"Columna inválida ORDER BY: {sort_by}"
        )

        sort_by = "id"

    # -----------------------------
    # OBTENER COLUMNA SEGURA
    # -----------------------------

    columna = (
        COLUMNAS_ORDEN_PERMITIDAS[
            sort_by
        ]
    )

    # -----------------------------
    # ASC / DESC
    # -----------------------------

    if order == "desc":

        query = query.order_by(
            columna.desc()
        )

    else:

        query = query.order_by(
            columna.asc()
        )

    logger.info(
        f"Ordenando por {sort_by} {order}"
    )
    

    # -----------------------------
    # TOTAL
    # -----------------------------

    total = query.count()

    # -----------------------------
    # PAGINAS
    # -----------------------------

    pages = (

        total + limit - 1

    ) // limit

    # -----------------------------
    # OFFSET
    # -----------------------------

    offset = (

        page - 1

    ) * limit

    # -----------------------------
    # PAGINACION
    # -----------------------------

    usuarios = (

        query

        .offset(offset)

        .limit(limit)

        .all()
    )

    logger.info(
        f"Usuarios encontrados: "
        f"{len(usuarios)}"
    )

    return {

        "usuarios": usuarios,

        "total": total,

        "pages": pages,

        "page": page,

        "limit": limit
    }

# -----------------------------------
# CREAR USUARIO
# -----------------------------------

def crear_usuario_web(
    db: Session,
    datos
):

    try:

        logger.info(
            f"Creando usuario: "
            f"{datos.usuario}"
        )

        # -------------------------
        # VALIDAR PASSWORD
        # -------------------------

        if len(datos.password) < 4:

            logger.warning(
                "Password demasiado corta"
            )

            return {

                "success": False,

                "mensaje": (
                    "Password demasiado corta."
                )
            }

        # -------------------------
        # USUARIO EXISTENTE
        # -------------------------

        usuario_existente = (

            db.query(Usuario)

            .filter(
                Usuario.usuario ==
                datos.usuario
            )

            .first()
        )

        if usuario_existente:

            logger.warning(
                f"Usuario duplicado: "
                f"{datos.usuario}"
            )

            return {

                "success": False,

                "mensaje": (
                    "Usuario ya existe."
                )
            }

        # -------------------------
        # EMAIL EXISTENTE
        # -------------------------

        if datos.email:

            email_existente = (

                db.query(Usuario)

                .filter(
                    Usuario.email ==
                    datos.email
                )

                .first()
            )

            if email_existente:

                logger.warning(
                    f"Email duplicado: "
                    f"{datos.email}"
                )

                return {

                    "success": False,

                    "mensaje": (
                        "El correo ya está "
                        "registrado."
                    )
                }

        # -------------------------
        # CREAR USUARIO
        # -------------------------

        nuevo_usuario = Usuario(

            nombre=datos.nombre,

            apellido=datos.apellido,

            usuario=datos.usuario,

            password_hash=hash_password(
                datos.password
            ),

            email=getattr(datos, 'email', None),

            rol=datos.rol,

            nivel_seguridad=(
                datos.nivel_seguridad
            ),

            activo=datos.activo
        )

        db.add(nuevo_usuario)

        db.flush()

        # -------------------------
        # ROLES (normalizados)
        # -------------------------

        from backend.services.roles_service import (
            asignar_rol_usuario
        )

        asignar_rol_usuario(
            db, nuevo_usuario.id, datos.rol
        )

        if datos.roles_nombre:
            for r in datos.roles_nombre:
                if r != datos.rol:
                    asignar_rol_usuario(
                        db, nuevo_usuario.id, r
                    )

        db.commit()

        db.refresh(nuevo_usuario)

        # -----------------------------
        # AUDITORIA
        # -----------------------------
    
        registrar_auditoria(
        
            db=db,
    
            usuario=datos.usuario,
    
            accion="CREATE",
    
            tabla="usuarios",
    
            registro_id=nuevo_usuario.id,
    
            detalle=(
                f"Usuario creado: "
                f"{datos.usuario}"
            )
        )

        logger.info(
            f"Usuario creado ID="
            f"{nuevo_usuario.id}"
        )

        return {

            "success": True,

            "mensaje": (
                "Usuario creado."
            ),

            "usuario_id": (
                nuevo_usuario.id
            )
        }

    # ---------------------------------
    # INTEGRITY ERROR
    # ---------------------------------

    except IntegrityError as e:

        db.rollback()

        logger.error(
            f"IntegrityError: {str(e)}"
        )

        return {

            "success": False,

            "mensaje": (
                "Error integridad DB."
            )
        }

    # ---------------------------------
    # ERROR GENERAL
    # ---------------------------------

    except Exception as e:

        db.rollback()

        logger.error(
            f"Error creando usuario: "
            f"{str(e)}"
        )

        return {

            "success": False,

            "mensaje": (
                "Error interno."
            )
        }

# -----------------------------------
# ACTUALIZAR USUARIO
# -----------------------------------

def actualizar_usuario_web(

    db: Session,

    usuario_id: int,

    datos
):

    try:

        logger.info(
            f"Actualizando usuario ID="
            f"{usuario_id}"
        )

        # -------------------------
        # BUSCAR USUARIO
        # -------------------------

        usuario_db = (

            db.query(Usuario)

            .filter(
                Usuario.id == usuario_id
            )

            .first()
        )

        # -------------------------
        # NO EXISTE
        # -------------------------

        if not usuario_db:

            logger.warning(
                f"Usuario inexistente "
                f"ID={usuario_id}"
            )

            return {

                "success": False,

                "mensaje": (
                    "Usuario no encontrado."
                )
            }
        # -------------------------
        # ESTADO ANTERIOR
        # -------------------------
        
        before_data = {
        
            "nombre": usuario_db.nombre,
        
            "apellido": usuario_db.apellido,
        
            "usuario": usuario_db.usuario,
        
            "rol": usuario_db.rol,
        
            "nivel_seguridad": (
                usuario_db.nivel_seguridad
            ),
        
            "activo": usuario_db.activo
        } 

        # -------------------------
        # VALIDAR DUPLICADO USUARIO
        # -------------------------

        if datos.usuario:

            usuario_existente = (

                db.query(Usuario)

                .filter(
                    Usuario.usuario ==
                    datos.usuario,

                    Usuario.id != usuario_id
                )

                .first()
            )

            if usuario_existente:

                logger.warning(
                    f"Usuario duplicado: "
                    f"{datos.usuario}"
                )

                return {

                    "success": False,

                    "mensaje": (
                        "Nombre usuario "
                        "ya existe."
                    )
                }

        # -------------------------
        # VALIDAR DUPLICADO EMAIL
        # -------------------------

        if datos.email:

            email_existente = (

                db.query(Usuario)

                .filter(
                    Usuario.email ==
                    datos.email,

                    Usuario.id != usuario_id
                )

                .first()
            )

            if email_existente:

                logger.warning(
                    f"Email duplicado: "
                    f"{datos.email}"
                )

                return {

                    "success": False,

                    "mensaje": (
                        "El correo ya está "
                        "registrado por otro "
                        "usuario."
                    )
                }

        # -------------------------
        # UPDATE PARCIAL DINAMICO
        # -------------------------

        update_data = datos.dict(
            exclude_unset=True
        )

        logger.warning(update_data)

        roles_nombre = update_data.pop(
            "roles_nombre", None
        )

        for campo, valor in (
            update_data.items()
        ):

            # ---------------------
            # PASSWORD
            # ---------------------

            if campo == "password":
            
                if len(valor) < 4:
                
                    return {
                    
                        "success": False,

                        "mensaje": (
                            "Password demasiado corta."
                        )
                    }

                usuario_db.password_hash = (
                    hash_password(valor)
                )

            else:
            
                setattr(
                    usuario_db,
                    campo,
                    valor
                )

        # -------------------------
        # ROLES (normalizados)
        # -------------------------

        if "rol" in update_data or roles_nombre:

            from backend.services.roles_service import (
                asignar_rol_usuario
            )

            roles_a_asignar = set()

            if "rol" in update_data:
                roles_a_asignar.add(
                    update_data["rol"]
                )

            if roles_nombre:
                roles_a_asignar.update(
                    roles_nombre
                )

            db.query(UsuarioRol).filter(
                UsuarioRol.usuario_id ==
                usuario_db.id
            ).delete()

            for r in roles_a_asignar:
                asignar_rol_usuario(
                    db, usuario_db.id, r
                )

        # -------------------------
        # COMMIT
        # -------------------------

        db.commit()

        # -------------------------
        # ESTADO NUEVO
        # -------------------------

        after_data = {

            "nombre": usuario_db.nombre,

            "apellido": usuario_db.apellido,

            "usuario": usuario_db.usuario,

            "rol": usuario_db.rol,

            "nivel_seguridad": (
                usuario_db.nivel_seguridad
            ),

            "activo": usuario_db.activo
        }

        # -------------------------
        # AUDITORIA
        # -------------------------

        registrar_auditoria(

            db=db,

            usuario=usuario_db.usuario,

            accion="UPDATE",

            tabla="usuarios",

            registro_id=usuario_db.id,

            detalle=(

                f"ANTES: {before_data} | "

                f"DESPUES: {after_data}"
            )
        )

        logger.info(
            f"Usuario actualizado "
            f"ID={usuario_id}"
        )

        return {

            "success": True,

            "mensaje": (
                "Usuario actualizado."
            )
        }

    # ---------------------------------
    # INTEGRITY ERROR
    # ---------------------------------

    except IntegrityError as e:

        db.rollback()

        logger.error(
            f"IntegrityError UPDATE: "
            f"{str(e)}"
        )

        return {

            "success": False,

            "mensaje": (
                "Error integridad DB."
            )
        }

    # ---------------------------------
    # ERROR GENERAL
    # ---------------------------------

    except Exception as e:

        db.rollback()

        logger.error(
            f"Error UPDATE usuario: "
            f"{str(e)}"
        )

        return {

            "success": False,

            "mensaje": (
                "Error interno."
            )
        }

# -----------------------------------
# DESACTIVAR USUARIO
# -----------------------------------

def desactivar_usuario_web(

    db: Session,

    usuario_id: int,

    usuario_actual: str
):

    logger.info(
        f"Desactivando usuario "
        f"ID={usuario_id}"
    )

    try:

        # -----------------------------
        # BUSCAR USUARIO
        # -----------------------------

        usuario = (

            db.query(Usuario)

            .filter(
                Usuario.id == usuario_id
            )

            .first()
        )

        # -----------------------------
        # NO EXISTE
        # -----------------------------

        if not usuario:

            logger.warning(
                f"Usuario inexistente "
                f"ID={usuario_id}"
            )

            # -----------------------------
            # AUDITORIA
            # -----------------------------

            registrar_auditoria(

                db=db,

                usuario=usuario_actual,

                accion="DELETE_LOGICO_ERROR",

                tabla="usuarios",

                registro_id=usuario_id,

                detalle=(
                    "Intento eliminar "
                    "usuario inexistente"
                )
            )

            return {

                "success": False,

                "mensaje": (
                    "Usuario no existe."
                )
            }

        # -----------------------------
        # YA DESACTIVADO
        # -----------------------------

        if not usuario.activo:

            logger.warning(
                f"Usuario ya "
                f"desactivado "
                f"ID={usuario_id}"
            )

            # -----------------------------
            # AUDITORIA
            # -----------------------------

            registrar_auditoria(

                db=db,

                usuario=usuario_actual,

                accion="DELETE_LOGICO_ERROR",

                tabla="usuarios",

                registro_id=usuario.id,

                detalle=(
                    "Intento desactivar "
                    "usuario ya desactivado"
                )
            )

            return {

                "success": False,

                "mensaje": (
                    "Usuario ya "
                    "desactivado."
                )
            }

        # -----------------------------
        # PROTEGER SUPERUSUARIO
        # -----------------------------

        if usuario.es_superusuario:

            logger.warning(
                "Intento desactivar "
                "superusuario"
            )

            # -----------------------------
            # AUDITORIA
            # -----------------------------

            registrar_auditoria(

                db=db,

                usuario=usuario_actual,

                accion="DELETE_LOGICO_ERROR",

                tabla="usuarios",

                registro_id=usuario.id,

                detalle=(
                    "Intento desactivar "
                    "superusuario"
                )
            )

            return {

                "success": False,

                "mensaje": (
                    "No se puede "
                    "desactivar "
                    "superusuario."
                )
            }

        # -----------------------------
        # BEFORE DATA
        # -----------------------------

        before_data = {

            "nombre": usuario.nombre,

            "apellido": usuario.apellido,

            "usuario": usuario.usuario,

            "rol": usuario.rol,

            "activo": usuario.activo
        }

        # -----------------------------
        # SOFT DELETE
        # -----------------------------

        usuario.activo = False

        db.commit()

        # -----------------------------
        # AFTER DATA
        # -----------------------------

        after_data = {

            "nombre": usuario.nombre,

            "apellido": usuario.apellido,

            "usuario": usuario.usuario,

            "rol": usuario.rol,

            "activo": usuario.activo
        }

        # -----------------------------
        # AUDITORIA
        # -----------------------------

        registrar_auditoria(

            db=db,

            usuario=usuario_actual,

            accion="DELETE_LOGICO",

            tabla="usuarios",

            registro_id=usuario.id,

            detalle=(

                f"ANTES: {before_data} | "

                f"DESPUES: {after_data}"
            )
        )

        logger.info(
            f"Usuario desactivado "
            f"ID={usuario_id}"
        )

        return {

            "success": True,

            "mensaje": (
                "Usuario desactivado."
            )
        }

    # -----------------------------
    # INTEGRITY ERROR
    # -----------------------------

    except IntegrityError as e:

        db.rollback()

        logger.error(
            f"IntegrityError "
            f"desactivar usuario: {e}"
        )

        registrar_auditoria(

            db=db,

            usuario=usuario_actual,

            accion="DELETE_LOGICO_ERROR",

            tabla="usuarios",

            registro_id=usuario_id,

            detalle=f"IntegrityError: {str(e)}"
        )

        return {

            "success": False,

            "mensaje": (
                "Error integridad DB."
            )
        }

    # -----------------------------
    # ERROR GENERAL
    # -----------------------------

    except Exception as e:

        db.rollback()

        logger.exception(
            f"Error desactivar "
            f"usuario: {e}"
        )

        registrar_auditoria(

            db=db,

            usuario=usuario_actual,

            accion="DELETE_LOGICO_ERROR",

            tabla="usuarios",

            registro_id=usuario_id,

            detalle=f"Exception: {str(e)}"
        )

        return {

            "success": False,

            "mensaje": (
                "Error interno."
            )
        }


# -----------------------------------
# REACTIVAR USUARIO
# -----------------------------------

def reactivar_usuario_web(

    db: Session,

    usuario_id: int,

    usuario_actual: str
):

    logger.info(
        f"Reactivando usuario "
        f"ID={usuario_id}"
    )

    try:

        usuario = db.query(Usuario).filter(
            Usuario.id == usuario_id
        ).first()

        if not usuario:

            logger.warning(
                f"Usuario inexistente "
                f"ID={usuario_id}"
            )

            return {
                "success": False,
                "mensaje": "Usuario no existe."
            }

        if usuario.activo:

            logger.warning(
                f"Usuario ya activo "
                f"ID={usuario_id}"
            )

            return {
                "success": False,
                "mensaje": "Usuario ya esta activo."
            }

        usuario.activo = True

        db.commit()

        registrar_auditoria(

            db=db,

            usuario=usuario_actual,

            accion="REACTIVATE",

            tabla="usuarios",

            registro_id=usuario.id,

            detalle=(
                f"Usuario reactivado: "
                f"{usuario.usuario}"
            )
        )

        logger.info(
            f"Usuario reactivado "
            f"ID={usuario_id}"
        )

        return {
            "success": True,
            "mensaje": "Usuario reactivado."
        }

    except Exception as e:

        db.rollback()

        logger.exception(
            f"Error reactivar "
            f"usuario: {e}"
        )

        return {
            "success": False,
            "mensaje": "Error interno."
        }