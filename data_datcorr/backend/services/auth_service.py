from database.conexion import SessionLocal

from database.modelos import Usuario

from utils.hash import verificar_password

from backend.security.jwt_manager import (
    crear_token
)
from backend.security.jwt_manager import (
    crear_refresh_token
)

from database.modelos_refresh import (
    RefreshToken
)

from backend.security.jwt_manager import (
    verificar_refresh_token
)

from database.modelos import (
    Usuario,
    RefreshToken
)

from sqlalchemy.orm import Session

from backend.core.logger import logger

from backend.services.auditoria_service import (
    registrar_auditoria
)

from backend.services.blacklist_service import (

    blacklist_token,

    token_esta_revocado
)

from datetime import datetime, timedelta

def login_usuario(
    usuario,
    password
):

    session = SessionLocal()

    try:

        usuario_db = (
            session.query(Usuario)
            .filter(
                Usuario.usuario.ilike(usuario)
            )
            .first()
        )

        logger.debug(
            f"LOGIN usuario={usuario}"
        )

        if not usuario_db:

            return {
                "success": False,
                "mensaje": "Credenciales inválidas."
            }

        logger.debug(f"USUARIO_DB_ID={usuario_db.id}")

        logger.debug(
            f"ACTIVO={usuario_db.activo}"
        )

        if not usuario_db.activo:

            return {
                "success": False,
                "mensaje": "Usuario inactivo."
            }

        # -----------------------------------
        # BLOQUEO POR INTENTOS FALLIDOS
        # -----------------------------------

        MAX_ATTEMPTS = 5
        BLOCK_MINUTES = 15

        ahora = datetime.now()

        if usuario_db.bloqueado_hasta and usuario_db.bloqueado_hasta > ahora:
            logger.warning(f"Cuenta bloqueada: {usuario_db.usuario}")
            return {
                "success": False,
                "mensaje": "Cuenta bloqueada temporalmente por intentos fallidos."
            }

        password_ok = verificar_password(
            password,
            usuario_db.password_hash
        )

        logger.debug(
            f"PASSWORD_OK={password_ok}"
        )

        if not password_ok:
            usuario_db.intentos_fallidos = (usuario_db.intentos_fallidos or 0) + 1
            if usuario_db.intentos_fallidos >= MAX_ATTEMPTS:
                usuario_db.bloqueado_hasta = ahora + timedelta(minutes=BLOCK_MINUTES)
                logger.warning(f"Cuenta bloqueada tras {MAX_ATTEMPTS} intentos: {usuario_db.usuario}")
                try:
                    registrar_auditoria(db=session, usuario=usuario_db.usuario,
                                       accion="CUENTA_BLOQUEADA",
                                       tabla="auth",
                                       detalle=f"Bloqueada por {BLOCK_MINUTES} min tras {MAX_ATTEMPTS} intentos fallidos")
                except Exception:
                    pass
            session.commit()

            return {
                "success": False,
                "mensaje": "Credenciales inválidas."
            }

        # éxito → resetear contador
        usuario_db.intentos_fallidos = 0
        usuario_db.bloqueado_hasta = None

        # -----------------------------------
        # ACCESS TOKEN
        # -----------------------------------

        resultado_token = crear_token({

            "sub": usuario_db.usuario,

            "nombre": usuario_db.nombre or "",

            "apellido": usuario_db.apellido or "",

            "rol": usuario_db.rol or "",

            "nivel": (
                usuario_db.nivel_seguridad
            ),

            "superusuario": (
                usuario_db.es_superusuario
            )
        })

        # -----------------------------------
        # REFRESH TOKEN
        # -----------------------------------

        resultado_refresh = (
        
            crear_refresh_token({
            
                "sub": usuario_db.usuario
            })
        )

        # -----------------------------------
        # GUARDAR REFRESH TOKEN
        # -----------------------------------

        nuevo_refresh = RefreshToken(

            usuario_id=usuario_db.id,

            token_jti=resultado_refresh[
                "jti"
            ],

            refresh_token=resultado_refresh[
                "refresh_token"
            ],

            revoked=False,

            ip_address=None,

            user_agent=None,

            expires_at=resultado_refresh[
                "expires_at"
            ],

            access_jti=resultado_token[
                "jti"
            ],

            last_activity=datetime.now()
        )

        usuario_db.ultimo_login = datetime.now()

        session.add(
            nuevo_refresh
        )

        session.commit()

        # -----------------------------------
        # RETURN
        # -----------------------------------

        return {
            "success": True,
            "mensaje": "Login correcto.",
            
            "usuario": {
                "id": usuario_db.id,
                "usuario": usuario_db.usuario,
                "nombre": usuario_db.nombre,
                "apellido": usuario_db.apellido,
                "rol": usuario_db.rol,
                "nivel_seguridad": usuario_db.nivel_seguridad,
                "es_superusuario": usuario_db.es_superusuario
            },
        
            "token": resultado_token["access_token"],
            "refresh_token": resultado_refresh["refresh_token"],
            "jti": resultado_token["jti"]
        }

    finally:

        session.close()

