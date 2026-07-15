from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
    f"/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:

    result = conn.execute(
        text("""
            SELECT schema_name
            FROM information_schema.schemata
            ORDER BY schema_name
        """)
    )

    for row in result:
        print(row[0])