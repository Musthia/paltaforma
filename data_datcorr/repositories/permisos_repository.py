import logging

from repositories.base_repository import BaseRepository
from database.modelos import Permiso


class PermisosRepository(BaseRepository):

    # -----------------------------------
    # LISTAR TODOS
    # -----------------------------------

    def get_all(self):

        try:

            return (
                self.session.query(Permiso)
                .order_by(Permiso.codigo)
                .all()
            )

        except Exception:

            logging.exception("Error get_all permisos")
            raise

    # -----------------------------------
    # OBTENER POR ID
    # -----------------------------------

    def get_by_id(self, permiso_id: int):

        try:

            return (
                self.session.query(Permiso)
                .filter(Permiso.id == permiso_id)
                .first()
            )

        except Exception:

            logging.exception("Error get_by_id permisos")
            raise

    # -----------------------------------
    # OBTENER POR CÓDIGO
    # -----------------------------------

    def get_by_codigo(self, codigo: str):

        try:

            return (
                self.session.query(Permiso)
                .filter(Permiso.codigo == codigo)
                .first()
            )

        except Exception:

            logging.exception("Error get_by_codigo permisos")
            raise