from platformcore.services.audit import AuditService
from platformcore.database import SessionLocal as PlatformSessionLocal


def registrar_auditoria(
    db=None,
    usuario: str = "",
    accion: str = "",
    tabla: str = "",
    registro_id: int = None,
    endpoint: str = "",
    ip: str = "",
    detalle: str = "",
    ip_address=None,
    user_agent=None,
    token_jti=None,
):
    session = PlatformSessionLocal()
    try:
        AuditService.record(
            db=session,
            username=usuario,
            action=accion,
            entity=tabla,
            entity_id=registro_id,
            endpoint=endpoint,
            detail=detalle,
            ip_address=ip_address or ip,
            user_agent=user_agent,
            token_jti=token_jti,
            module="datcorr",
        )
    finally:
        session.close()
