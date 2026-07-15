class PlatformException(Exception):
    status_code: int = 500
    detail: str = "Error interno de plataforma"

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.detail)


class AuthError(PlatformException):
    status_code = 401
    detail = "Error de autenticación"


class PermissionDenied(PlatformException):
    status_code = 403
    detail = "Permiso denegado"


class NotFoundError(PlatformException):
    status_code = 404
    detail = "Recurso no encontrado"


class ConflictError(PlatformException):
    status_code = 409
    detail = "Conflicto"
