def get_usuario_attr(usuario, key, default=None):

    if not usuario:
        return default

    if isinstance(usuario, dict):
        return usuario.get(key, default)

    return getattr(usuario, key, default)