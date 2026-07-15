from pydantic import BaseModel

from typing import (
    List,
    Optional
)


class RolResponse(BaseModel):

    id: int
    nombre: str
    descripcion: Optional[str] = None
    nivel_minimo: int


class RolesListadoResponse(BaseModel):

    success: bool
    roles: List[RolResponse]
