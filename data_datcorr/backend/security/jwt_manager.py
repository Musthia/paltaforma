from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from platformcore.jwt import (
    create_access_token,
    verify_access_token,
    create_refresh_token,
    verify_refresh_token,
    decode_token_payload,
)
from platformcore.config import settings
from platformcore.database import SessionLocal, get_db
from platformcore.models.identity import PlatformUser, PlatformTokenBlacklist
from platformcore.services.audit import AuditService
from platformcore.services.identity import IdentityService
from platformcore.logger import logger

security = HTTPBearer()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
COOKIE_SECURE = settings.COOKIE_SECURE
INACTIVITY_MINUTES = settings.INACTIVITY_MINUTES


def crear_token(data):
    result = create_access_token(data)
    return {
        "access_token": result["access_token"],
        "jti": result["jti"],
        "expires_at": result["expires_at"],
    }


def verificar_token(token):
    payload = verify_access_token(token)
    if not payload:
        return None
    jti = payload.get("jti")
    db = SessionLocal()
    try:
        if jti and IdentityService.is_token_blacklisted(db, jti):
            return None
        return payload
    finally:
        db.close()


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    from platformcore.dependencies import get_current_user
    return get_current_user(credenciales, db)


def crear_refresh_token(data):
    result = create_refresh_token(data)
    return {
        "refresh_token": result["refresh_token"],
        "jti": result["jti"],
        "expires_at": result["expires_at"],
    }


def verificar_refresh_token(token):
    return verify_refresh_token(token)


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
