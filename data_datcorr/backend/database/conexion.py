from database.conexion import (
    engine,
    SessionLocal
)

# -----------------------------------
# DEPENDENCY DB
# -----------------------------------

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()