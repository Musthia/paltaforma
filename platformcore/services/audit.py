from sqlalchemy.orm import Session

from platformcore.logger import logger
from platformcore.models.audit import PlatformAuditLog


class AuditService:

    @staticmethod
    def record(
        db: Session,
        user_id: int | None = None,
        username: str | None = None,
        action: str = "",
        entity: str | None = None,
        entity_id: int | None = None,
        module: str | None = None,
        detail: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        token_jti: str | None = None,
        endpoint: str | None = None,
    ):
        log = PlatformAuditLog(
            user_id=user_id,
            username=username,
            action=action,
            entity=entity,
            entity_id=entity_id,
            module=module,
            detail=detail,
            ip_address=ip_address,
            user_agent=user_agent,
            token_jti=token_jti,
            endpoint=endpoint,
        )
        db.add(log)
        db.commit()
        logger.info(f"AUDIT: {action} | entity={entity} id={entity_id} user={username}")

    @staticmethod
    def list_logs(
        db: Session,
        page: int = 1,
        limit: int = 50,
        action: str | None = None,
        entity: str | None = None,
        username: str | None = None,
    ):
        query = db.query(PlatformAuditLog)

        if action:
            query = query.filter(PlatformAuditLog.action == action)
        if entity:
            query = query.filter(PlatformAuditLog.entity == entity)
        if username:
            query = query.filter(PlatformAuditLog.username.ilike(f"%{username}%"))

        query = query.order_by(PlatformAuditLog.id.desc())

        total = query.count()
        pages = max(1, (total + limit - 1) // limit)
        offset = (page - 1) * limit
        logs = query.offset(offset).limit(limit).all()

        return {"logs": logs, "total": total, "pages": pages, "page": page, "limit": limit}
