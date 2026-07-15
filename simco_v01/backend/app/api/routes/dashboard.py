from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.db.dependencies import get_db
from app.models.solicitud import Solicitud
from app.models.user import User

from app.models.audit import AuditLog

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/hoy")
def actividad_hoy(db: Session = Depends(get_db)):

    hoy = date.today()

    rows = (
        db.query(Solicitud, User.username)
        .outerjoin(User, User.id == Solicitud.creado_por_usuario_id)
        .filter(Solicitud.fecha_creacion >= hoy)
        .order_by(Solicitud.id.desc())
        .limit(50)
        .all()
    )

    result = []
    for s, nombre in rows:
        d = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        d["creado_por_nombre"] = nombre or f"usuario {s.creado_por_usuario_id}"
        result.append(d)
    return result

@router.get("/activity")
def actividad_sistema(db: Session = Depends(get_db)):

    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.fecha.desc())
        .limit(50)
        .all()
    )

    return logs