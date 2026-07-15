from services.usuario_service import (
    crear_usuario
)

resultado = crear_usuario(
    nombre="Juan",
    apellido="Perez",
    usuario="jperez",
    password="1234",
    rol="Operador",
    nivel_seguridad=3
)

print(resultado)