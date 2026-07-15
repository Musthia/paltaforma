from pydantic import BaseModel

from typing import (
    List,
    Optional
)

from backend.schemas.roles_schema import (
    RolResponse
)

# -----------------------------------
# RESPONSE USUARIO
# -----------------------------------

class UsuarioResponse(BaseModel):

    id: int
    nombre: str
    apellido: str
    usuario: str
    email: Optional[str] = None
    rol: str
    nivel_seguridad: int
    activo: bool
    es_superusuario: bool
    roles: List[RolResponse] = []


# -----------------------------------
# CREAR USUARIO
# -----------------------------------

class UsuarioCreate(BaseModel):

    nombre: str
    apellido: str
    usuario: str
    password: str
    email: Optional[str] = None
    rol: Optional[str] = "Consulta"
    nivel_seguridad: int = 1
    activo: bool = True
    roles_nombre: Optional[List[str]] = None


# -----------------------------------
# RESPONSE CREAR
# -----------------------------------

class UsuarioCreateResponse(BaseModel):

    success: bool
    mensaje: str
    usuario_id: Optional[int] = None


# -----------------------------------
# RESPONSE LISTADO
# -----------------------------------

class UsuariosListadoResponse(
    BaseModel
):

    success: bool

    total: int

    page: int

    limit: int

    pages: int

    usuarios: List[
        UsuarioResponse
    ]

# -----------------------------------
# UPDATE USUARIO
# -----------------------------------

class UsuarioUpdate(BaseModel):

    nombre: Optional[str] = None

    apellido: Optional[str] = None

    usuario: Optional[str] = None

    email: Optional[str] = None

    password: Optional[str] = None

    rol: Optional[str] = None

    nivel_seguridad: Optional[int] = None

    activo: Optional[bool] = None

    roles_nombre: Optional[List[str]] = None

# -----------------------------------
# RESPONSE UPDATE
# -----------------------------------

class UsuarioUpdateResponse(
    BaseModel
):

    success: bool

    mensaje: str