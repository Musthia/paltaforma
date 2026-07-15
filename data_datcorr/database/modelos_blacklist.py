from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean
)

from database.conexion import Base

from datetime import datetime

# -----------------------------------
# TOKEN BLACKLIST
# -----------------------------------

class TokenBlacklist(Base):

    __tablename__ = "token_blacklist"

    id = Column(

        Integer,

        primary_key=True,

        index=True
    )

    jti = Column(

        String,

        unique=True,

        nullable=False,

        index=True
    )

    usuario = Column(

        String,

        nullable=False
    )

    revoked_at = Column(

        DateTime,

        default=datetime.utcnow
    )

    motivo = Column(

        String,

        default="logout"
    )

    activo = Column(

        Boolean,

        default=True
    )