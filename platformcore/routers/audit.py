from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from platformcore.database import get_db
from platformcore.dependencies import require_role
from platformcore.services.audit import AuditService
from platformcore.models.identity import PlatformUser

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/")
def list_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    action: str = None,
    entity: str = None,
    username: str = None,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin", "Administrador")),
):
    return AuditService.list_logs(
        db=db, page=page, limit=limit,
        action=action, entity=entity, username=username,
    )

