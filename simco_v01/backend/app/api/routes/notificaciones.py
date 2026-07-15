from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.core.deps import get_current_user
from app.models.solicitud import Solicitud
from app.models.user import User

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("/nuevas")
def nuevas_notificaciones(
    tipo: str = Query(...),
    desde_id: int = Query(0),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if tipo not in ("pendiente", "respondida"):
        return {"count": 0, "items": []}

    estado = tipo

    rows = (
        db.query(Solicitud, User.username)
        .outerjoin(User, User.id == Solicitud.creado_por_usuario_id)
        .filter(Solicitud.estado == estado, Solicitud.id > desde_id)
        .order_by(Solicitud.id.asc())
        .all()
    )

    items = []
    for s, nombre in rows:
        d = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        d["creado_por_nombre"] = nombre or f"usuario {s.creado_por_usuario_id}"
        items.append(d)

    return {
        "count": len(items),
        "max_id": max((s.id for s, _ in rows), default=0),
        "items": items,
    }
