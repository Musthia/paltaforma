import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.core.deps import get_current_user
from app.services.respuesta_service import responder_solicitud
from app.services.archivo_helper import guardar_archivo, UPLOAD_DIR

from app.models.respuesta import Respuesta
from app.models.user import User

from app.models.audit import AuditLog

router = APIRouter(prefix="/respuestas", tags=["Respuestas"])


@router.post("/")
def responder(
    solicitud_id: int = Form(...),
    estado_documento: str = Form(...),
    observacion: str = Form(...),
    detalle: str = Form(...),
    archivo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role in ("oficina", "consulta"):
        raise HTTPException(status_code=403, detail="No tienes permiso para responder solicitudes")

    archivo_nombre = None
    if archivo and archivo.filename:
        nombre_original, nombre_servidor = guardar_archivo(archivo)
        archivo_nombre = f"{nombre_servidor}::{nombre_original}"

    class Data:
        pass
    data = Data()
    data.solicitud_id = solicitud_id
    data.estado_documento = estado_documento
    data.observacion = observacion
    data.detalle = detalle

    respuesta = responder_solicitud(db, data, user.id, archivo_nombre)

    if not respuesta:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    return respuesta

@router.get("/{respuesta_id}/archivo")
def descargar_archivo_respuesta(respuesta_id: int, db: Session = Depends(get_db)):
    respuesta = db.query(Respuesta).filter(Respuesta.id == respuesta_id).first()
    if not respuesta or not respuesta.archivo_nombre:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    nombre_servidor, nombre_original = respuesta.archivo_nombre.split("::", 1)
    ruta = os.path.join(UPLOAD_DIR, nombre_servidor)
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")

    return FileResponse(ruta, headers={"Content-Disposition": f'inline; filename="{nombre_original}"'})


@router.get("/{respuesta_id}/archivo/download")
def descargar_archivo_respuesta_directo(respuesta_id: int, db: Session = Depends(get_db)):
    respuesta = db.query(Respuesta).filter(Respuesta.id == respuesta_id).first()
    if not respuesta or not respuesta.archivo_nombre:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    nombre_servidor, nombre_original = respuesta.archivo_nombre.split("::", 1)
    ruta = os.path.join(UPLOAD_DIR, nombre_servidor)
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")

    return FileResponse(ruta, filename=nombre_original, media_type="application/octet-stream")


@router.get("/")
def listar_respuestas(db: Session = Depends(get_db)):
    rows = db.query(Respuesta, User.username).outerjoin(User, User.id == Respuesta.usuario_responde_id).all()
    result = []
    for r, nombre in rows:
        d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        d["usuario_responde_nombre"] = nombre or f"usuario {r.usuario_responde_id}"
        result.append(d)
    return result