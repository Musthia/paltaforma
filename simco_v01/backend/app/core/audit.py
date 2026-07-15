from app.services.audit_service import registrar_auditoria


def audit_action(db, user_id, action, entity, entity_id, codigo="", detail=""):
    registrar_auditoria(
        db=db,
        usuario_id=user_id,
        accion=action,
        codigo=codigo,
        entidad=entity,
        entidad_id=entity_id,
        detalle=detail
    )