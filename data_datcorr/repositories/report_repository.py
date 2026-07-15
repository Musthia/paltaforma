import logging
from typing import Any, Optional
from sqlalchemy import text

from database.conexion import engine as postgres_engine
from repositories.base_repository import BaseRepository

logger = logging.getLogger("datcorr")


class ReportRepository(BaseRepository):

    def __init__(self):
        super().__init__()
        self.engine = postgres_engine

    def fetchall(self, sql: str, params: dict = None) -> list[dict]:
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                if result.returns_rows:
                    return [dict(row._mapping) for row in result.fetchall()]
                return []
        except Exception as e:
            logger.error(f"Error en fetchall: {e}", exc_info=True)
            raise

    def scalar(self, sql: str, params: dict = None) -> Optional[Any]:
        try:
            with self.engine.connect() as conn:
                return conn.execute(text(sql), params or {}).scalar()
        except Exception as e:
            logger.error(f"Error en scalar: {e}", exc_info=True)
            raise

    def fetchone(self, sql: str, params: dict = None) -> Optional[dict]:
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return None
        except Exception as e:
            logger.error(f"Error en fetchone: {e}", exc_info=True)
            raise
