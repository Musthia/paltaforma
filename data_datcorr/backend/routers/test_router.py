from fastapi import (
    APIRouter,
    Depends
)

from backend.security.jwt_bearer import (
    obtener_usuario_actual
)

router = APIRouter(
    prefix="/test",
    tags=["Test"]
)

# -----------------------------------
# RUTA PROTEGIDA
# -----------------------------------

@router.get("/protegido")

def protegido(

    usuario = Depends(
        obtener_usuario_actual
    )

):

    return {
        "success": True,
        "usuario": usuario.username,
        "rol": usuario.role,
        "nivel": usuario.nivel_seguridad,
        "superusuario": (
            usuario.is_superuser
        )
    }