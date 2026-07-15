from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.db.base import Base


class Respuesta(Base):
    __tablename__ = "respuestas"

    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"))

    usuario_responde_id = Column(Integer, ForeignKey("users.id"))

    estado_documento = Column(String)  # existe / no_existe / retirado / no_localizado
    observacion = Column(String)

    archivo_nombre = Column(String, nullable=True)
    
    detalle = Column(String)

    fecha_respuesta = Column(DateTime, default=datetime.utcnow)