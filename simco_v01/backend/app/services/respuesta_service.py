from sqlalchemy.orm import Session
from app.models.respuesta import Respuesta
from datetime import datetime
from app.models.solicitud import Solicitud
from app.core.audit import audit_action


def responder_solicitud(db: Session, data, user_id: int, archivo_nombre: str | None = None):

    solicitud = db.query(Solicitud).filter(Solicitud.id == data.solicitud_id).first()

    if not solicitud:
        return None

    # Crear respuesta
    respuesta = Respuesta(
        solicitud_id=data.solicitud_id,
        usuario_responde_id=user_id,
        estado_documento=data.estado_documento,
        observacion=data.observacion,
        archivo_nombre=archivo_nombre,
        detalle=data.detalle,
        fecha_respuesta=datetime.utcnow()
    )

    db.add(respuesta)
    db.flush()  # 👈 importante para obtener ID antes del commit

    # Auditoría (UNA SOLA VEZ)
    audit_action(
        db,
        user_id,
        "RESPONDER_SOLICITUD",
        "respuesta",
        respuesta.id,
        f"Solicitud {data.solicitud_id} respondida"
    )

    # Cambiar estado de la solicitud
    solicitud.estado = "respondida"

    db.commit()
    db.refresh(respuesta)

    return respuesta