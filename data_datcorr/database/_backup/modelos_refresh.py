from sqlalchemy import (

    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    text
)

from database.conexion import Base

# -----------------------------------
# REFRESH TOKENS
# -----------------------------------

class RefreshToken(Base):

    __tablename__ = "refresh_tokens"

    id = Column(

        Integer,

        primary_key=True,

        index=True
    )

    usuario_id = Column(

        Integer,

        ForeignKey("usuarios.id"),

        nullable=False
    )

    token_jti = Column(

        String(255),

        nullable=False
    )

    refresh_token = Column(

        String,

        nullable=False
    )

    revoked = Column(

        Boolean,

        default=False
    )

    ip_address = Column(
        String(100)
    )

    user_agent = Column(
        String(500)
    )

    expires_at = Column(
        TIMESTAMP,
        nullable=False
    )

    last_activity = Column(
        TIMESTAMP,
        nullable=True
    )

    access_jti = Column(
        String(255),
        nullable=True
    )

    created_at = Column(

        TIMESTAMP,

        server_default=text(
            "CURRENT_TIMESTAMP"
        )
    )