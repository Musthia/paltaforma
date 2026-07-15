from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, DateTime, func

from platformcore.database import Base


class PlatformAuditLog(Base):
    __tablename__ = "platform_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=True)
    entity_id = Column(Integer, nullable=True)
    module = Column(String(50), nullable=True)
    detail = Column(Text, nullable=True)
    ip_address = Column(String(100), nullable=True)
    user_agent = Column(String(500), nullable=True)
    token_jti = Column(String(255), nullable=True)
    endpoint = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
