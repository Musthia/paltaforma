from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password
from app.core.audit import audit_action

MASTER_USERNAME = "Musthia"


def list_users(db: Session):
    return db.query(User).filter(User.username != MASTER_USERNAME).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, data, current_user_id: int):
    user = User(
        username=data.username,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=data.role,
        is_active=True,
    )
    db.add(user)
    db.flush()

    audit_action(db, current_user_id, "CREAR_USUARIO", "user", user.id,
                 codigo=data.username, detail=f"Usuario {data.username} creado con rol {data.role}")
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data, current_user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    if user.username == MASTER_USERNAME:
        return None

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password:
        user.hashed_password = hash_password(data.password)

    db.flush()
    audit_action(db, current_user_id, "ACTUALIZAR_USUARIO", "user", user.id,
                 codigo=user.username, detail=f"Usuario {user.username} actualizado")
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, current_user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    if user.username == MASTER_USERNAME:
        return False

    audit_action(db, current_user_id, "ELIMINAR_USUARIO", "user", user.id,
                 codigo=user.username, detail=f"Usuario {user.username} eliminado")
    db.delete(user)
    db.commit()
    return True
