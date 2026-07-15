import logging
from typing import Any
from datetime import datetime, timedelta
from fastapi import HTTPException
from functools import lru_cache

from repositories.report_repository import ReportRepository

logger = logging.getLogger("datcorr")

SCHEMAS = [
    "ips", "pediatrico", "igpj", "igpj_txt_listado",
    "igpj_listado_nuevo", "maternidad", "escribania",
]

TIPOS_REPORTE = [
    "kpis",
    "actividad-usuarios", "evolucion-diaria", "tipos-operacion",
    "usuarios-inactivos", "actividad-bases", "alertas",
]


class ReportService:
    def __init__(self, repository: ReportRepository = None):
        self.repo = repository or ReportRepository()
        logger.debug("ReportService inicializado")

    def parse_fecha(self, fecha_str: str) -> datetime:
        try:
            return datetime.strptime(fecha_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            raise HTTPException(400, "Formato de fecha inválido. Use YYYY-MM-DD.")

    def validar_rango(self, desde: datetime, hasta: datetime):
        if desde > hasta:
            raise HTTPException(400, "La fecha 'desde' no puede ser posterior a 'hasta'.")
        if (hasta - desde).days > 365:
            raise HTTPException(400, "El rango de fechas no puede superar 1 año.")

    def get_kpis(self, es_admin: bool = True, usuario_actual: str = ""):
        total_registros = 0
        for s in SCHEMAS:
            cnt = self.repo.scalar(f'SELECT COUNT(*) FROM "{s}"."Datcorr_database"') or 0
            total_registros += cnt
        activos = self.repo.scalar("SELECT COUNT(*) FROM public.usuarios WHERE activo = true") or 0
        total_usuarios = self.repo.scalar("SELECT COUNT(*) FROM public.usuarios") or 0
        alertas = self._contar_alertas()
        return {
            "total_registros": total_registros,
            "usuarios_activos": activos,
            "total_usuarios": total_usuarios,
            "alertas_pendientes": alertas,
        }

    def get_actividad_usuarios(self, desde: str, hasta: str, limite: int = 10, pagina: int = 1,
                               es_admin: bool = True, usuario_actual: str = ""):
        self.validar_rango(self.parse_fecha(desde), self.parse_fecha(hasta))
        offset = (pagina - 1) * limite
        sql = """
            SELECT usuario, COUNT(*) as operaciones
            FROM public.auditoria
            WHERE fecha BETWEEN :desde AND :hasta
              AND (:es_admin = true OR usuario = :usuario_actual)
            GROUP BY usuario
            ORDER BY operaciones DESC
            LIMIT :limite OFFSET :offset
        """
        return self.repo.fetchall(sql, {
            "desde": desde, "hasta": hasta,
            "es_admin": es_admin, "usuario_actual": usuario_actual,
            "limite": limite, "offset": offset,
        })

    def get_evolucion_diaria(self, desde: str, hasta: str, es_admin: bool = True, usuario_actual: str = ""):
        sql = """
            SELECT DATE(fecha) as dia, COUNT(*) as operaciones
            FROM public.auditoria
            WHERE fecha BETWEEN :desde AND :hasta
              AND (:es_admin = true OR usuario = :usuario_actual)
            GROUP BY dia ORDER BY dia
        """
        return self.repo.fetchall(sql, {"desde": desde, "hasta": hasta, "es_admin": es_admin, "usuario_actual": usuario_actual})

    def get_tipos_operacion(self, desde: str, hasta: str, es_admin: bool = True, usuario_actual: str = ""):
        sql = """
            SELECT accion, COUNT(*) as cantidad
            FROM public.auditoria
            WHERE fecha BETWEEN :desde AND :hasta
              AND (:es_admin = true OR usuario = :usuario_actual)
            GROUP BY accion ORDER BY cantidad DESC
        """
        return self.repo.fetchall(sql, {"desde": desde, "hasta": hasta, "es_admin": es_admin, "usuario_actual": usuario_actual})

    def get_usuarios_inactivos(self, dias: int = 30, es_admin: bool = True, usuario_actual: str = ""):
        if not es_admin:
            raise HTTPException(403, "Sin permisos para ver usuarios inactivos.")
        fecha_limite = (datetime.utcnow() - timedelta(days=dias)).strftime("%Y-%m-%d")
        sql = """
            SELECT u.usuario, u.nombre, u.rol, MAX(a.fecha) AS ultimo_acceso
            FROM public.usuarios u
            LEFT JOIN public.auditoria a ON a.usuario = u.usuario
            WHERE u.activo = true
            GROUP BY u.usuario, u.nombre, u.rol
            HAVING MAX(a.fecha) IS NULL OR MAX(a.fecha) < :fecha_limite
            ORDER BY ultimo_acceso ASC NULLS FIRST
        """
        return self.repo.fetchall(sql, {"fecha_limite": fecha_limite})

    def get_actividad_bases(self):
        resultados = []
        for s in SCHEMAS:
            cnt = self.repo.scalar(f'SELECT COUNT(*) FROM "{s}"."Datcorr_database"') or 0
            resultados.append({"base": s, "schema": s, "registros": cnt})
        return resultados

    def get_alertas(self, min_borrados: int = 50, min_login_fallidos: int = 5,
                    ventana_horas: int = 24, limite: int = 20,
                    es_admin: bool = True, usuario_actual: str = ""):
        if not es_admin:
            raise HTTPException(403, "Sin permisos para ver alertas.")
        alertas = []
        rows = self.repo.fetchall("""
            SELECT usuario, COUNT(*) as cantidad
            FROM public.auditoria
            WHERE accion IN ('DELETE','DELETE_LOGICO') AND fecha >= NOW() - CAST(:ventana AS interval)
            GROUP BY usuario HAVING COUNT(*) > :min_borrados
            LIMIT :limite
        """, {"ventana": f"{ventana_horas} hours", "min_borrados": min_borrados, "limite": limite})
        for r in rows:
            alertas.append({
                "regla": "borrados_masivos", "severidad": "alta",
                "detalle": f"Usuario '{r['usuario']}' realizó {r['cantidad']} eliminaciones en {ventana_horas}h.",
                "cantidad_afectados": r["cantidad"],
            })
            logger.warning(f"ALERTA [alta] {alertas[-1]['detalle']}")
        rows = self.repo.fetchall("""
            SELECT usuario, COUNT(*) as cantidad
            FROM public.auditoria
            WHERE accion = 'LOGIN_FAILED' AND fecha >= NOW() - CAST(:ventana AS interval)
            GROUP BY usuario HAVING COUNT(*) >= :min_login_fallidos
            LIMIT :limite
        """, {"ventana": f"{ventana_horas} hours", "min_login_fallidos": min_login_fallidos, "limite": limite})
        for r in rows:
            alertas.append({
                "regla": "login_fallidos", "severidad": "alta",
                "detalle": f"Usuario '{r['usuario']}' tuvo {r['cantidad']} intentos fallidos en {ventana_horas}h.",
                "cantidad_afectados": r["cantidad"],
            })
            logger.warning(f"ALERTA [alta] {alertas[-1]['detalle']}")
        return alertas

    def _contar_alertas(self):
        try:
            b = self.repo.scalar("""
                SELECT COUNT(*) FROM (SELECT usuario FROM public.auditoria
                WHERE accion IN ('DELETE','DELETE_LOGICO')
                AND fecha >= NOW() - CAST('24 hours' AS interval)
                GROUP BY usuario HAVING COUNT(*) > 50) sub
            """) or 0
            f = self.repo.scalar("""
                SELECT COUNT(*) FROM (SELECT usuario FROM public.auditoria
                WHERE accion = 'LOGIN_FAILED'
                AND fecha >= NOW() - CAST('24 hours' AS interval)
                GROUP BY usuario HAVING COUNT(*) >= 5) sub
            """) or 0
            return b + f
        except Exception as e:
            logger.error(f"Error contando alertas: {e}", exc_info=True)
            return 0

    def _verificar_permiso(self, modulo, es_admin: bool):
        permiso = getattr(modulo, "PERMISO_REQUERIDO", None)
        if permiso == "admin" and not es_admin:
            raise HTTPException(403, f"Sin permisos para acceder a '{modulo.NOMBRE}'.")

    def ejecutar_consulta(self, nombre_consulta: str, filtros: dict = None,
                          es_admin: bool = True, usuario_actual: str = ""):
        from backend.reportes.consultas import inventario, movimientos, usuarios, auditoria, estadisticos

        CONSULTAS = {
            "inventario": inventario,
            "movimientos": movimientos,
            "usuarios": usuarios,
            "auditoria": auditoria,
            "estadisticos": estadisticos,
        }

        modulo = CONSULTAS.get(nombre_consulta)
        if not modulo:
            raise HTTPException(404, f"Consulta '{nombre_consulta}' no encontrada.")

        self._verificar_permiso(modulo, es_admin)

        filtros = filtros or {}
        params = dict(filtros, es_admin=es_admin, usuario_actual=usuario_actual)
        import inspect
        sig = inspect.signature(modulo.ejecutar)
        kwargs = {k: v for k, v in params.items() if k in sig.parameters}
        result = modulo.ejecutar(self.repo, **kwargs)
        return {
            "nombre": modulo.NOMBRE,
            "descripcion": modulo.DESCRIPCION,
            "columnas": modulo.COLUMNAS,
            "datos": result,
        }

    def listar_consultas_disponibles(self, es_admin: bool = False):
        from backend.reportes.consultas import inventario, movimientos, usuarios, auditoria, estadisticos
        todas = [
            ("inventario", inventario),
            ("movimientos", movimientos),
            ("usuarios", usuarios),
            ("auditoria", auditoria),
            ("estadisticos", estadisticos),
        ]
        resultado = []
        for cid, modulo in todas:
            permiso = getattr(modulo, "PERMISO_REQUERIDO", None)
            if permiso == "admin" and not es_admin:
                continue
            resultado.append({
                "id": cid, "nombre": modulo.NOMBRE,
                "descripcion": modulo.DESCRIPCION, "filtros": modulo.FILTROS,
            })
        return resultado

