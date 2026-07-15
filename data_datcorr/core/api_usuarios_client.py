from core.api_client import ApiClient


class ApiUsuariosClient:

    def __init__(self, client: ApiClient):
        self._client = client

    def listar_usuarios(self, page: int = 1, limit: int = 100,
                        search: str = "", rol: str = "",
                        activo: bool = None,
                        sort_by: str = "id", order: str = "asc"):
        params = {
            "page": page, "limit": limit,
            "search": search, "rol": rol,
            "sort_by": sort_by, "order": order
        }
        if activo is not None:
            params["activo"] = activo
        return self._client.get("/usuarios/", params=params)

    def obtener_usuario(self, usuario_id: int):
        return self._client.get(f"/usuarios/{usuario_id}")

    def crear_usuario(self, data: dict):
        return self._client.post("/usuarios/", data)

    def actualizar_usuario(self, usuario_id: int, data: dict):
        return self._client.patch(f"/usuarios/{usuario_id}", data)

    def desactivar_usuario(self, usuario_id: int):
        return self._client.delete(f"/usuarios/{usuario_id}")

    def activar_usuario(self, usuario_id: int):
        return self._client.post(f"/usuarios/{usuario_id}/reactivar")

    def listar_roles(self):
        return self._client.get("/roles/")

    def listar_permisos(self):
        return self._client.get("/permisos/")

    def listar_permisos_usuario(self, usuario_id: int):
        return self._client.get(f"/permisos/usuario/{usuario_id}")

    def asignar_permiso(self, usuario_id: int, permiso_codigo: str):
        return self._client.post("/permisos/asignar", {
            "usuario_id": usuario_id,
            "permiso_codigo": permiso_codigo
        })

    def quitar_permiso(self, usuario_id: int, permiso_codigo: str):
        return self._client.post("/permisos/quitar", {
            "usuario_id": usuario_id,
            "permiso_codigo": permiso_codigo
        })
