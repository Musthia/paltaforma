import logging

from database.modelos import Usuario
from repositories.base_repository import BaseRepository


class UsuariosRepository(BaseRepository):

    # -----------------------------------
    # OBTENER POR ID
    # -----------------------------------

    def get_by_id(self, usuario_id: int):

        try:

            return (
                self.session.query(Usuario)
                .filter(Usuario.id == usuario_id)
                .first()
            )

        except Exception as e:

            logging.exception("Error get_by_id usuarios")

            raise

    # -----------------------------------
    # LISTAR TODOS
    # -----------------------------------

    def get_all(self):
        
        return (
            self.session.query(Usuario)
            .order_by(Usuario.id.asc())
            .all()
        )

    # -----------------------------------
    # CREAR
    # -----------------------------------

    def create(self, usuario: Usuario):

        try:

            self.session.add(usuario)
            self.session.commit()
            return usuario

        except Exception as e:

            self.session.rollback()
            logging.exception("Error create usuario")
            raise

    # -----------------------------------
    # ACTUALIZAR
    # -----------------------------------

    def update(self):

        try:

            self.session.commit()

        except Exception as e:

            self.session.rollback()
            logging.exception("Error update usuario")
            raise

    # -----------------------------------
    # ELIMINAR (si aplica futuro)
    # -----------------------------------

    def delete(self, usuario: Usuario):

        try:

            self.session.delete(usuario)
            self.session.commit()

        except Exception as e:

            self.session.rollback()
            logging.exception("Error delete usuario")
            raise