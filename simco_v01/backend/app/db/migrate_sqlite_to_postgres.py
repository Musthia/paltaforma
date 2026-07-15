from sqlalchemy import create_engine, MetaData, Table
from dotenv import load_dotenv
import os

load_dotenv()

SQLITE_URL = os.getenv("SQLITE_URL", "sqlite:///./sige.db")
POSTGRES_URL = os.getenv("POSTGRES_URL")

sqlite_engine = create_engine(SQLITE_URL)
pg_engine = create_engine(POSTGRES_URL)

sqlite_meta = MetaData()
sqlite_meta.reflect(bind=sqlite_engine)

print("🚀 Iniciando migración SQLite → PostgreSQL")

# ⚠️ ORDEN IMPORTA (por foreign keys)
TABLE_ORDER = ["users", "solicitudes", "respuestas", "audit_logs"]

sqlite_conn = sqlite_engine.connect()
pg_conn = pg_engine.connect()

for table_name in TABLE_ORDER:

    if table_name not in sqlite_meta.tables:
        print(f"⚠️ Tabla {table_name} no existe en SQLite, se omite")
        continue

    print(f"📦 Migrando: {table_name}")

    table = sqlite_meta.tables[table_name]

    # crear tabla en postgres
    new_table = Table(
        table_name,
        MetaData(),
        *[c.copy() for c in table.columns],
        extend_existing=True
    )

    new_table.create(pg_engine, checkfirst=True)

    # copiar datos
    rows = sqlite_conn.execute(table.select()).fetchall()

    if rows:
        with pg_engine.begin() as conn:
            conn.execute(new_table.insert(), [dict(row._mapping) for row in rows])

    print(f"✔ {table_name}: {len(rows)} registros migrados")

print("🎉 Migración completada correctamente")