from sqlalchemy.orm import Session

from platformcore.models.identity import PlatformTokenBlacklist
from platformcore.database import SessionLocal


def blacklist_token(
    db: Session,
    jti: str,
    usuario: str,
    motivo: str = "logout",
):
    existe = db.query(PlatformTokenBlacklist).filter(
        PlatformTokenBlacklist.jti == jti
    ).first()
    if existe:
        return
    token = PlatformTokenBlacklist(
        jti=jti,
        username=usuario,
        motivo=motivo,
        is_active=True,
    )
    db.add(token)
    db.commit()


def token_esta_revocado(
    db: Session,
    jti: str,
):
    token = db.query(PlatformTokenBlacklist).filter(
        PlatformTokenBlacklist.jti == jti,
        PlatformTokenBlacklist.is_active == True,
    ).first()
    return token is not None
