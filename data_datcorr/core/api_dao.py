from datetime import datetime, timezone

from core.session_manager import SessionManager
from utils.organismos import columnas_para_base


class ApiDAOPostgres:

    def __init__(self, base):
        self.base = base
        self.table = "Datcorr_database"
        self.id_field = "id_Datcorr_database"

    def _db(self):
        return SessionManager.get_db_client()

    def _db_kwargs(self):
        return {"base": self.base, "table": self.table}

    def insertar(self, **kwargs):
        data = dict(kwargs)
        data["registro"] = datetime.now(timezone.utc).isoformat()
        result = self._db().crear_registro(**self._db_kwargs(), data=data)
        if result.get("success"):
            return result.get("registro_id")
        raise RuntimeError(result.get("mensaje", "Error al insertar"))

    def actualizar(self, id_registro, columna, valor):
        result = self._db().actualizar(
            **self._db_kwargs(), record_id=id_registro,
            data={columna: valor}
        )
        if not result.get("success"):
            raise RuntimeError(result.get("mensaje", "Error al actualizar"))

    def eliminar(self, id_registro):
        result = self._db().eliminar(**self._db_kwargs(), record_id=id_registro)
        if not result.get("success"):
            raise RuntimeError(result.get("mensaje", "Error al eliminar"))

    def buscar_autocomplete(self, columna, texto, limite=30):
        result = self._db().autocomplete(
            **self._db_kwargs(), columna=columna, q=texto, limite=limite
        )
        if not result.get("success"):
            return []
        return [
            (row[0], row[1]) for row in result.get("resultados", [])
            if len(row) >= 2
        ]

    def cargar_por_id(self, id_registro, columnas):
        result = self._db().obtener_registro(
            **self._db_kwargs(), record_id=id_registro, columnas=columnas
        )
        if result.get("success"):
            return result.get("registro")
        return None