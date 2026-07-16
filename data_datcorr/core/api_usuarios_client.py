from core.api_client import ApiClient


_FIELD_MAP = {
    "username": "usuario",
    "full_name": "nombre",
    "role": "rol",
    "is_active": "activo",
    "is_superuser": "es_superusuario",
}

_FIELD_MAP_REVERSE = {v: k for k, v in _FIELD_MAP.items()}

def _map_user(user: dict) -> dict:
    mapped = {}
    for eng, spa in _FIELD_MAP.items():
        if eng in user:
            mapped[spa] = user[eng]
    for k, v in user.items():
        if k not in _FIELD_MAP:
            mapped[k] = v
    return mapped


class ApiUsuariosClient:

    def __init__(self, client: ApiClient):
        self._client = client

    def listar_usuarios(self, page: int = 1, limit: int = 100,
                        search: str = "", rol: str = "",
                        activo: bool = None,
                        sort_by: str = "id", order: str = "asc"):
        params = {
            "page": page, "limit": limit,
            "search": search, "role": rol,
            "sort_by": sort_by, "order": order
        }
        if activo is not None:
            params["is_active"] = activo
        resultado = self._client.get("/users/", params=params)
        if isinstance(resultado, dict):
            if "users" in resultado:
                resultado["usuarios"] = [_map_user(u) for u in resultado["users"]]
        return resultado

    def obtener_usuario(self, usuario_id: int):
        resultado = self._client.get(f"/users/{usuario_id}")
        if isinstance(resultado, dict):
            return _map_user(resultado)
        return resultado

    def _map_outgoing(self, data: dict) -> dict:
        mapped = {}
        nombre = data.get("nombre", "")
        apellido = data.get("apellido", "")
        if nombre or apellido:
            mapped["full_name"] = f"{nombre} {apellido}".strip()
        for k, v in data.items():
            if k in ("nombre", "apellido"):
                continue
            eng = _FIELD_MAP_REVERSE.get(k, k)
            mapped[eng] = v
        return mapped

    def crear_usuario(self, data: dict):
        return self._client.post("/users/", self._map_outgoing(data))

    def actualizar_usuario(self, usuario_id: int, data: dict):
        return self._client.put(f"/users/{usuario_id}", self._map_outgoing(data))

    def desactivar_usuario(self, usuario_id: int):
        return self._client.delete(f"/users/{usuario_id}")

    def activar_usuario(self, usuario_id: int):
        return self._client.patch(f"/users/{usuario_id}/reactivate")

    def listar_roles(self):
        return self._client.get("/roles/")

    def listar_permisos(self):
        return self._client.get("/permissions/")

    def listar_permisos_usuario(self, usuario_id: int):
        return self._client.get(f"/permissions/user/{usuario_id}")

    def asignar_permiso(self, usuario_id: int, permiso_codigo: str):
        return self._client.post("/permissions/assign", {
            "user_id": usuario_id,
            "permission_code": permiso_codigo
        })

    def quitar_permiso(self, usuario_id: int, permiso_codigo: str):
        return self._client.post("/permissions/remove", {
            "user_id": usuario_id,
            "permission_code": permiso_codigo
        })
