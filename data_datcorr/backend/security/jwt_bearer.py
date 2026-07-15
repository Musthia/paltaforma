from fastapi import (
    Depends,
    HTTPException
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from backend.security.jwt_manager import (
    verificar_token
)

from database.conexion import SessionLocal

from database.modelos import Usuario

security = HTTPBearer()

# -----------------------------------
# OBTENER USUARIO ACTUAL
# -----------------------------------

def obtener_usuario_actual(

    credentials:
    HTTPAuthorizationCredentials = Depends(
        security
    )

):

    token = credentials.credentials

    payload = verificar_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Token inválido."
        )

    username = payload.get("sub")

    if not username:

        raise HTTPException(
            status_code=401,
            detail="Token inválido."
        )

    session = SessionLocal()

    try:

        usuario_db = (
            session.query(Usuario)
            .filter(
                Usuario.usuario == username
            )
            .first()
        )

        if not usuario_db:

            raise HTTPException(
                status_code=401,
                detail="Usuario inexistente."
            )

        if not usuario_db.activo:

            raise HTTPException(
                status_code=403,
                detail="Usuario inactivo."
            )

        return usuario_db

    finally:

        session.close()