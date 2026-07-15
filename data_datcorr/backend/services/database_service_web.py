import logging

from sqlalchemy import text, inspect
from typing import List, Tuple, Optional

from database.conexion import engine as postgres_engine


MAPA_BASE_SCHEMA = {
    "IPS": "ips",
    "PEDIATRICO": "pediatrico",
    "IGPJ_LISTADO_NUEVO": "igpj_listado_nuevo",
    "IGPJ TXT LISTADO": "igpj_txt_listado",
    "IGPJ": "igpj",
    "MATERNIDAD": "maternidad",
    "ESCRIBANIA": "escribania",
}

BASES_POSTGRES = list(MAPA_BASE_SCHEMA.keys())


def listar_bases() -> list:
    return [{"nombre": nombre, "tipo": "postgres"} for nombre in BASES_POSTGRES]


def _schema_para_base(base: str) -> Optional[str]:
    return MAPA_BASE_SCHEMA.get(base)


def _validar_base(base: str):
    if base not in MAPA_BASE_SCHEMA:
        raise ValueError(f"Base no reconocida: {base}")


def obtener_tablas(base: str) -> list:
    _validar_base(base)
    schema = _schema_para_base(base)
    with postgres_engine.connect() as conn:
        inspector = inspect(conn)
        return inspector.get_table_names(schema=schema)


def consultar_base(
    base: str, tabla: str = "Datcorr_database",
    page: int = 1, limit: Optional[int] = 50,
) -> Tuple[List[str], List[list], int]:
    _validar_base(base)
    schema = _schema_para_base(base)
    with postgres_engine.connect() as conn:
        total = conn.execute(
            text(f'SELECT COUNT(*) FROM "{schema}"."{tabla}"')
        ).scalar() or 0

        if limit is None or limit <= 0:
            sql = text(f'SELECT * FROM "{schema}"."{tabla}"')
            params = {}
        else:
            offset = (page - 1) * limit
            sql = text(f'SELECT * FROM "{schema}"."{tabla}" OFFSET :offset LIMIT :limit')
            params = {"offset": offset, "limit": limit}

        result = conn.execute(sql, params)
        columnas = list(result.keys())
        registros = [list(row) for row in result.fetchall()]
    return columnas, registros, total


def buscar_en_base(
    base: str, criterio: str, tabla: str = "Datcorr_database",
    page: int = 1, limit: int = 50,
) -> Tuple[List[str], List[list], int]:
    _validar_base(base)
    schema = _schema_para_base(base)
    offset = (page - 1) * limit
    with postgres_engine.connect() as conn:
        col_sql = text(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table"
        )
        col_result = conn.execute(col_sql, {"schema": schema, "table": tabla})
        columnas_info = col_result.fetchall()
        columnas = [row[0] for row in columnas_info if not row[0].lower().startswith("id_datcorr")]
        if not columnas:
            return [], [], 0
        where_clause = " OR ".join(
            'CAST("{}" AS TEXT) ILIKE :patron'.format(c) for c in columnas
        )
        id_col = next(
            (row[0] for row in columnas_info if row[0].lower().startswith("id_datcorr")),
            "id_Datcorr_database"
        )
        cols_select = ", ".join('"{}"'.format(c) for c in columnas)

        total = conn.execute(
            text(f'SELECT COUNT(*) FROM "{schema}"."{tabla}" WHERE {where_clause}'),
            {"patron": f"%{criterio}%"},
        ).scalar() or 0

        sql = text(
            'SELECT "{}", {} FROM "{}"."{}" WHERE {} OFFSET :offset LIMIT :limit'.format(
                id_col, cols_select, schema, tabla, where_clause
            )
        )
        result = conn.execute(
            sql, {"patron": f"%{criterio}%", "offset": offset, "limit": limit}
        )
        columnas_out = list(result.keys())
        registros = [list(row) for row in result.fetchall()]
    return columnas_out, registros, total


def actualizar_registro(base: str, registro_id: int, data: dict, tabla: str = "Datcorr_database"):
    _validar_base(base)
    schema = _schema_para_base(base)
    set_clause = ", ".join(f'"{k}" = :{k}' for k in data.keys())
    params = dict(data)
    params["id_value"] = registro_id
    sql = text(
        f'UPDATE "{schema}"."{tabla}" SET {set_clause} WHERE "id_Datcorr_database" = :id_value'
    )
    with postgres_engine.begin() as conn:
        conn.execute(sql, params)
    logging.debug(f"[DB WEB] Registro {registro_id} actualizado en {base}")


def obtener_columnas(base: str, tabla: str = "Datcorr_database") -> list:
    _validar_base(base)
    schema = _schema_para_base(base)
    with postgres_engine.connect() as conn:
        sql = text(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table "
            "ORDER BY ordinal_position"
        )
        result = conn.execute(sql, {"schema": schema, "table": tabla})
        return [{"nombre": row[0], "tipo": row[1]} for row in result.fetchall()]


def eliminar_registro(base: str, registro_id: int, tabla: str = "Datcorr_database"):
    _validar_base(base)
    schema = _schema_para_base(base)
    sql = text(
        f'DELETE FROM "{schema}"."{tabla}" WHERE "id_Datcorr_database" = :id_value'
    )
    with postgres_engine.begin() as conn:
        result = conn.execute(sql, {"id_value": registro_id})
        if result.rowcount == 0:
            raise ValueError(f"Registro {registro_id} no encontrado en {base}")


def insertar_registro(base: str, data: dict, tabla: str = "Datcorr_database") -> int:
    _validar_base(base)
    schema = _schema_para_base(base)
    columnas = ", ".join(f'"{k}"' for k in data.keys())
    valores = ", ".join(f":{k}" for k in data.keys())
    sql = text(
        f'INSERT INTO "{schema}"."{tabla}" ({columnas}) VALUES ({valores})'
    )
    with postgres_engine.begin() as conn:
        conn.execute(sql, data)
        lastval = conn.execute(text("SELECT LASTVAL()")).scalar()
    logging.debug(f"[DB WEB] Registro insertado en {base} con ID {lastval}")
    return lastval


def autocomplete_en_base(
    base: str, columna: str, texto: str, limite: int = 30,
    tabla: str = "Datcorr_database"
) -> list:
    _validar_base(base)
    schema = _schema_para_base(base)
    id_col = "id_Datcorr_database"
    sql = text(
        f'SELECT "{id_col}", "{columna}" FROM "{schema}"."{tabla}" '
        f'WHERE CAST("{columna}" AS TEXT) ILIKE :patron LIMIT :limite'
    )
    with postgres_engine.connect() as conn:
        result = conn.execute(sql, {"patron": f"%{texto}%", "limite": limite})
        return [list(row) for row in result.fetchall()]


def obtener_registro(
    base: str, registro_id: int, columnas: list = None,
    tabla: str = "Datcorr_database"
) -> dict:
    _validar_base(base)
    schema = _schema_para_base(base)
    if not columnas:
        columnas = ["denominacion"]
    cols = ", ".join(f'"{c}"' for c in columnas)
    sql = text(
        f'SELECT {cols} FROM "{schema}"."{tabla}" '
        f'WHERE "id_Datcorr_database" = :id'
    )
    with postgres_engine.connect() as conn:
        result = conn.execute(sql, {"id": registro_id})
        row = result.fetchone()
        if row:
            return dict(zip(columnas, row))
        return None
