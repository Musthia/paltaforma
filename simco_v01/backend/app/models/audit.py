from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(Integer)
    accion = Column(String)  # CREATE_SOLICITUD / RESPONDER / LOGIN / etc
    codigo = Column(String) 
    entidad = Column(String)  # solicitud / respuesta
    entidad_id = Column(Integer)

    detalle = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)