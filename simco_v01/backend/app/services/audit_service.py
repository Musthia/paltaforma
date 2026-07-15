from platformcore.services.audit import AuditService


def registrar_auditoria(db, usuario_id: int, accion: str, codigo: str,
                        entidad: str, entidad_id: int, detalle: str = ""):
    AuditService.record(
        db=db,
        user_id=usuario_id,
        action=accion,
        entity=entidad,
        entity_id=entidad_id,
        detail=detalle or codigo,
        module="simco",
    )
