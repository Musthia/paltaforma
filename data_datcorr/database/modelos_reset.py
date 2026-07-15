from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP,
    ForeignKey, text
)

from database.conexion import Base


class PasswordResetToken(Base):

    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    token_hash = Column(
        String(255),
        nullable=False
    )

    expires_at = Column(
        TIMESTAMP,
        nullable=False
    )

    usado = Column(
        Boolean,
        default=False
    )

    ip_solicitud = Column(
        String(100)
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
