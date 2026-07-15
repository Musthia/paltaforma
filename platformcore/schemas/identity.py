from datetime import datetime
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    email: str | None = None
    role: str
    nivel_seguridad: int = 1
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    success: bool
    mensaje: str
    user: UserOut | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    jti: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    success: bool
    access_token: str | None = None
    refresh_token: str | None = None
    mensaje: str | None = None


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class LogoutResponse(BaseModel):
    success: bool
    mensaje: str


class MeResponse(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    email: str | None = None
    role: str
    nivel_seguridad: int
    is_superuser: bool
    permissions: list[str] = []

    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UserCreateRequest(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    email: str | None = None
    role: str = "consulta"
    nivel_seguridad: int = 1
    is_active: bool = True
    is_superuser: bool = False


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    email: str | None = None
    role: str | None = None
    nivel_seguridad: int | None = None
    is_active: bool | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    email: str | None = None
    role: str
    nivel_seguridad: int
    is_active: bool
    is_superuser: bool
    last_login: datetime | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
