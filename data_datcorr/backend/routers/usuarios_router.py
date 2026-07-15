from backend.core.logger import logger

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Query,
    Response
)

from backend.schemas.usuario_schema import (
    UsuarioResponse,
    UsuarioCreate,
    UsuarioCreateResponse,
    UsuariosListadoResponse,
    UsuarioUpdate,
    UsuarioUpdateResponse
)

from backend.schemas.roles_schema import (
    RolResponse
)

from backend.services.usuarios_service import (
    listar_usuarios_web,
    crear_usuario_web,
    actualizar_usuario_web,
    desactivar_usuario_web,
    reactivar_usuario_web
)

from backend.security.jwt_bearer import (
    obtener_usuario_actual
)

from backend.security.jwt_manager import set_refresh_cookie

from backend.security.permissions import (
    requiere_permiso
)

from sqlalchemy.orm import Session

from backend.dependencies import (
    get_db
)

from database.conexion import (
    SessionLocal
)

from backend.core.exceptions import (
    DatcorrException
)

from typing import Optional

from backend.schemas.auth_schema import (
    LoginRequest,
    LoginResponse,
    RefreshResponse
)

from backend.schemas.auth_schema import (
    RefreshRequest,
    RefreshResponse
)

from backend.services.auth_service import (
    refresh_access_token
)

from backend.services.roles_service import (
    obtener_roles_usuario
)

from backend.security.permissions import (
    requiere_permiso,
    requiere_nivel
)

from backend.services.auditoria_service import (
    registrar_auditoria
)

# -----------------------------------
# DB SESSION
# -----------------------------------

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# -----------------------------------
# LISTAR USUARIOS
# -----------------------------------

@router.get(
    "/",
    response_model=UsuariosListadoResponse
)

def listar_usuarios(

    page: int = 1,

    limit: int = 20,

    search: str = "",

    rol: str = "",

    activo: Optional[bool] = None,

    usuario_actual = Depends(
        requiere_nivel(5)
    ),

    sort_by: str = Query(
        "id"
    ),

    order: str = Query(
        "asc"
    ),

    db: Session = Depends(
        get_db
    )
):


    logger.debug(
        "API WEB: listar usuarios"
    )

    resultado = listar_usuarios_web(

        db=db,

        page=page,

        limit=limit,

        search=search,

        rol=rol,

        activo=activo,

        sort_by=sort_by,

        order=order
    )

    usuarios_db = resultado[
        "usuarios"
    ]

    usuarios_response = []

    for usuario in usuarios_db:

        roles_usuario = obtener_roles_usuario(
            db, usuario.id
        )

        usuarios_response.append(

            UsuarioResponse(

                id=usuario.id,

                nombre=usuario.nombre,

                apellido=usuario.apellido,

                usuario=usuario.usuario,

                email=usuario.email,

                rol=usuario.rol,

                nivel_seguridad=(
                    usuario.nivel_seguridad
                ),

                activo=usuario.activo,

                es_superusuario=(
                    usuario.es_superusuario
                ),

                roles=[
                    RolResponse(
                        id=r.id,
                        nombre=r.nombre,
                        descripcion=r.descripcion,
                        nivel_minimo=r.nivel_minimo
                    )
                    for r in roles_usuario
                ]
            )
        )

    logger.debug(
        f"Usuarios serializados: "
        f"{len(usuarios_response)}"
    )

    registrar_auditoria(
        db=db,
        usuario=usuario_actual.usuario,
        accion="CONSULTA",
        tabla="usuarios",
        registro_id=None,
        detalle=(
            f"Listado de usuarios - "
            f"total={resultado['total']}, "
            f"page={resultado['page']}, "
            f"search='{search}', "
            f"rol='{rol}'"
        )
    )

    return UsuariosListadoResponse(

        success=True,

        total=resultado["total"],

        page=resultado["page"],

        limit=resultado["limit"],

        pages=resultado["pages"],

        usuarios=usuarios_response
    )

# -----------------------------------
# OBTENER USUARIO POR ID
# -----------------------------------

@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse
)

def obtener_usuario_por_id(

    usuario_id: int,

    usuario_actual = Depends(
        obtener_usuario_actual
    ),

    db: Session = Depends(
        get_db
    )
):

    logger.info(f"Obtener usuario ID={usuario_id}")

    from database.modelos import Usuario

    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado."
        )

    roles_usuario = obtener_roles_usuario(
        db, usuario.id
    )

    return UsuarioResponse(
        id=usuario.id,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        usuario=usuario.usuario,
        email=usuario.email,
        rol=usuario.rol,
        nivel_seguridad=usuario.nivel_seguridad,
        activo=usuario.activo,
        es_superusuario=usuario.es_superusuario,
        roles=[
            RolResponse(
                id=r.id,
                nombre=r.nombre,
                descripcion=r.descripcion,
                nivel_minimo=r.nivel_minimo
            )
            for r in roles_usuario
        ]
    )

# -----------------------------------
# CREAR USUARIO
# -----------------------------------

@router.post(
    "/",
    response_model=UsuarioCreateResponse
)

