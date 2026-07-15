from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from backend.dependencies import get_db

from backend.security.jwt_bearer import (
    obtener_usuario_actual
)

from backend.security.permissions import (
    requiere_permiso
)

from backend.services.roles_service import (
    listar_roles
)

from backend.schemas.roles_schema import (
    RolesListadoResponse,
    RolResponse
)

router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)


@router.get(
    "/",
    response_model=RolesListadoResponse
)
def get_roles(
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual)
):
    roles = listar_roles(db)
    return RolesListadoResponse(
        success=True,
        roles=[
            RolResponse(
                id=r.id,
                nombre=r.nombre,
                descripcion=r.descripcion,
                nivel_minimo=r.nivel_minimo
            )
            for r in roles
        ]
    )
