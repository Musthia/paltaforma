from core.session_manager import SessionManager


def _get_client():
    return SessionManager.get_usuarios_client()


def asignar_permiso_usuario(usuario_id, codigo_permiso):
    client = _get_client()
    if not client:
        return {"success": False, "mensaje": "API no disponible."}
    return client.asignar_permiso(usuario_id, codigo_permiso)


def usuario_tiene_permiso(usuario_id, codigo_permiso):
    if not usuario_id:
        return False
    user = SessionManager.obtener_usuario()
    if user and user.get("es_superusuario"):
        return True
    permisos = listar_permisos_usuario(usuario_id)
    return codigo_permiso in permisos


def quitar_permiso_usuario(usuario_id, codigo_permiso):
    client = _get_client()
    if not client:
        return {"success": False, "mensaje": "API no disponible."}
    return client.quitar_permiso(usuario_id, codigo_permiso)


def listar_permisos_usuario(usuario_id):
    client = _get_client()
    if not client:
        return []
    resultado = client.listar_permisos_usuario(usuario_id)
    if resultado and isinstance(resultado, dict):
        return resultado.get("permissions", [])
    return []


def obtener_permisos_usuario(usuario_id):
    return listar_permisos_usuario(usuario_id)