def crear_usuario(

    datos: UsuarioCreate,

    db: Session = Depends(get_db),

    usuario_actual=Depends(
        obtener_usuario_actual
    )
):

    logger.debug(
        f"Usuario actual: "
        f"{usuario_actual.usuario}"
    )

    # -----------------------------
    # VALIDAR NIVEL
    # -----------------------------

    if (
        not usuario_actual.es_superusuario
        and
        usuario_actual.nivel_seguridad < 10
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Sin permisos "
                "para crear usuarios."
            )
        )

    # -----------------------------
    # CREAR
    # -----------------------------

    resultado = crear_usuario_web(
        db,
        datos
    )

    # -----------------------------
    # ERROR
    # -----------------------------

    if not resultado["success"]:

        raise HTTPException(
            status_code=400,
            detail=resultado["mensaje"]
        )

    # -----------------------------
    # OK
    # -----------------------------

    return UsuarioCreateResponse(

        success=True,

        mensaje=resultado["mensaje"],

        usuario_id=(
            resultado["usuario_id"]
        )
    )

# -----------------------------------
# ACTUALIZAR USUARIO
# -----------------------------------

@router.patch(

    "/{usuario_id}",

    response_model=(
        UsuarioUpdateResponse
    )
)

def actualizar_usuario(

    usuario_id: int,

    datos: UsuarioUpdate,

    usuario_actual=Depends(
        obtener_usuario_actual
    ),

    db: Session = Depends(
        get_db
    )
):

    # -----------------------------
    # VALIDAR PERMISOS
    # -----------------------------

    if (
        not usuario_actual.es_superusuario
        and
        usuario_actual.nivel_seguridad < 10
    ):

        raise HTTPException(

            status_code=403,

            detail=(
                "Sin permisos "
                "para actualizar usuarios."
            )
        )

    # -----------------------------
    # ACTUALIZAR
    # -----------------------------

    resultado = actualizar_usuario_web(

        db=db,

        usuario_id=usuario_id,

        datos=datos
    )

    logger.debug(
        f"Resultado update: "
        f"{resultado}"
    )

    # -----------------------------
    # ERROR
    # -----------------------------

    if not resultado["success"]:

        raise HTTPException(

            status_code=400,

            detail=(
                resultado["mensaje"]
            )
        )

    # -----------------------------
    # OK
    # -----------------------------

    return UsuarioUpdateResponse(

        success=True,

        mensaje=(
            resultado["mensaje"]
        )
    )

# -----------------------------------
# DESACTIVAR USUARIO
# -----------------------------------

@router.delete(

    "/{usuario_id}"
)

def desactivar_usuario(

    usuario_id: int,

    usuario_actual=Depends(
        obtener_usuario_actual
    ),

    db: Session = Depends(
        get_db
    )
):

    # -----------------------------
    # VALIDAR PERMISOS
    # -----------------------------

    if (

        not usuario_actual.es_superusuario

        and

        usuario_actual.nivel_seguridad < 10
    ):

        raise HTTPException(

            status_code=403,

            detail=(
                "Sin permisos "
                "para desactivar usuarios."
            )
        )

    # -----------------------------
    # DESACTIVAR
    # -----------------------------

    resultado = desactivar_usuario_web(
        
        db=db,
    
        usuario_id=usuario_id,
    
        usuario_actual=usuario_actual.usuario
    )

    # -----------------------------
    # ERROR
    # -----------------------------

    if not resultado["success"]:

        raise HTTPException(

            status_code=400,

            detail=(
                resultado["mensaje"]
            )
        )

    # -----------------------------
    # OK
    # -----------------------------

    return resultado

# -----------------------------------
# REACTIVAR USUARIO
# -----------------------------------

@router.post(
    "/{usuario_id}/reactivar"
)

def reactivar_usuario(

    usuario_id: int,

    usuario_actual=Depends(
        obtener_usuario_actual
    ),

    db: Session = Depends(
        get_db
    )
):

    if (
        not usuario_actual.es_superusuario
        and
        usuario_actual.nivel_seguridad < 10
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Sin permisos "
                "para reactivar usuarios."
            )
        )

    resultado = reactivar_usuario_web(

        db=db,
        usuario_id=usuario_id,
        usuario_actual=usuario_actual.usuario
    )

    if not resultado["success"]:

        raise HTTPException(
            status_code=400,
            detail=resultado["mensaje"]
        )

    return resultado

@router.post(

    "/refresh",

    response_model=RefreshResponse
)

def refresh_token(

    request: Request,

    response: Response,

    db: Session = Depends(get_db),

    datos: RefreshRequest = None
):

    refresh_token_str = request.cookies.get("refresh_token") or (getattr(datos, "refresh_token", None) if datos else None)

    if not refresh_token_str:
        raise HTTPException(status_code=401, detail="Refresh token requerido.")

    resultado = refresh_access_token(

        db=db,

        refresh_token=refresh_token_str
    )

    # -------------------------
    # ERROR
    # -------------------------

    if not resultado["success"]:

        raise HTTPException(

            status_code=401,

            detail=resultado["mensaje"]
        )

    # -------------------------
    # OK
    # -------------------------

    set_refresh_cookie(response, resultado["refresh_token"])

    return RefreshResponse(

        success=True,

        access_token=resultado[
            "access_token"
        ],

        refresh_token=resultado[
            "refresh_token"
        ]
    )