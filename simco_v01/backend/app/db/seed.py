import os
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.core.security import hash_password
from dotenv import load_dotenv

load_dotenv()

def create_admin():
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    fullname = os.getenv("ADMIN_FULLNAME")
    role = os.getenv("ADMIN_ROLE", "admin")

    # Verificar si ya existe
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print("Admin ya existe")
        return

    admin_user = User(
        username=username,
        full_name=fullname,
        hashed_password=hash_password(password),
        role=role,
        is_active=True
    )

    db.add(admin_user)
    db.commit()
    db.close()

    print("Usuario admin creado correctamente")

if __name__ == "__main__":
    create_admin()