from pydantic import BaseModel


class SolicitudCreate(BaseModel):
    tipo_documento: str
    identificador_documento: str
    detalle: str
    prioridad: str = "media"