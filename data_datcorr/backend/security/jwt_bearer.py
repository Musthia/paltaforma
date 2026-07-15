from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from platformcore.dependencies import get_current_user as platform_get_current_user
from platformcore.database import get_db

security = HTTPBearer()


def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    from platformcore.database import SessionLocal
    db = SessionLocal()
    try:
        user = platform_get_current_user(credentials, db)
        return user
    finally:
        db.close()
