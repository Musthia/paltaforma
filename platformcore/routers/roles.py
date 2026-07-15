from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from platformcore.database import get_db
from platformcore.dependencies import require_role
from platformcore.services.security import RoleService
from platformcore.models.identity import PlatformUser

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/")
def list_roles(
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_role("admin")),
):
    roles = RoleService.list_roles(db)
    return [{"id": r.id, "name": r.name, "description": r.description, "nivel_minimo": r.nivel_minimo} for r in roles]
