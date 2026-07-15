from pydantic import BaseModel


class RespuestaCreate(BaseModel):
    solicitud_id: int
    estado_documento: str
    observacion: str
    archivo_digital: str | None = None
    detalle: str