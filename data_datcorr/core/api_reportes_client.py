from core.api_client import ApiClient


class ApiReportesClient:

    def __init__(self, client: ApiClient):
        self._client = client

    def listar_consultas(self):
        return self._client.get("/reportes/consultas")

    def kpis(self):
        return self._client.get("/reportes/kpis")

    def actividad_usuarios(self, desde: str, hasta: str,
                           limite: int = 10, pagina: int = 1):
        return self._client.get(
            "/reportes/actividad-usuarios",
            params={"desde": desde, "hasta": hasta,
                    "limite": limite, "pagina": pagina}
        )

    def evolucion_diaria(self, desde: str, hasta: str):
        return self._client.get(
            "/reportes/evolucion-diaria",
            params={"desde": desde, "hasta": hasta}
        )

    def tipos_operacion(self, desde: str, hasta: str):
        return self._client.get(
            "/reportes/tipos-operacion",
            params={"desde": desde, "hasta": hasta}
        )

    def usuarios_inactivos(self, dias: int = 30):
        return self._client.get(
            "/reportes/usuarios-inactivos",
            params={"dias": dias}
        )

    def actividad_bases(self):
        return self._client.get("/reportes/actividad-bases")

    def alertas(self, min_borrados: int = 50,
                min_login_fallidos: int = 5,
                ventana_horas: int = 24, limite: int = 20):
        return self._client.get(
            "/reportes/alertas",
            params={"min_borrados": min_borrados,
                    "min_login_fallidos": min_login_fallidos,
                    "ventana_horas": ventana_horas, "limite": limite}
        )

    def ejecutar_consulta(self, consulta_id: str, **filtros):
        return self._client.get(
            f"/reportes/ejecutar/{consulta_id}",
            params=filtros
        )

    def exportar_consulta(self, consulta_id: str, formato: str = "csv",
                          **filtros):
        params = {"formato": formato}
        params.update(filtros)
        return self._client.get_raw(
            f"/reportes/exportar/{consulta_id}",
            params=params
        )