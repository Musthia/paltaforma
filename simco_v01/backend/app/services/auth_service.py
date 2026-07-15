from platformcore.services.identity import IdentityService


def authenticate_user(db, username: str, password: str):
    result = IdentityService.login(db, username, password)
    if result["success"]:
        return result["user"]
    return None


def generate_tokens(user):
    from platformcore.jwt import create_access_token, create_refresh_token
    payload = {
        "sub": user.username,
        "user_id": user.id,
        "role": user.role,
        "username": user.username,
        "full_name": getattr(user, "full_name", ""),
    }
    access = create_access_token(payload)
    refresh = create_refresh_token(payload)
    return {
        "access_token": access["access_token"],
        "refresh_token": refresh["refresh_token"],
    }
