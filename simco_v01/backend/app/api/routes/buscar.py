from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.core.deps import get_current_user
from app.models.solicitud import Solicitud
from app.models.respuesta import Respuesta
from app.services.buscar_archivos import buscar_en_contenido

router = APIRouter(prefix="/buscar", tags=["Buscar"])


@router.get("/archivos")
def buscar_archivos(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = q.lower()
    resultados: list[dict] = []

    solicitudes = db.query(Solicitud).filter(Solicitud.archivo_nombre.isnot(None)).all()
    for s in solicitudes:
        nombre = buscar_en_contenido(s.archivo_nombre, query)
        if nombre:
            resultados.append({
                "tipo": "solicitud",
                "id": s.id,
                "codigo": s.codigo,
                "archivo_original": nombre,
                "entidad_titulo": f"Solicitud #{s.id}",
            })

    respuestas = db.query(Respuesta).filter(Respuesta.archivo_nombre.isnot(None)).all()
    for r in respuestas:
        nombre = buscar_en_contenido(r.archivo_nombre, query)
        if nombre:
            resultados.append({
                "tipo": "respuesta",
                "id": r.id,
                "solicitud_id": r.solicitud_id,
                "archivo_original": nombre,
                "entidad_titulo": f"Respuesta #{r.id} (Sol. #{r.solicitud_id})",
            })

    return resultados
