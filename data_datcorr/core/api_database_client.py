from core.api_client import ApiClient


class ApiDatabaseClient:

    def __init__(self, client: ApiClient):
        self._client = client

    def listar_bases(self):
        return self._client.get("/databases/")

    def listar_tablas(self, base: str):
        return self._client.get(f"/databases/{base}/tables")

    def consultar_datos(self, base: str, table: str = "Datcorr_database",
                        page: int = 1, limit: int = 50):
        return self._client.get(
            f"/databases/{base}/data",
            params={"table": table, "page": page, "limit": limit}
        )

    def buscar_datos(self, base: str, q: str, table: str = "Datcorr_database",
                     page: int = 1, limit: int = 50):
        return self._client.get(
            f"/databases/{base}/search",
            params={"q": q, "table": table, "page": page, "limit": limit}
        )

    def listar_columnas(self, base: str, table: str = "Datcorr_database"):
        return self._client.get(
            f"/databases/{base}/columns",
            params={"table": table}
        )

    def crear_registro(self, base: str, data: dict,
                       table: str = "Datcorr_database"):
        return self._client.post(
            f"/databases/{base}/records?table={table}",
            {"data": data}
        )

    def actualizar(self, base: str, record_id: int, data: dict,
                   table: str = "Datcorr_database"):
        return self._client.patch(
            f"/databases/{base}/records/{record_id}?table={table}",
            {"data": data}
        )

    def eliminar(self, base: str, record_id: int,
                 table: str = "Datcorr_database"):
        return self._client.delete(
            f"/databases/{base}/records/{record_id}?table={table}"
        )

    def autocomplete(self, base: str, columna: str, q: str,
                     limite: int = 30, table: str = "Datcorr_database"):
        return self._client.get(
            f"/databases/{base}/autocomplete",
            params={"columna": columna, "q": q, "limite": limite, "table": table}
        )

    def obtener_registro(self, base: str, record_id: int,
                         columnas: list = None,
                         table: str = "Datcorr_database"):
        params = {"table": table}
        if columnas:
            params["columnas"] = ",".join(columnas)
        return self._client.get(
            f"/databases/{base}/records/{record_id}",
            params=params
        )