def refresh_access_token(

    db: Session,

    refresh_token: str
    ):

    try:

        # -----------------------------------
        # VALIDAR REFRESH TOKEN
        # -----------------------------------

        payload = verificar_refresh_token(
            refresh_token
        )

        if not payload:

            return {

                "success": False,

                "mensaje": (
                    "Refresh token inválido."
                )
            }
        # -----------------------------------
        # OBTENER USUARIO
        # -----------------------------------

        usuario = payload.get("sub")

        usuario_db = (

            db.query(Usuario)

            .filter(
                Usuario.usuario == usuario
            )

            .first()
        )

        if not usuario_db:

            return {

                "success": False,

                "mensaje": (
                    "Usuario inexistente."
                )
            }
        # -----------------------------------
        # REVOCAR TOKEN ANTERIOR
        # -----------------------------------

        token_db = (
        
            db.query(RefreshToken)

            .filter(
                RefreshToken.refresh_token
                == refresh_token
            )

            .first()
        )

        # -----------------------------------
        # TOKEN NO EXISTE
        # -----------------------------------

        if not token_db:
        
            return {
            
                "success": False,

                "mensaje": (
                    "Refresh token inexistente."
                )
            }

        # -----------------------------------
        # REUSE DETECTION
        # -----------------------------------

        if token_db.revoked:

            logger.critical(

                f"REUSE DETECTADO | "
                f"usuario_id={token_db.usuario_id} | "
                f"jti={token_db.token_jti}"
            )

            registrar_auditoria(

                db=db,

                usuario=usuario_db.usuario,

                accion="TOKEN_REUSE_DETECTED",

                tabla="auth",

                registro_id=usuario_db.id,

                endpoint="/usuarios/refresh",

                detalle=(
                    "Intento reutilización "
                    "refresh token revocado"
                ),

                token_jti=token_db.token_jti
            )
        
            # -----------------------------------
            # REVOCAR TODAS LAS SESIONES
            # -----------------------------------

            db.query(RefreshToken).filter(
            
                RefreshToken.usuario_id
                == token_db.usuario_id

            ).update({
            
                "revoked": True
            })

            db.commit()

            return {
            
                "success": False,

                "mensaje": (
                    "Reuse detection activado."
                )
            }

        if token_db:
        
            token_db.revoked = True
        

        # -----------------------------------
        # NUEVO ACCESS TOKEN
        # -----------------------------------

        nuevo_access = crear_token({
        
            "sub": usuario_db.usuario,

            "nivel": (
                usuario_db.nivel_seguridad
            ),

            "superusuario": (
                usuario_db.es_superusuario
            )
        })

        # -----------------------------------
        # NUEVO REFRESH TOKEN
        # -----------------------------------

        nuevo_refresh = crear_refresh_token({
        
            "sub": usuario_db.usuario,

            "nivel": (
                usuario_db.nivel_seguridad
            ),

            "superusuario": (
                usuario_db.es_superusuario
            )
        })

        # -----------------------------------
        # GUARDAR NUEVO REFRESH
        # -----------------------------------

        refresh_db = RefreshToken(
        
            usuario_id=usuario_db.id,

            token_jti=nuevo_refresh[
                "jti"
            ],

            refresh_token=nuevo_refresh[
                "refresh_token"
            ],

            revoked=False,

            ip_address=None,

            user_agent=None,

            expires_at=nuevo_refresh[
                "expires_at"
            ],

            access_jti=nuevo_access[
                "jti"
            ],

            last_activity=datetime.now()
        )

        db.add(refresh_db)

        db.commit()

        # -----------------------------------
        # RETURN
        # -----------------------------------

        return {
        
            "success": True,

            "access_token": nuevo_access[
                "access_token"
            ],

            "refresh_token": nuevo_refresh[
                "refresh_token"
            ]
        }

    except Exception as e:
        
        return {
            
            "success": False,

            "mensaje": str(e)
        }

# -----------------------------------
# LOGOUT USUARIO
# -----------------------------------

def logout_usuario(

    db: Session,

    refresh_token: str
):

    try:

        # -----------------------------------
        # BUSCAR TOKEN
        # -----------------------------------

        token_db = (

            db.query(RefreshToken)

            .filter(
                RefreshToken.refresh_token
                == refresh_token
            )

            .first()
        )

        # -----------------------------------
        # TOKEN NO EXISTE
        # -----------------------------------

        if not token_db:

            return {

                "success": False,

                "mensaje": (
                    "Refresh token inexistente."
                )
            }

        # -----------------------------------
        # YA REVOCADO
        # -----------------------------------

        if token_db.revoked:
            registrar_auditoria(

            db=db,

            usuario="desconocido",

            accion="LOGOUT_FAILED",

            tabla="auth",

            detalle="Intento logout con refresh inválido"
        )

            return {

                "success": False,

                "mensaje": (
                    "Refresh token ya revocado."
                )
            }

        # -----------------------------------
        # REVOCAR TOKEN
        # -----------------------------------
        
        token_db.revoked = True
        
        db.commit()
        
        # -----------------------------------
        # OBTENER USUARIO
        # -----------------------------------
        
        usuario_db = (
        
            db.query(Usuario)
        
            .filter(
                Usuario.id == token_db.usuario_id
            )
        
            .first()
        )
        
        # -----------------------------------
        # AUDITORIA
        # -----------------------------------
        
        registrar_auditoria(
        
            db=db,
        
            usuario=usuario_db.usuario,
        
            accion="LOGOUT_SUCCESS",
        
            tabla="auth",
        
            registro_id=usuario_db.id,
        
            detalle="Logout exitoso"
        )

        # -----------------------------------
        # RETURN
        # -----------------------------------

        return {

            "success": True,

            "mensaje": (
                "Logout correcto."
            )
        }

    except Exception as e:

        return {

            "success": False,

            "mensaje": str(e)
        }
