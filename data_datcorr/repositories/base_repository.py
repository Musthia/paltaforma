from database.conexion import SessionLocal
import logging


class BaseRepository:

    def __init__(self):
        self.session = SessionLocal()
        logging.debug(f"REPOSITORY INIT: {self.__class__.__name__}")

    def close(self):
        if self.session:
            self.session.close()
            self.session = None