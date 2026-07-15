# migration/type_mapper.py

def sqlite_to_postgres(sqlite_type: str) -> str:

    sqlite_type = sqlite_type.upper()

    if "INTEGER" in sqlite_type:
        return "INTEGER"

    if "TEXT" in sqlite_type:
        return "TEXT"

    if "REAL" in sqlite_type:
        return "DOUBLE PRECISION"

    if "BLOB" in sqlite_type:
        return "BYTEA"

    return "TEXT"