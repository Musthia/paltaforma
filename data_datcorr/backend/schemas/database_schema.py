from pydantic import BaseModel
from typing import Optional, List, Any


class BaseInfo(BaseModel):
    nombre: str
    tipo: str


class BasesResponse(BaseModel):
    success: bool
    bases: List[BaseInfo]


class ConsultaRequest(BaseModel):
    table: str = "Datcorr_database"


class ColumnaInfo(BaseModel):
    nombre: str
    tipo: str


class ConsultaResponse(BaseModel):
    success: bool
    total: int
    columnas: List[str]
    registros: List[List[Any]]


class BusquedaResponse(BaseModel):
    success: bool
    total: int
    columnas: List[str]
    registros: List[List[Any]]
    base: str


class ActualizarRequest(BaseModel):
    data: dict


class ActualizarResponse(BaseModel):
    success: bool
    mensaje: str


class TablasResponse(BaseModel):
    success: bool
    tablas: List[str]


class ColumnasResponse(BaseModel):
    success: bool
    columnas: List[ColumnaInfo]


class CrearRegistroRequest(BaseModel):
    data: dict


class CrearRegistroResponse(BaseModel):
    success: bool
    mensaje: str
    registro_id: Optional[int] = None


class EliminarResponse(BaseModel):
    success: bool
    mensaje: str


class AutocompleteResponse(BaseModel):
    success: bool
    resultados: List[List[Any]]


class ObtenerRegistroResponse(BaseModel):
    success: bool
    registro: Optional[dict] = None
