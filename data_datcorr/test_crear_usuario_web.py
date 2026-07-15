from backend.services.usuario_service_web import (
    crear_usuario_web
)

resultado = crear_usuario_web(

    nombre="Laura",

    apellido="Gomez",

    usuario="lgomez",

    password="1234",

    rol="Operador",

    nivel_seguridad=3
)

print(resultado)