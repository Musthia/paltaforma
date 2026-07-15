from fastapi import (
    APIRouter,
    Depends
)

from backend.security.permissions import (
    requiere_permiso
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# -----------------------------------
# ADMIN USUARIOS
# -----------------------------------

@router.get("/usuarios")

def usuarios(

    usuario = Depends(
        requiere_permiso(
            "ADMIN_USUARIOS"
        )
    )

):

    return {
        "success": True,
        "mensaje": (
            "Acceso autorizado."
        ),
        "usuario": usuario.usuario
    }