from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from platformcore.config import settings
from platformcore.jwt import create_access_token, create_refresh_token, verify_refresh_token
from platformcore.security import hash_password, verify_password
from platformcore.logger import logger
from platformcore.exceptions import AuthError

from platformcore.models.identity import (
    PlatformUser,
    PlatformRefreshToken,
    PlatformTokenBlacklist,
    PlatformPasswordResetToken,
)


class IdentityService:

    @staticmethod
    def login(db: Session, username: str, password: str, ip_address: str = "", user_agent: str = ""):
        user = db.query(PlatformUser).filter(PlatformUser.username.ilike(username)).first()

        if not user:
            return {"success": False, "mensaje": "Credenciales inválidas."}

        logger.debug(f"LOGIN user={username} active={user.is_active}")

        if not user.is_active:
            return {"success": False, "mensaje": "Usuario inactivo."}

        # bloqueo por intentos
        now = datetime.now()
        if user.locked_until and user.locked_until > now:
            logger.warning(f"Cuenta bloqueada: {user.username}")
            return {"success": False, "mensaje": "Cuenta bloqueada temporalmente por intentos fallidos."}

        if not verify_password(password, user.password_hash):
            user.failed_attempts = (user.failed_attempts or 0) + 1
            if user.failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=settings.BLOCK_MINUTES)
                logger.warning(f"Cuenta bloqueada tras {settings.MAX_LOGIN_ATTEMPTS} intentos: {user.username}")
            db.commit()
            return {"success": False, "mensaje": "Credenciales inválidas."}

        # éxito
        user.failed_attempts = 0
        user.locked_until = None

        token_result = create_access_token({
            "sub": user.username,
            "user_id": user.id,
            "role": user.role,
            "nivel": user.nivel_seguridad,
            "is_superuser": user.is_superuser,
            "full_name": user.full_name or "",
        })

        refresh_result = create_refresh_token({"sub": user.username, "user_id": user.id})

        # guardar refresh token
        rt = PlatformRefreshToken(
            user_id=user.id,
            token_jti=refresh_result["jti"],
            refresh_token=refresh_result["refresh_token"],
            revoked=False,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=refresh_result["expires_at"],
            access_jti=token_result["jti"],
            last_activity=datetime.now(),
        )
        db.add(rt)

        user.last_login = datetime.now()
        db.commit()

        return {
            "success": True,
            "mensaje": "Login correcto.",
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "nivel_seguridad": user.nivel_seguridad,
                "is_superuser": user.is_superuser,
            },
            "access_token": token_result["access_token"],
            "refresh_token": refresh_result["refresh_token"],
            "jti": token_result["jti"],
        }

    @staticmethod
    def refresh(db: Session, refresh_token_str: str):
        payload = verify_refresh_token(refresh_token_str)
        if not payload:
            return {"success": False, "mensaje": "Refresh token inválido."}

        username = payload.get("sub")
        user = db.query(PlatformUser).filter(PlatformUser.username == username).first()
        if not user:
            return {"success": False, "mensaje": "Usuario inexistente."}

        # buscar token en DB
        token_db = db.query(PlatformRefreshToken).filter(
            PlatformRefreshToken.refresh_token == refresh_token_str
        ).first()

        if not token_db:
            return {"success": False, "mensaje": "Refresh token inexistente."}

        if token_db.revoked:
            logger.critical(f"REUSE DETECTED | user_id={token_db.user_id} | jti={token_db.token_jti}")
            # revocar todas las sesiones del usuario
            db.query(PlatformRefreshToken).filter(
                PlatformRefreshToken.user_id == token_db.user_id
            ).update({"revoked": True})
            db.commit()
            return {"success": False, "mensaje": "Reuse detection activado. Todas las sesiones revocadas."}

        # revocar token anterior
        token_db.revoked = True

        nuevo_access = create_access_token({
            "sub": user.username, "user_id": user.id, "role": user.role,
            "nivel": user.nivel_seguridad, "is_superuser": user.is_superuser,
        })
        nuevo_refresh = create_refresh_token({"sub": user.username, "user_id": user.id})

        nuevo_rt = PlatformRefreshToken(
            user_id=user.id,
            token_jti=nuevo_refresh["jti"],
            refresh_token=nuevo_refresh["refresh_token"],
            revoked=False,
            expires_at=nuevo_refresh["expires_at"],
            access_jti=nuevo_access["jti"],
            last_activity=datetime.now(),
        )
        db.add(nuevo_rt)
        db.commit()

        return {
            "success": True,
            "access_token": nuevo_access["access_token"],
            "refresh_token": nuevo_refresh["refresh_token"],
        }

    @staticmethod
    def logout(db: Session, refresh_token_str: str):
        token_db = db.query(PlatformRefreshToken).filter(
            PlatformRefreshToken.refresh_token == refresh_token_str
        ).first()

        if not token_db:
            return {"success": False, "mensaje": "Refresh token inexistente."}

        if token_db.revoked:
            return {"success": False, "mensaje": "Refresh token ya revocado."}

        token_db.revoked = True
        db.commit()
        return {"success": True, "mensaje": "Logout correcto."}

    @staticmethod
    def blacklist_jti(db: Session, jti: str, username: str, motivo: str = "logout"):
        existe = db.query(PlatformTokenBlacklist).filter(
            PlatformTokenBlacklist.jti == jti
        ).first()
        if existe:
            return
        entry = PlatformTokenBlacklist(jti=jti, username=username, motivo=motivo)
        db.add(entry)
        db.commit()

    @staticmethod
    def is_token_blacklisted(db: Session, jti: str) -> bool:
        return db.query(PlatformTokenBlacklist).filter(
            PlatformTokenBlacklist.jti == jti,
            PlatformTokenBlacklist.is_active == True,
        ).first() is not None

    @staticmethod
    def solicitar_reset(db: Session, email: str) -> str | None:
        user = db.query(PlatformUser).filter(PlatformUser.email == email).first()
        if not user:
            return None
        import secrets
        from datetime import datetime
        from platformcore.security import hash_password
        token = secrets.token_urlsafe(32)
        # Token expira en 1 hora
        expires = datetime.now() + timedelta(hours=1)
        reset = PlatformPasswordResetToken(
            user_id=user.id,
            token_hash=hash_password(token),
            expires_at=expires,
        )
        db.add(reset)
        db.commit()
        return token

    @staticmethod
    def resetear_password(db: Session, token: str, nueva_password: str) -> bool:
        from datetime import datetime
        now = datetime.now()
        resets = db.query(PlatformPasswordResetToken).filter(
            PlatformPasswordResetToken.used == False,
            PlatformPasswordResetToken.expires_at > now,
        ).all()
        from platformcore.security import verify_password, hash_password
        for r in resets:
            if verify_password(token, r.token_hash):
                user = db.query(PlatformUser).filter(PlatformUser.id == r.user_id).first()
                if user:
                    user.password_hash = hash_password(nueva_password)
                    r.used = True
                    db.commit()
                    return True
        return False
