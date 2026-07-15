from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from platformcore.database import get_db
from platformcore.jwt import verify_access_token
from platformcore.exceptions import AuthError, PermissionDenied
from platformcore.models.identity import PlatformUser
from platformcore.models.security import PlatformUserPermission, PlatformPermission
from platformcore.services.audit import AuditService

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    username = payload.get("sub")
    jti = payload.get("jti")

    # verificar blacklist
    from platformcore.services.identity import IdentityService
    if jti and IdentityService.is_token_blacklisted(db, jti):
        AuditService.record(
            db=db, username=username, action="TOKEN_REVOKED_ACCESS",
            entity="auth", detail="Acceso bloqueado: token en blacklist",
            token_jti=jti,
        )
        raise HTTPException(status_code=401, detail="Token revocado.")

    user = db.query(PlatformUser).filter(PlatformUser.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario inexistente.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo.")

    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
):
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, db)
    except Exception:
        return None


def require_permission(permission_code: str):
    def wrapper(user: PlatformUser = Depends(get_current_user), db: Session = Depends(get_db)):
        if user.is_superuser:
            return user
        has_perm = (
            db.query(PlatformUserPermission)
            .join(PlatformPermission)
            .filter(
                PlatformUserPermission.user_id == user.id,
                PlatformPermission.code == permission_code,
            )
            .first()
        )
        if not has_perm:
            raise HTTPException(status_code=403, detail=f"Permiso denegado: {permission_code}")
        return user
    return wrapper


def require_role(*allowed_roles: str):
    def wrapper(user: PlatformUser = Depends(get_current_user)):
        if user.role not in allowed_roles and not user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail=f"Se requiere uno de estos roles: {', '.join(allowed_roles)}",
            )
        return user
    return wrapper
