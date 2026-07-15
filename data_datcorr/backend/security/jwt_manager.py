import os
from dotenv import load_dotenv
from jose import jwt, JWTError

load_dotenv()
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database.conexion import get_db
from database.modelos_blacklist import TokenBlacklist
from backend.services.auditoria_service import registrar_auditoria

from datetime import datetime, timezone, timedelta

import uuid

from backend.database.conexion import SessionLocal

from database.modelos import Usuario

from backend.services.blacklist_service import token_esta_revocado

datetime.now(timezone.utc)

security = HTTPBearer()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY and ENVIRONMENT == "production":
    raise RuntimeError("JWT_SECRET_KEY no configurado")
if not SECRET_KEY:
    SECRET_KEY = "DATCORR_SECRET_KEY"

ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
INACTIVITY_MINUTES = int(os.getenv("INACTIVITY_MINUTES", "30"))

# -----------------------------------
# CREAR TOKEN
# -----------------------------------

def crear_token(data):

    to_encode = data.copy()

    # -----------------------------------
    # EXPIRACION
    # -----------------------------------

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # -----------------------------------
    # JWT ID (JTI)
    # -----------------------------------

    jti = str(uuid.uuid4())

    # -----------------------------------
    # PAYLOAD
    # -----------------------------------

    to_encode.update({

        "exp": expire,
        "jti": jti
    })

    # -----------------------------------
    # GENERAR TOKEN
    # -----------------------------------

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    # -----------------------------------
    # RETORNO ENTERPRISE
    # -----------------------------------

    return {

        "access_token": encoded_jwt,
        "jti": jti,
        "expires_at": expire
    }
    
# -----------------------------------
# VERIFICAR TOKEN
# -----------------------------------

def verificar_token(token):

    db: Session = SessionLocal()

    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]
        )

        # -----------------------------------
        # OBTENER JTI
        # -----------------------------------

        jti = payload.get("jti")

        usuario = payload.get("sub")

        usuario_db = (
        
            db.query(Usuario)

            .filter(
                Usuario.usuario == usuario
            )

            .first()
        )

        if not usuario_db:

            registrar_auditoria(
            
                db=db,
        
                usuario=usuario,
        
                accion="USER_NOT_FOUND",
        
                tabla="auth",
        
                detalle="JWT válido pero usuario inexistente"
            )
        
            raise HTTPException(
            
                status_code=401,
        
                detail="Usuario inexistente."
            )

        # -----------------------------------
        # TOKEN EN BLACKLIST
        # -----------------------------------

        if jti and token_esta_revocado(

            db=db,

            jti=jti
        ):

            return None

        return payload

    except JWTError:

        return None

    finally:

        db.close()

# -----------------------------------
# OBTENER USUARIO ACTUAL
# -----------------------------------

def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credenciales.credentials

    try:
        # -----------------------------------
        # DECODIFICAR JWT
        # -----------------------------------
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        jti = payload.get("jti")
        usuario = payload.get("sub")

        # -----------------------------------
        # VERIFICAR BLACKLIST (CENTRALIZADO)
        # -----------------------------------
        token_revocado = (
            db.query(TokenBlacklist)
            .filter(TokenBlacklist.token_jti == jti)
            .first()
        )

        if token_revocado:

            registrar_auditoria(
                db=db,
                usuario=usuario,
                accion="TOKEN_REVOKED_ACCESS",
                tabla="auth",
                detalle="Acceso bloqueado: token en blacklist",
                token_jti=jti
            )

            raise HTTPException(
                status_code=401,
                detail="Token revocado."
            )

        # -----------------------------------
        # OK - USUARIO AUTENTICADO
        # -----------------------------------
        return {
            "usuario": usuario,
            "nivel": payload.get("nivel"),
            "superusuario": payload.get("superusuario", False),
            "jti": jti
        }

    except JWTError as e:

        # -----------------------------------
        # LOG DE TOKEN INVALIDO
        # -----------------------------------
        try:
            registrar_auditoria(
                db=db,
                usuario="desconocido",
                accion="TOKEN_INVALID",
                tabla="auth",
                detalle=f"JWT inválido: {str(e)}"
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=401,
            detail="Token inválido."
        )

def crear_refresh_token(data):

    to_encode = data.copy()

    expire = (

        datetime.now(timezone.utc)

        +

        timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    jti = str(uuid.uuid4())

    to_encode.update({

        "exp": expire,

        "jti": jti,

        "type": "refresh"
    })

    encoded_jwt = jwt.encode(

        to_encode,

        SECRET_KEY,

        algorithm=ALGORITHM
    )

    return {

        "refresh_token": encoded_jwt,

        "jti": jti,

        "expires_at": expire
    }

def verificar_refresh_token(token):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            return None

        return payload

    except JWTError:
        return None


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
        path="/",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


def clear_refresh_cookie(response):
    response.delete_cookie("refresh_token", path="/")