from db.engines import create_postgres_engine

def initialize_postgres():
    engine = create_postgres_engine()
    db_registry.set_engine(engine)
    db_registry.db_type = "postgres"
    db_registry.current_source = "postgresql"

    return engine

class DBRegistry:
    """
    Mantiene la base activa en runtime (SQLite o PostgreSQL)
    """

    def __init__(self):
        print("ID REGISTRY:", id(self))
        self.engine = None
        self.db_type = None
        self.current_source = None

    def set_engine(self, engine):
        print("SET REGISTRY:", id(self))
        self.engine = engine
        print("[REGISTRY] engine seteado:", engine)

    def get_engine(self):
        print("GET REGISTRY:", id(self))
        print("ENGINE:", self.engine)
        print("[REGISTRY] engine leído:", self.engine)
        return self.engine

    def set_sqlite(self, db_path: str):
        from db.engines import get_sqlite_engine

        self.engine = get_sqlite_engine(db_path)
        self.db_type = "sqlite"
        self.current_source = db_path

    def set_postgres(self):
        from db.engines import postgres_engine

        self.engine = postgres_engine
        self.db_type = "postgres"
        self.current_source = "postgresql"


# instancia global (tipo singleton)
db_registry = DBRegistry()