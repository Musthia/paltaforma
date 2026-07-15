from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from datetime import datetime


def registrar_auditoria(db: Session, usuario_id: int, accion: str, codigo: str,
                        entidad: str, entidad_id: int, detalle: str = ""):

    log = AuditLog(
        usuario_id=usuario_id,
        accion=accion,
        codigo=codigo,
        entidad=entidad,
        entidad_id=entidad_id,
        detalle=detalle,
        fecha=datetime.utcnow()
    )

    db.add(log)
    db.commit()