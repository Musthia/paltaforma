import os
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.core.deps import get_current_user
from app.services.solicitud_service import crear_solicitud
from app.services.archivo_helper import guardar_archivo, UPLOAD_DIR

from app.models.solicitud import Solicitud
from app.models.user import User

from app.models.audit import AuditLog

from fastapi import HTTPException

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])

@router.post("/")
def crear(
    tipo_documento: str = Form(...),
    identificador_documento: str = Form(...),
    detalle: str = Form(...),
    prioridad: str = Form("media"),
    archivo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role == "consulta":
        raise HTTPException(status_code=403, detail="Consulta no puede crear solicitudes")

    archivo_nombre = None
    if archivo and archivo.filename:
        nombre_original, nombre_servidor = guardar_archivo(archivo)
        archivo_nombre = f"{nombre_servidor}::{nombre_original}"

    class Data:
        pass
    data = Data()
    data.tipo_documento = tipo_documento
    data.identificador_documento = identificador_documento
    data.detalle = detalle
    data.prioridad = prioridad

    return crear_solicitud(db, data, user.id, archivo_nombre)

@router.get("/{solicitud_id}/archivo")
def descargar_archivo_solicitud(solicitud_id: int, db: Session = Depends(get_db)):
    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not solicitud or not solicitud.archivo_nombre:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    nombre_servidor, nombre_original = solicitud.archivo_nombre.split("::", 1)
    ruta = os.path.join(UPLOAD_DIR, nombre_servidor)
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")

    return FileResponse(ruta, headers={"Content-Disposition": f'inline; filename="{nombre_original}"'})


@router.get("/{solicitud_id}/archivo/download")
def descargar_archivo_solicitud_directo(solicitud_id: int, db: Session = Depends(get_db)):
    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not solicitud or not solicitud.archivo_nombre:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    nombre_servidor, nombre_original = solicitud.archivo_nombre.split("::", 1)
    ruta = os.path.join(UPLOAD_DIR, nombre_servidor)
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")

    return FileResponse(ruta, filename=nombre_original, media_type="application/octet-stream")


@router.get("/")
def listar_solicitudes(db: Session = Depends(get_db)):
    rows = db.query(Solicitud, User.username).outerjoin(User, User.id == Solicitud.creado_por_usuario_id).all()
    result = []
    for s, nombre in rows:
        d = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        d["creado_por_nombre"] = nombre or f"usuario {s.creado_por_usuario_id}"
        result.append(d)
    return result

@router.get("/panel")
def panel(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(Solicitud)

    if user.role == "consulta":
        query = query.filter(Solicitud.estado != None)  # solo lectura

    elif user.role in ["oficina", "deposito"]:
        query = query.filter(
            (Solicitud.creado_por_usuario_id == user.id)
        )

    # admin ve todo

    return query.order_by(Solicitud.id.desc()).all()

@router.get("/mias")
def mis_solicitudes(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Solicitud)\
        .filter(Solicitud.creado_por_usuario_id == user.id)\
        .order_by(Solicitud.id.desc())\
        .all()
        
@router.get("/estado/{estado}")
def por_estado(
    estado: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    rows = db.query(Solicitud, User.username)\
        .outerjoin(User, User.id == Solicitud.creado_por_usuario_id)\
        .filter(Solicitud.estado == estado)\
        .order_by(Solicitud.id.desc())\
        .all()
    result = []
    for s, nombre in rows:
        d = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        d["creado_por_nombre"] = nombre or f"usuario {s.creado_por_usuario_id}"
        result.append(d)
    return result
        
@router.get("/{solicitud_id}/auditoria")
def auditoria_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(AuditLog)\
        .filter(AuditLog.entidad == "solicitud")\
        .filter(AuditLog.entidad_id == solicitud_id)\
        .order_by(AuditLog.fecha.desc())\
        .all()

@router.patch("/{solicitud_id}/destacar")
def destacar_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ["oficina", "admin"]:
        raise HTTPException(status_code=403, detail="Solo oficina puede destacar")

    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.estado == "respondida":
        raise HTTPException(status_code=400, detail="Solicitud ya respondida, no se puede destacar")

    solicitud.destacado = not solicitud.destacado
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.patch("/{solicitud_id}/verificando")
def verificar_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ["deposito", "admin"]:
        raise HTTPException(status_code=403, detail="Solo depósito puede verificar")

    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.estado == "respondida":
        raise HTTPException(status_code=400, detail="Solicitud ya respondida, no se puede verificar")

    solicitud.verificado = not solicitud.verificado
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.get("/{solicitud_id}")
def detalle_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()

    raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    return solicitud