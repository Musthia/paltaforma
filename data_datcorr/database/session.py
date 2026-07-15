from sqlalchemy.orm import sessionmaker

from database.conexion import engine

# -----------------------------------
# SESSION FACTORY
# -----------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)