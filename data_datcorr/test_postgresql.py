from sqlalchemy import create_engine, text

# -----------------------------------
# CONFIGURACIÓN POSTGRESQL
# -----------------------------------

USUARIO = "postgres"
PASSWORD = "postgres123"
HOST = "localhost"
PUERTO = "5432"
BASE_DATOS = "datcorr"

# -----------------------------------
# URL CONEXIÓN
# -----------------------------------

DATABASE_URL = (
    f"postgresql+psycopg2://{USUARIO}:{PASSWORD}"
    f"@{HOST}:{PUERTO}/{BASE_DATOS}"
)

# -----------------------------------
# ENGINE SQLALCHEMY
# -----------------------------------

engine = create_engine(DATABASE_URL)

# -----------------------------------
# TEST CONEXIÓN
# -----------------------------------

try:

    with engine.connect() as conexion:

        resultado = conexion.execute(
            text("SELECT * FROM prueba_usuarios")
        )

        print("\nCONEXIÓN EXITOSA\n")

        for fila in resultado:
            print(fila)

except Exception as e:

    print("\nERROR DE CONEXIÓN\n")
    print(e)