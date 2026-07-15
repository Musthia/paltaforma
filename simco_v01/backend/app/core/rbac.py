from fastapi import HTTPException


def require_roles(*allowed_roles):
    def wrapper(user):
        if user.role not in allowed_roles and not getattr(user, "is_superuser", False):
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para esta acción",
            )
        return user
    return wrapper
