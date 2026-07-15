from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password
from app.core.jwt import create_access_token, create_refresh_token


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def generate_tokens(user: User):
    payload = {
        "sub": str(user.id),
        "id": user.id,
        "role": user.role,
        "username": user.username,
        "full_name": user.full_name,
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }