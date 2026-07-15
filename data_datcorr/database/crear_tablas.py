from database.conexion import engine
from database.modelos import Base

# -----------------------------------
# CREAR TODAS LAS TABLAS
# -----------------------------------

print("\nCreando tablas PostgreSQL...\n")

Base.metadata.create_all(bind=engine)

print("Tablas creadas correctamente.")