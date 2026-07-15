from sqlalchemy import (

    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    DateTime,
    text
)

from sqlalchemy.sql import func

from database.conexion import Base

# -----------------------------------
# AUDITORIA
# -----------------------------------

class Auditoria(Base):

    __tablename__ = "auditoria"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    usuario = Column(
        String,
        nullable=True
    )

    accion = Column(
        String,
        nullable=False
    )

    tabla = Column(
        String,
        nullable=False
    )

    registro_id = Column(
        Integer,
        nullable=True
    )

    endpoint = Column(
        String,
        nullable=True
    )

    ip = Column(
        String,
        nullable=True
    )

    detalle = Column(
        Text,
        nullable=True
    )

    # -----------------------------------
    # IP CLIENTE
    # -----------------------------------

    ip_address = Column(
        String(100),
        nullable=True
    )

    # -----------------------------------
    # USER AGENT
    # -----------------------------------

    user_agent = Column(
        String(500),
        nullable=True
    )

    # -----------------------------------
    # JWT TOKEN ID
    # -----------------------------------

    token_jti = Column(
        String(255),
        nullable=True
    )

    fecha = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )