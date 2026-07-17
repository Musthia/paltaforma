import logging
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy import text

from database.conexion import engine as postgres_engine
from backend.security.jwt_bearer import obtener_usuario_actual

router = APIRouter(tags=["dashboard"])

SCHEMAS = [
    "ips", "pediatrico", "igpj", "igpj_txt_listado",
    "igpj_listado_nuevo", "maternidad", "escribania",
]


@router.get("/dashboard/stats")
def dashboard_stats():
    with postgres_engine.connect() as conn:
        bases = []
        total = 0
        total_datcorr = 0
        total_verificado = 0
        for s in SCHEMAS:
            result = conn.execute(
                text('SELECT COUNT(*) FROM "{0}"."Datcorr_database"'.format(s))
            )
            count = result.scalar()
            dat = conn.execute(
                text("""SELECT COUNT(*) FROM "{0}"."Datcorr_database" WHERE estado = 'DATCORR'""".format(s))
            ).scalar() or 0
            ver = conn.execute(
                text("""SELECT COUNT(*) FROM "{0}"."Datcorr_database" WHERE estado = 'VERIFICADO'""".format(s))
            ).scalar() or 0
            bases.append({"nombre": s, "registros": count, "datcorr": dat, "verificado": ver})
            total += count
            total_datcorr += dat
            total_verificado += ver

        user_count = conn.execute(
            text("SELECT COUNT(*) FROM public.usuarios WHERE activo = true")
        ).scalar()
        user_total = conn.execute(
            text("SELECT COUNT(*) FROM public.usuarios")
        ).scalar()

        auditoria = conn.execute(
            text("""
                SELECT fecha, usuario, accion, detalle
                FROM public.auditoria
                ORDER BY fecha DESC
                LIMIT 15
            """)
        )
        actividad = [
            {
                "fecha": row[0].isoformat() if hasattr(row[0], "isoformat") else str(row[0]),
                "usuario": row[1],
                "accion": row[2],
                "detalle": row[3],
            }
            for row in auditoria
        ]

    return {
        "bases": bases,
        "total_registros": total,
        "total_datcorr": total_datcorr,
        "total_verificado": total_verificado,
        "total_bases": len(SCHEMAS),
        "usuarios_activos": user_count or 0,
        "total_usuarios": user_total or 0,
        "actividad": actividad,
    }


@router.get("/auditoria")
def listar_auditoria(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    usuario_actual=Depends(obtener_usuario_actual),
):
    if not usuario_actual.is_superuser and usuario_actual.nivel_seguridad < 10:
        raise HTTPException(status_code=403, detail="Sin permisos para ver auditoria.")
    offset = (page - 1) * limit
    with postgres_engine.connect() as conn:
        total = conn.execute(
            text("SELECT COUNT(*) FROM public.auditoria")
        ).scalar() or 0

        rows = conn.execute(
            text("""
                SELECT id, usuario, accion, tabla, registro_id, endpoint, ip,
                       detalle, fecha, ip_address, user_agent
                FROM public.auditoria
                ORDER BY fecha DESC
                OFFSET :offset LIMIT :limit
            """),
            {"offset": offset, "limit": limit},
        )

        registros = [
            {
                "id": r[0],
                "usuario": r[1],
                "accion": r[2],
                "tabla": r[3],
                "registro_id": r[4],
                "endpoint": r[5],
                "ip": r[6],
                "detalle": r[7],
                "fecha": r[8].isoformat() if hasattr(r[8], "isoformat") else str(r[8]),
                "ip_address": r[9],
                "user_agent": r[10],
            }
            for r in rows
        ]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "registros": registros,
    }
