import os

from pathlib import Path

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")

print("DB_ENGINE =", DB_ENGINE)

if DB_ENGINE == "postgres":
    # Railway PostgreSQL → DATABASE_URL
    # Local → POSTGRES_URL
    DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    if not DATABASE_URL:
        raise RuntimeError(
            "DB_ENGINE=postgres pero no se encontró DATABASE_URL ni POSTGRES_URL. "
            "En Railway, agregá DATABASE_URL=${{Postgres.DATABASE_URL}} en las variables del servicio."
        )
    engine = create_engine(DATABASE_URL)

else:
    DATABASE_URL = "sqlite:///./sige.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)