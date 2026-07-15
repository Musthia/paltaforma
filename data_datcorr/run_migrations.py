"""
Script unificado de migración SQLite → PostgreSQL.
Ejecuta todas las migraciones secuencialmente.

Para agregar una nueva base, solo añadila a la lista MIGRATIONS.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys

from migration.migrator import Migrator

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
    f"/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# ──────────────────────────────────────────────
# LISTA DE MIGRACIONES — agregar nuevas aquí
# ──────────────────────────────────────────────
MIGRATIONS = [
    {"schema": "ips",              "sqlite": "bases_g/IPS.db"},
    {"schema": "pediatrico",       "sqlite": "bases_g/PEDIATRICO.db"},
    {"schema": "igpj",             "sqlite": "bases_g/IGPJ.db"},
    {"schema": "igpj_txt_listado", "sqlite": "bases_g/IGPJ TXT LISTADO.db"},
    {"schema": "igpj_listado_nuevo","sqlite": "bases_g/IGPJ_LISTADO_NUEVO.db"},
    {"schema": "maternidad",       "sqlite": "bases_g/MATERNIDAD.db"},
    {"schema": "escribania",       "sqlite": "bases_g/ESCRIBANIA.db"},
]

TABLE = "Datcorr_database"


def main():
    session = Session()

    for i, mig in enumerate(MIGRATIONS, start=1):
        schema = mig["schema"]
        sqlite_path = mig["sqlite"]
        label = f"[{i}/{len(MIGRATIONS)}] {schema}"

        if not os.path.exists(sqlite_path):
            print(f"{label} — ARCHIVO NO ENCONTRADO: {sqlite_path}, se salta.")
            continue

        print(f"{label} — migrando desde {sqlite_path} ...")

        try:
            migrator = Migrator(
                sqlite_db=sqlite_path,
                postgres_session=session
            )

            count = migrator.migrate_table(
                schema_name=schema,
                table_name=TABLE
            )

            print(f"{label} — {count} registros migrados")

        except Exception as e:
            print(f"{label} — ERROR: {e}", file=sys.stderr)
            # Rollback parcial para no dejar la sesión inconsistente
            session.rollback()

    session.close()
    print("\nMigraciones finalizadas.")


if __name__ == "__main__":
    main()
