from platformcore.services.audit import AuditService
from platformcore.database import SessionLocal


def audit_action(db, user_id, action, entity, entity_id, codigo="", detail=""):
    AuditService.record(
        db=db,
        user_id=user_id,
        username=str(user_id),
        action=action,
        entity=entity,
        entity_id=entity_id,
        detail=detail or codigo,
        module="simco",
    )
