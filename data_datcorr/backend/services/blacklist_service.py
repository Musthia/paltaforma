from sqlalchemy.orm import Session

from database.modelos_blacklist import (
    TokenBlacklist
)

# -----------------------------------
# AGREGAR TOKEN A BLACKLIST
# -----------------------------------

def blacklist_token(

    db: Session,

    jti: str,

    usuario: str,

    motivo: str = "logout"
):

    existe = (

        db.query(TokenBlacklist)

        .filter(
            TokenBlacklist.jti == jti
        )

        .first()
    )

    # -------------------------
    # EVITAR DUPLICADOS
    # -------------------------

    if existe:

        return

    token = TokenBlacklist(

        jti=jti,

        usuario=usuario,

        motivo=motivo,

        activo=True
    )

    db.add(token)

    db.commit()

# -----------------------------------
# VERIFICAR TOKEN BLACKLIST
# -----------------------------------

def token_esta_revocado(

    db: Session,

    jti: str
):

    token = (

        db.query(TokenBlacklist)

        .filter(
            TokenBlacklist.jti == jti
        )

        .filter(
            TokenBlacklist.activo == True
        )

        .first()
    )

    return token is not None