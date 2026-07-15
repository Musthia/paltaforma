from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from platformcore.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from platformcore.models import identity, security, audit
    Base.metadata.create_all(bind=engine)
