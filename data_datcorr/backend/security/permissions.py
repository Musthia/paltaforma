from fastapi import (
    Depends,
    HTTPException
)

from backend.security.jwt_bearer import (
    obtener_usuario_actual
)

from services.usuarios_permisos_service import (
    usuario_tiene_permiso
)

# -----------------------------------
# REQUIERE PERMISO
# -----------------------------------

def requiere_permiso(
    codigo_permiso
):

    def validador(

        usuario = Depends(
            obtener_usuario_actual
        )

    ):

        # -----------------------------
        # SUPERUSUARIO
        # -----------------------------

        if usuario.es_superusuario:

            return usuario

        permitido = (
            usuario_tiene_permiso(
                usuario.id,
                codigo_permiso
            )
        )

        if not permitido:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Permiso denegado."
                )
            )

        return usuario

    return validador

# -----------------------------------
# REQUIERE NIVEL
# -----------------------------------

def requiere_nivel(
    nivel_requerido
):

    def validador(

        usuario = Depends(
            obtener_usuario_actual
        )

    ):

        # -----------------------------
        # SUPERUSUARIO
        # -----------------------------

        if usuario.es_superusuario:

            return usuario

        if (
            usuario.nivel_seguridad
            <
            nivel_requerido
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "Nivel insuficiente."
                )
            )

        return usuario

    return validador