from fastapi import (

    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response
)

from sqlalchemy.orm import Session

from datetime import datetime, timezone

from backend.database.conexion import (
    get_db
)

from backend.services.password_reset_service import (
    solicitar_reset,
    resetear_password,
    enviar_email_reset,
)

from utils.hash import verificar_password, hash_password

from backend.schemas.auth_schema import (

    LoginRequest,
    LoginResponse,

    LogoutRequest,
    LogoutResponse,
    MeResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)

from database.modelos import (
    Permiso,
    UsuarioPermiso
)

from backend.services.auth_service import (
    login_usuario,
    logout_usuario
)

from backend.services.auditoria_service import (
    registrar_auditoria
)

from backend.schemas.refresh_schema import (

    RefreshRequest,

    RefreshResponse
)

from backend.services.auth_service import (

    refresh_access_token
)

from jose import jwt

from backend.services.blacklist_service import (
    blacklist_token
)

from backend.security.jwt_manager import (
    SECRET_KEY,
    ALGORITHM,
)

from backend.security.jwt_bearer import (
    obtener_usuario_actual
)

from backend.security.jwt_manager import set_refresh_cookie, clear_refresh_cookie

from backend.schemas.usuario_schema import (
    UsuarioResponse
)

from fastapi.security import (

    HTTPBearer,

    HTTPAuthorizationCredentials
)

security = HTTPBearer()

router = APIRouter(

    prefix="/auth",

    tags=["Auth"]
)

# -----------------------------------
# LOGIN
# -----------------------------------

@router.post(

    "/login",

    response_model=LoginResponse
)

def login(

    request: Request,

    datos: LoginRequest,

    response: Response,

    db: Session = Depends(get_db)
):

    # -----------------------------------
    # IP CLIENTE
    # -----------------------------------

    ip_address = request.client.host

    # -----------------------------------
    # USER AGENT
    # -----------------------------------

    user_agent = request.headers.get(
        "user-agent"
    )

    # -----------------------------------
    # LOGIN
    # -----------------------------------

    resultado = login_usuario(

        datos.usuario,

        datos.password
    )

    #print("LOGIN RESULTADO:")
    #print(resultado)

    # -----------------------------------
    # LOGIN FALLIDO
    # -----------------------------------

    if not resultado["success"]:

        registrar_auditoria(

            db=db,

            usuario=datos.usuario,

            accion="LOGIN_FAILED",

            tabla="auth",

            registro_id=0,

            detalle=resultado["mensaje"],

            ip_address=ip_address,

            user_agent=user_agent
        )

        raise HTTPException(

            status_code=401,

            detail=resultado["mensaje"]
        )

    # -----------------------------------
    # TOKEN + JTI
    # -----------------------------------

    token = resultado["token"]

    jti = resultado.get("jti")

    # -----------------------------------
    # LOGIN EXITOSO
    # -----------------------------------

    registrar_auditoria(

        db=db,
    
        usuario=resultado["usuario"]["usuario"],
    
        accion="LOGIN_SUCCESS",
    
        tabla="auth",
    
        registro_id=resultado["usuario"]["id"],
    
        detalle="Login exitoso",
    
        ip_address=ip_address,
    
        user_agent=user_agent,
    
        token_jti=jti
    )

    # -----------------------------------
    # RESPONSE
    # -----------------------------------

    set_refresh_cookie(response, resultado["refresh_token"])

    return LoginResponse(

        success=True,

        mensaje=resultado["mensaje"],

        usuario=resultado["usuario"],

        token=resultado["token"],

        refresh_token=resultado[
            "refresh_token"
        ]
    )

# -----------------------------------
# LOGOUT
# -----------------------------------

@router.post(

    "/logout",

    response_model=LogoutResponse
)

def logout(

    request: Request,

    response: Response,

    credentials: HTTPAuthorizationCredentials = Depends(security),

    datos: LogoutRequest = None,

    db: Session = Depends(get_db)
):
    refresh_token_str = request.cookies.get("refresh_token") or (datos.refresh_token if datos else None)

    if not refresh_token_str:
        raise HTTPException(status_code=401, detail="Refresh token requerido.")

    resultado = logout_usuario(

        db=db,

        refresh_token=refresh_token_str
    )

    # -----------------------------------
    # ERROR
    # -----------------------------------

    if not resultado["success"]:

        raise HTTPException(

            status_code=401,

            detail=resultado["mensaje"]
        )

    # -----------------------------------
    # ACCESS TOKEN
    # -----------------------------------

    access_token = credentials.credentials

    payload = jwt.decode(

        access_token,

        SECRET_KEY,

        algorithms=[ALGORITHM]
    )

    jti = payload.get("jti")

    usuario = payload.get("sub")

    # -----------------------------------
    # BLACKLIST ACCESS TOKEN
    # -----------------------------------

    if jti:

        blacklist_token(

            db=db,

            jti=jti,

            usuario=usuario,

            motivo="logout"
        )

    # -----------------------------------
    # OK
    # -----------------------------------

    clear_refresh_cookie(response)

    return LogoutResponse(

        success=True,

        mensaje=resultado["mensaje"]
    )


# -----------------------------------
# GET /auth/me
# -----------------------------------

@router.get(
    "/me",
    response_model=MeResponse
)
def get_current_user(
    usuario_actual=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db)
):
    permisos_db = (
        db.query(Permiso.codigo)
        .join(UsuarioPermiso, UsuarioPermiso.permiso_id == Permiso.id)
        .filter(UsuarioPermiso.usuario_id == usuario_actual.id)
        .all()
    )
    permisos = [p[0] for p in permisos_db]

    return MeResponse(
        id=usuario_actual.id,
        usuario=usuario_actual.usuario,
        nombre=usuario_actual.nombre,
        apellido=usuario_actual.apellido,
        email=usuario_actual.email,
        rol=usuario_actual.rol,
        nivel_seguridad=usuario_actual.nivel_seguridad,
        es_superusuario=usuario_actual.es_superusuario,
        permisos=permisos
    )


# -----------------------------------
# POST /auth/forgot-password
# -----------------------------------

@router.post("/forgot-password")
def forgot_password(
    body: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else None
    import os
    token = solicitar_reset(db, body.email, ip)
    if token:
        frontend_url = os.getenv("FRONTEND_URL", str(request.base_url).rstrip("/"))
        enlace = f"{frontend_url}/reset-password?token={token}"
        try:
            enviar_email_reset(body.email, enlace)
        except Exception:
            pass
    return {"success": True, "mensaje": "Si el correo existe, recibirá instrucciones."}


# -----------------------------------
# POST /auth/reset-password
# -----------------------------------

@router.post("/reset-password")
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    ok = resetear_password(db, body.token, body.nueva_password)
    if not ok:
        raise HTTPException(400, "Token inválido o expirado.")
    return {"success": True, "mensaje": "Contraseña actualizada correctamente."}


# -----------------------------------
# PATCH /auth/change-password
# -----------------------------------

@router.patch("/change-password")
def change_password(
    body: ChangePasswordRequest,
    usuario_actual=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    if not verificar_password(body.actual, usuario_actual.password_hash):
        raise HTTPException(400, "La contraseña actual no es correcta.")
    usuario_actual.password_hash = hash_password(body.nueva)
    usuario_actual.ultimo_cambio_password = datetime.now(timezone.utc)
    db.commit()
    return {"success": True, "mensaje": "Contraseña cambiada correctamente."}