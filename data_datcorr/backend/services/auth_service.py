from datetime import datetime

from sqlalchemy.orm import Session

from platformcore.services.identity import IdentityService
from platformcore.models.identity import PlatformUser, PlatformRefreshToken
from platformcore.logger import logger


def login_usuario(usuario, password, ip_address="", user_agent=""):
    from platformcore.database import SessionLocal
    db = SessionLocal()
    try:
        result = IdentityService.login(
            db=db,
            username=usuario,
            password=password,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        if not result["success"]:
            return {"success": False, "mensaje": result["mensaje"]}

        return {
            "success": True,
            "mensaje": "Login correcto.",
            "usuario": result["user"],
            "token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "jti": result["jti"],
        }
    finally:
        db.close()


def refresh_access_token(db: Session, refresh_token: str):
    result = IdentityService.refresh(db, refresh_token)
    return result


def logout_usuario(db: Session, refresh_token: str):
    result = IdentityService.logout(db, refresh_token)
    return result
