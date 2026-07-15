import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.security.jwt_bearer import obtener_usuario_actual
from backend.dependencies import get_db
from backend.database.conexion import get_db as _inject_db
from backend.reportes.report_service import ReportService
from backend.reportes.exportadores.csv_exporter import CSVExporter
from backend.reportes.exportadores.excel_exporter import ExcelExporter
from backend.reportes.exportadores.pdf_exporter import PDFExporter
from backend.services.auditoria_service import registrar_auditoria

logger = logging.getLogger("datcorr")
router = APIRouter(prefix="/reportes", tags=["reportes"])

svc = ReportService()
exportadores = {
    "csv": CSVExporter(),
    "xlsx": ExcelExporter(),
    "pdf": PDFExporter(),
}
FORMATOS_VALIDOS = set(exportadores.keys())
TIPOS_EXPORTABLES = {"kpis", "actividad-usuarios", "evolucion-diaria", "tipos-operacion",
                     "usuarios-inactivos", "actividad-bases", "alertas",
                     "inventario", "movimientos", "usuarios", "auditoria"}


def _es_admin(user) -> bool:
    return user.es_superusuario or user.nivel_seguridad >= 10


@router.get("/consultas")
def listar_consultas(usuario_actual=Depends(obtener_usuario_actual)):
    return {"consultas": svc.listar_consultas_disponibles(es_admin=_es_admin(usuario_actual))}


@router.get("/kpis")
def kpis(usuario_actual=Depends(obtener_usuario_actual)):
    try:
        return svc.get_kpis(es_admin=_es_admin(usuario_actual), usuario_actual=usuario_actual.usuario)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en kpis: {e}", exc_info=True)
        raise HTTPException(500, "Error interno del servidor.")


@router.get("/actividad-usuarios")
def actividad_usuarios(
    desde: str = Query(...), hasta: str = Query(...),
    limite: int = Query(10, ge=1, le=100), pagina: int = Query(1, ge=1),
    usuario_actual=Depends(obtener_usuario_actual),
):
    try:
        return svc.get_actividad_usuarios(desde, hasta, limite, pagina,
                                          _es_admin(usuario_actual), usuario_actual.usuario)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en actividad-usuarios: {e}", exc_info=True)
        raise HTTPException(500, "Error interno del servidor.")


@router.get("/evolucion-diaria")
def evolucion_diaria(
    desde: str = Query(...), hasta: str = Query(...),
    usuario_actual=Depends(obtener_usuario_actual),
):
    try:
        return svc.get_evolucion_diaria(desde, hasta, _es_admin(usuario_actual), usuario_actual.usuario)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en evolucion-diaria: {e}", exc_info=True)
        raise HTTPException(500, "Error interno del servidor.")


@router.get("/tipos-operacion")
def tipos_operacion(
    desde: str = Query(...), hasta: str = Query(...),
    usuario_actual=Depends(obtener_usuario_actual),
):
    try:
        return svc.get_tipos_operacion(desde, hasta, _es_admin(usuario_actual), usuario_actual.usuario)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en tipos-operacion: {e}", exc_info=True)
        raise HTTPException(500, "Error interno del servidor.")


@router.get("/usuarios-inactivos")
def usuarios_inactivos(
    dias: int = Query(30, ge=1, le=365),
    usuario_actual=Depends(obtener_usuario_actual),
):
    try:
        return svc.get_usuarios_inactivos(dias, _es_admin(usuario_actual), usuario_actual.usuario)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en usuarios-inactivos: {e}", exc_info=True)
        raise HTTPException(500, "Error interno del servidor.")


@router.get("/actividad-bases")
def actividad_bases(usuario_actual=Depends(obtener_usuario_actual)):
    try:
        return svc.get_actividad_bases()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en actividad-bases: {e}", exc_info=True)
        raise HTTPException(500, "Error interno del servidor.")


@router.get("/alertas")
def alertas(
    min_borrados: int = Query(50, ge=1),
    min_login_fallidos: int = Query(5, ge=1),
    ventana_horas: int = Query(24, ge=1, le=720),
    limite: int = Query(20, ge=1, le=200),
    usuario_actual=Depends(obtener_usuario_actual),
):
    try:
        return svc.get_alertas(min_borrados, min_login_fallidos, ventana_horas, limite,
                               _es_admin(usuario_actual), usuario_actual.usuario)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en alertas: {e}", exc_info=True)
        raise HTTPException(500, "Error interno del servidor.")


@router.get("/ejecutar/{consulta_id}")
def ejecutar_consulta(
    consulta_id: str,
    request: Request,
    usuario_actual=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        filtros = dict(request.query_params)

        result = svc.ejecutar_consulta(consulta_id, filtros,
                                       _es_admin(usuario_actual), usuario_actual.usuario)

        registrar_auditoria(
            db=db, usuario=usuario_actual.usuario, accion="CONSULTA",
            tabla=f"reportes.{consulta_id}",
            detalle=f"Ejecutó reporte '{consulta_id}' con filtros: {filtros}"
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ejecutando consulta {consulta_id}: {e}", exc_info=True)
        raise HTTPException(500, "Error interno del servidor.")


@router.get("/exportar/{consulta_id}")
def exportar_consulta(
    consulta_id: str,
    request: Request,
    formato: str = Query("csv"),
    usuario_actual=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        if formato not in FORMATOS_VALIDOS:
            raise HTTPException(400, f"Formato '{formato}' no soportado. Use: {', '.join(FORMATOS_VALIDOS)}")

        filtros = dict(request.query_params)
        filtros.pop("formato", None)

        result = svc.ejecutar_consulta(consulta_id, filtros,
                                       _es_admin(usuario_actual), usuario_actual.usuario)
        datos = result["datos"]
        nombre_archivo = f"reporte_{consulta_id}"

        exportador = exportadores[formato]
        response = exportador.exportar(datos, nombre_archivo)

        registrar_auditoria(
            db=db, usuario=usuario_actual.usuario, accion="REPORTE_EXPORT",
            tabla=f"reportes.{consulta_id}",
            detalle=f"Exportó '{consulta_id}' en formato {formato}. Filtros: {filtros}"
        )

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exportando {consulta_id}: {e}", exc_info=True)
        raise HTTPException(500, "Error interno del servidor.")
