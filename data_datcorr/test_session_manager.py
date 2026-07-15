from services.auth_service import (
    autenticar_usuario
)

from core.session_manager import (
    SessionManager
)

# -----------------------------------
# LOGIN
# -----------------------------------

resultado = autenticar_usuario(
    "fabio",
    "5678"
)

if resultado["success"]:

    usuario = resultado["usuario"]

    # -----------------------------------
    # INICIAR SESIÓN
    # -----------------------------------

    SessionManager.login(usuario)

    print("\nSESIÓN INICIADA\n")

    print(
        SessionManager.hay_sesion()
    )

    print(
        SessionManager.obtener_usuario().nombre
    )

    print(
        SessionManager.obtener_rol()
    )

    print(
        SessionManager.obtener_nivel_seguridad()
    )

    print(
        SessionManager.obtener_fecha_login()
    )

    # -----------------------------------
    # LOGOUT
    # -----------------------------------

    SessionManager.logout()

    print("\nSESIÓN CERRADA\n")

    print(
        SessionManager.hay_sesion()
    )