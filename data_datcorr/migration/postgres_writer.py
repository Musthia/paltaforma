from sqlalchemy import text

from migration.type_mapper import sqlite_to_postgres


class PostgreSQLWriter:

    def __init__(self, session):
        self.session = session

    def drop_table(self, schema_name, table_name):
        """Elimina la tabla si existe, para recrearla con el esquema actual."""
        sql = text(f'DROP TABLE IF EXISTS "{schema_name}"."{table_name}"')
        self.session.execute(sql)
        self.session.commit()

    def create_table_if_not_exists(
        self,
        schema_name,
        table_name,
        columns
    ):

        fields = []

        for col in columns:

            cid, name, col_type, notnull, default, pk = col

            pg_type = sqlite_to_postgres(col_type)

            # INTEGER PRIMARY KEY → SERIAL para auto-increment
            if pk and "INT" in col_type.upper():
                definition = f'"{name}" SERIAL PRIMARY KEY'
            else:
                definition = f'"{name}" {pg_type}'
                if pk:
                    definition += " PRIMARY KEY"

            fields.append(definition)

        sql = f"""
        CREATE TABLE IF NOT EXISTS
        "{schema_name}"."{table_name}"
        (
            {",".join(fields)}
        )
        """

        self.session.execute(text(sql))
        self.session.commit()

    def sync_sequence(self, schema_name, table_name, id_column):
        """Sincroniza la secuencia SERIAL al max(id) + 1 después de migrar datos."""
        sql = text(
            f'SELECT setval(pg_get_serial_sequence(:schema, :col), '
            f'COALESCE(MAX("{id_column}"), 0) + 1, false) '
            f'FROM "{schema_name}"."{table_name}"'
        )
        self.session.execute(sql, {
            "schema": f'"{schema_name}"."{table_name}"',
            "col": id_column
        })
        self.session.commit()

    def truncate_table(self, schema_name, table_name):
        """Vacía la tabla antes de migrar, para una carga limpia y reejecutable."""
        sql = text(
            f'TRUNCATE TABLE "{schema_name}"."{table_name}"'
        )
        self.session.execute(sql)
        self.session.commit()

    def ensure_id_sequence(self, schema_name, table_name, id_column):
        """Asegura que la columna id tenga una secuencia asociada como default.

        Si la tabla fue creada sin SERIAL (p.ej. por el ORM de la app) o ya
        existía, los inserts de la app fallarían con NotNullViolation porque
        el id llegaría nulo. Esta función crea la secuencia y la enlaza.
        """
        check = text(
            "SELECT pg_get_serial_sequence(:qual, :col)"
        )
        qual = f'"{schema_name}"."{table_name}"'
        existing = self.session.execute(
            check, {"qual": qual, "col": id_column}
        ).scalar()

        if not existing:
            seq_name = f"{table_name}_{id_column}_seq"
            self.session.execute(
                text(
                    f'CREATE SEQUENCE IF NOT EXISTS '
                    f'"{schema_name}"."{seq_name}"'
                )
            )
            self.session.execute(
                text(
                    f'ALTER TABLE "{schema_name}"."{table_name}" '
                    f'ALTER COLUMN "{id_column}" '
                    f'SET DEFAULT nextval(\'"{schema_name}"."{seq_name}"\')'
                )
            )

        self.session.commit()

    def clear_table(self, schema_name, table_name):
        """Elimina todos los registros existentes para permitir re-ejecución."""
        sql = text(f'DELETE FROM "{schema_name}"."{table_name}"')
        self.session.execute(sql)
        self.session.commit()

    def insert_rows(
        self,
        schema_name,
        table_name,
        columns,
        rows
    ):

        column_names = [
            c[1]
            for c in columns
        ]

        fields = ",".join(
            f'"{x}"'
            for x in column_names
        )

        placeholders = ",".join(
            f":{x}"
            for x in column_names
        )

        sql = text(f"""
            INSERT INTO "{schema_name}"."{table_name}"
            ({fields})
            VALUES
            ({placeholders})
        """)

        for row in rows:

            data = dict(
                zip(column_names, row)
            )

            self.session.execute(
                sql,
                data
            )

        self.session.commit()