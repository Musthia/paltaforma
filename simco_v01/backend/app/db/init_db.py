from app.db.base import Base
from app.db.session import engine

# IMPORTANTE: importar TODOS los modelos
from app.models import user, solicitud, respuesta, audit  # noqa

def init_db():
    Base.metadata.create_all(bind=engine)
    print("[SIMCO] Tablas creadas correctamente")

if __name__ == "__main__":
    init_db()