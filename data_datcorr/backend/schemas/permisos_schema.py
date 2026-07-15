from pydantic import BaseModel

from typing import List


class PermisoResponse(BaseModel):
    id: int
    codigo: str
    descripcion: str


class PermisosListadoResponse(BaseModel):
    success: bool
    permisos: List[PermisoResponse]


class AsignarPermisoRequest(BaseModel):
    usuario_id: int
    permiso_codigo: str
