import sqlite3

class SQLiteReader:

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def get_columns(self, table_name):

        cursor = self.conn.execute(
            f"PRAGMA table_info({table_name})"
        )

        return cursor.fetchall()

    def get_rows(self, table_name):

        cursor = self.conn.execute(
            f"SELECT * FROM {table_name}"
        )

        return cursor.fetchall()

    def get_count(self, table_name):

        cursor = self.conn.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        )

        return cursor.fetchone()[0]