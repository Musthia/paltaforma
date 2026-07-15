from fastapi import Depends

from platformcore.dependencies import require_permission as platform_require_permission
from platformcore.dependencies import get_current_user
from platformcore.services.security import PermissionService


def requiere_permiso(codigo_permiso):
    return platform_require_permission(codigo_permiso)


def requiere_nivel(nivel_requerido):
    def validador(usuario=Depends(get_current_user)):
        if usuario.is_superuser:
            return usuario
        if usuario.nivel_seguridad < nivel_requerido:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Nivel insuficiente.")
        return usuario
    return validador
