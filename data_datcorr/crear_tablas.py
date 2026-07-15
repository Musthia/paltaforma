from database.conexion import (
    engine
)

from database.modelos import Base

from database.modelos_blacklist import (
    TokenBlacklist
)

print("\nMODELOS REGISTRADOS:\n")

for tabla in Base.metadata.tables:
    print(tabla)

print("\nCreando tablas PostgreSQL...\n")

Base.metadata.create_all(
    bind=engine
)

print(
    "Tablas creadas correctamente."
)