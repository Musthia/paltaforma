from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.db.base import Base


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True)

    tipo_documento = Column(String)  # expediente / legajo / caja / paquete
    identificador_documento = Column(String)

    detalle = Column(String)
    estado = Column(String, default="pendiente")  # pendiente / en_proceso / respondida / cancelada
    prioridad = Column(String, default="media")

    destacado = Column(Boolean, default=False)
    verificado = Column(Boolean, default=False)

    archivo_nombre = Column(String, nullable=True)

    creado_por_usuario_id = Column(Integer, ForeignKey("users.id"))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)