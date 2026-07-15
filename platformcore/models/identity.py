from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey, text,
)
from sqlalchemy.orm import relationship

from platformcore.database import Base


class PlatformUser(Base):
    __tablename__ = "platform_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    full_name = Column(String(200), nullable=True)
    password_hash = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False, default="consulta")
    nivel_seguridad = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    last_login = Column(TIMESTAMP, nullable=True)
    last_password_change = Column(TIMESTAMP, nullable=True)
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    roles = relationship("PlatformUserRole", back_populates="user", cascade="all, delete-orphan")
    permissions = relationship("PlatformUserPermission", back_populates="user", cascade="all, delete-orphan")


class PlatformRefreshToken(Base):
    __tablename__ = "platform_refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("platform_users.id"), nullable=False)
    token_jti = Column(String(255), nullable=False, index=True)
    refresh_token = Column(Text, nullable=False)
    revoked = Column(Boolean, default=False)
    ip_address = Column(String(100), nullable=True)
    user_agent = Column(String(500), nullable=True)
    expires_at = Column(TIMESTAMP, nullable=False)
    last_activity = Column(TIMESTAMP, nullable=True)
    access_jti = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class PlatformTokenBlacklist(Base):
    __tablename__ = "platform_token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    motivo = Column(String(50), default="logout")
    revoked_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    is_active = Column(Boolean, default=True)


class PlatformPasswordResetToken(Base):
    __tablename__ = "platform_password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("platform_users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    used = Column(Boolean, default=False)
    ip_solicitud = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
