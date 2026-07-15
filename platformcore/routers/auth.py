from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt

from platformcore.database import get_db
from platformcore.config import settings
from platformcore.schemas.identity import (
    LoginRequest, LoginResponse, RefreshRequest, LogoutRequest, LogoutResponse,
    MeResponse, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
)
from platformcore.services.identity import IdentityService
from platformcore.services.audit import AuditService
from platformcore.services.security import PermissionService
from platformcore.dependencies import get_current_user
from platformcore.models.identity import PlatformUser
from platformcore.jwt import decode_token_payload
from platformcore.security import verify_password, hash_password

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
def login(
    request: Request,
    datos: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    ip_address = request.client.host if request.client else ""
    user_agent = request.headers.get("user-agent", "")

    result = IdentityService.login(db, datos.username, datos.password, ip_address, user_agent)

    if not result["success"]:
        AuditService.record(
            db=db, username=datos.username, action="LOGIN_FAILED",
            entity="auth", detail=result["mensaje"],
            ip_address=ip_address, user_agent=user_agent,
        )
        raise HTTPException(status_code=401, detail=result["mensaje"])

    AuditService.record(
        db=db, username=datos.username, action="LOGIN_SUCCESS",
        entity="auth", entity_id=result["user"]["id"],
        detail="Login exitoso", ip_address=ip_address,
        user_agent=user_agent, token_jti=result.get("jti"),
    )

    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return LoginResponse(
        success=True,
        mensaje=result["mensaje"],
        user=result["user"],
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        jti=result.get("jti"),
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    datos: LogoutRequest = None,
    db: Session = Depends(get_db),
):
    refresh_token_str = request.cookies.get("refresh_token") or (
        datos.refresh_token if datos else None
    )
    if not refresh_token_str:
        raise HTTPException(status_code=401, detail="Refresh token requerido.")

    result = IdentityService.logout(db, refresh_token_str)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["mensaje"])

    # blacklist access token JTI
    access_token = credentials.credentials
    payload = decode_token_payload(access_token)
    if payload:
        jti = payload.get("jti")
        username = payload.get("sub")
        if jti:
            IdentityService.blacklist_jti(db, jti, username, motivo="logout")

    response.delete_cookie("refresh_token", path="/")
    return LogoutResponse(success=True, mensaje="Logout correcto.")


@router.post("/refresh")
def refresh(
    datos: RefreshRequest,
    db: Session = Depends(get_db),
):
    result = IdentityService.refresh(db, datos.refresh_token)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["mensaje"])
    return result


@router.get("/me", response_model=MeResponse)
def me(
    user: PlatformUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    permissions = PermissionService.get_user_permissions(db, user.id)
    return MeResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        nivel_seguridad=user.nivel_seguridad,
        is_superuser=user.is_superuser,
        permissions=permissions,
    )


@router.post("/forgot-password")
def forgot_password(
    body: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    import os
    token = IdentityService.solicitar_reset(db, body.email)
    if token:
        frontend_url = os.getenv("FRONTEND_URL", str(request.base_url).rstrip("/"))
        enlace = f"{frontend_url}/reset-password?token={token}"
        try:
            from platformcore.services.identity import IdentityService
            # enviar email (SMTP config en settings)
            import smtplib
            from email.mime.text import MIMEText
            if settings.SMTP_HOST:
                msg = MIMEText(f"Haz clic para restablecer: {enlace}")
                msg["Subject"] = "Restablecimiento de contraseña"
                msg["From"] = settings.SMTP_USER
                msg["To"] = body.email
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASS)
                    server.send_message(msg)
        except Exception:
            pass
    return {"success": True, "mensaje": "Si el correo existe, recibirá instrucciones."}


@router.post("/reset-password")
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    ok = IdentityService.resetear_password(db, body.token, body.new_password)
    if not ok:
        raise HTTPException(400, "Token inválido o expirado.")
    return {"success": True, "mensaje": "Contraseña actualizada correctamente."}


@router.patch("/change-password")
def change_password(
    body: ChangePasswordRequest,
    user: PlatformUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(400, "La contraseña actual no es correcta.")
    from datetime import datetime, timezone
    user.password_hash = hash_password(body.new_password)
    user.last_password_change = datetime.now(timezone.utc)
    db.commit()
    return {"success": True, "mensaje": "Contraseña cambiada correctamente."}
