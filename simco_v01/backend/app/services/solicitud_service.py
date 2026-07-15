from sqlalchemy.orm import Session
from app.models.solicitud import Solicitud
from datetime import datetime

from app.core.audit import audit_action


def crear_solicitud(db: Session, data, user_id: int, archivo_nombre: str | None = None):

    nueva = Solicitud(
        codigo=f"SOL-{int(datetime.utcnow().timestamp())}",
        tipo_documento=data.tipo_documento,
        identificador_documento=data.identificador_documento,
        detalle=data.detalle,
        prioridad=data.prioridad,
        archivo_nombre=archivo_nombre,
        creado_por_usuario_id=user_id,
        estado="pendiente"
    )

    db.add(nueva)
    db.flush()   # 👈 NECESARIO para obtener ID antes del commit

    # 🔥 Auditoría (UNA SOLA VEZ)
    audit_action(
        db,
        user_id,
        "CREAR_SOLICITUD",
        "solicitud",
        nueva.id,
        codigo=nueva.codigo
    )

    db.commit()
    db.refresh(nueva)

    return nueva