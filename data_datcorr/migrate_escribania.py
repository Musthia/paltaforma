from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

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

session = Session()

migrator = Migrator(
    sqlite_db="bases_g/ESCRIBANIA.db",  # ajusta la ruta real
    postgres_session=session
)

migrator.migrate_table(
    schema_name="escribania",
    table_name="Datcorr_database"
)