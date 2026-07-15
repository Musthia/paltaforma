from sqlalchemy.orm import declarative_base

Base = declarative_base()

# IMPORTANTE: importar modelos para que SQLAlchemy los registre

from app.models.solicitud import Solicitud
from app.models.respuesta import Respuesta
from app.models.audit import AuditLog
from app.models.message import Message