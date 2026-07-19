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

    import os
    db = SessionLocal()
    try:
        admin_username = os.getenv("ADMIN_USERNAME") or os.getenv("SUPERUSER_USERNAME") or "Musthia"
        admin_password = os.getenv("ADMIN_PASSWORD") or os.getenv("SUPERUSER_PASSWORD") or "0611"
        admin_name = os.getenv("ADMIN_FULLNAME") or "Super Administrador"

        existing = db.query(identity.PlatformUser).filter(
            identity.PlatformUser.username == admin_username
        ).first()
        if not existing:
            from platformcore.security import hash_password
            superuser = identity.PlatformUser(
                username=admin_username,
                password_hash=hash_password(admin_password),
                full_name=admin_name,
                role="admin",
                nivel_seguridad=10,
                is_superuser=True,
                is_active=True,
            )
            db.add(superuser)
            db.commit()
            print(f"[PLATFORM] Superusuario '{admin_username}' creado.")
        else:
            print(f"[PLATFORM] Superusuario '{admin_username}' ya existe.")
    except Exception as e:
        db.rollback()
        print(f"[PLATFORM] WARN: No se pudo crear superusuario por defecto: {e}")
    finally:
        db.close()
