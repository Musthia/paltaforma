from backend.schemas.usuario_schema import (
    UsuarioCreate
)

datos = UsuarioCreate(
    nombre="Carlos",
    apellido="Lopez",
    usuario="clopez",
    password="1234",
    rol="Operador",
    nivel_seguridad=3
)

print(datos)