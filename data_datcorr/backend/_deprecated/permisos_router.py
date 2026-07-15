from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from backend.dependencies import get_db

from backend.security.jwt_bearer import obtener_usuario_actual

from backend.security.permissions import requiere_permiso

from database.modelos import Permiso, UsuarioPermiso

from backend.schemas.permisos_schema import (
    PermisosListadoResponse,
    PermisoResponse,
    AsignarPermisoRequest
)

router = APIRouter(
    prefix="/permisos",
    tags=["permisos"]
)


@router.get(
    "/",
    response_model=PermisosListadoResponse
)
def get_permisos(
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual)
):
    permisos = db.query(Permiso).order_by(Permiso.codigo).all()
    return PermisosListadoResponse(
        success=True,
        permisos=[
            PermisoResponse(
                id=p.id,
                codigo=p.codigo,
                descripcion=p.descripcion
            )
            for p in permisos
        ]
    )


@router.get(
    "/usuario/{usuario_id}",
    response_model=PermisosListadoResponse
)
def get_permisos_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual)
):
    registros = db.query(UsuarioPermiso).filter(
        UsuarioPermiso.usuario_id == usuario_id
    ).all()

    permisos = []
    for up in registros:
        permiso = db.query(Permiso).filter(
            Permiso.id == up.permiso_id
        ).first()
        if permiso:
            permisos.append(permiso)

    return PermisosListadoResponse(
        success=True,
        permisos=[
            PermisoResponse(
                id=p.id,
                codigo=p.codigo,
                descripcion=p.descripcion
            )
            for p in permisos
        ]
    )


@router.post("/asignar")
def asignar_permiso(
    body: AsignarPermisoRequest,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual)
):
    permiso = db.query(Permiso).filter(
        Permiso.codigo == body.permiso_codigo
    ).first()

    if not permiso:
        raise HTTPException(400, "Permiso no encontrado.")

    existe = db.query(UsuarioPermiso).filter(
        UsuarioPermiso.usuario_id == body.usuario_id,
        UsuarioPermiso.permiso_id == permiso.id
    ).first()

    if existe:
        return {"success": False, "mensaje": "El usuario ya tiene este permiso."}

    db.add(UsuarioPermiso(
        usuario_id=body.usuario_id,
        permiso_id=permiso.id
    ))
    db.commit()

    return {"success": True, "mensaje": "Permiso asignado."}


@router.post("/quitar")
def quitar_permiso(
    body: AsignarPermisoRequest,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual)
):
    permiso = db.query(Permiso).filter(
        Permiso.codigo == body.permiso_codigo
    ).first()

    if not permiso:
        raise HTTPException(400, "Permiso no encontrado.")

    up = db.query(UsuarioPermiso).filter(
        UsuarioPermiso.usuario_id == body.usuario_id,
        UsuarioPermiso.permiso_id == permiso.id
    ).first()

    if not up:
        return {"success": False, "mensaje": "El usuario no tiene este permiso."}

    db.delete(up)
    db.commit()

    return {"success": True, "mensaje": "Permiso quitado."}
