from sqlalchemy import (
    Column, Integer, String, TIMESTAMP,
    ForeignKey, text
)

from database.conexion import Base


class Rol(Base):

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(
        String(50), unique=True, nullable=False
    )

    descripcion = Column(
        String(255), nullable=True
    )

    nivel_minimo = Column(
        Integer, default=1
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )


class UsuarioRol(Base):

    __tablename__ = "usuarios_roles"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    rol_id = Column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
