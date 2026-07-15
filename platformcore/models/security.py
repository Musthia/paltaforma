from sqlalchemy import (
    Column, Integer, String, ForeignKey, TIMESTAMP, text,
)
from sqlalchemy.orm import relationship

from platformcore.database import Base
from platformcore.models.identity import PlatformUser


class PlatformRole(Base):
    __tablename__ = "platform_roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    nivel_minimo = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class PlatformPermission(Base):
    __tablename__ = "platform_permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    module = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class PlatformUserRole(Base):
    __tablename__ = "platform_user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("platform_users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("platform_roles.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("PlatformUser", back_populates="roles")
    role = relationship("PlatformRole")


class PlatformUserPermission(Base):
    __tablename__ = "platform_user_permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("platform_users.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("platform_permissions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("PlatformUser", back_populates="permissions")
    permission = relationship("PlatformPermission")
