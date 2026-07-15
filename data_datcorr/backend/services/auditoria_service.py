from sqlalchemy.orm import Session

from platformcore.services.audit import AuditService


def registrar_auditoria(
    db: Session,
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
    AuditService.record(
        db=db,
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
