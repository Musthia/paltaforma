import logging

from repositories.base_repository import BaseRepository
from database.modelos import UsuarioPermiso, Usuario, Permiso


class UsuariosPermisosRepository(BaseRepository):

    # -----------------------------------
    # LISTAR PERMISOS DE USUARIO
    # -----------------------------------

    def get_permisos_usuario(self, usuario_id: int):

        try:

            return (
                self.session.query(UsuarioPermiso)
                .filter(
                    UsuarioPermiso.usuario_id == usuario_id
                )
                .all()
            )

        except Exception:

            logging.exception("Error get_permisos_usuario")
            raise

    # -----------------------------------
    # ASIGNAR PERMISO
    # -----------------------------------

    def asignar_permiso(self, usuario_id: int, permiso_id: int):

        try:

            existente = (
                self.session.query(UsuarioPermiso)
                .filter(
                    UsuarioPermiso.usuario_id == usuario_id,
                    UsuarioPermiso.permiso_id == permiso_id
                )
                .first()
            )

            if existente:
                return None

            nuevo = UsuarioPermiso(
                usuario_id=usuario_id,
                permiso_id=permiso_id
            )

            self.session.add(nuevo)
            self.session.commit()

            return nuevo

        except Exception:

            self.session.rollback()
            logging.exception("Error asignar_permiso")
            raise

    # -----------------------------------
    # QUITAR PERMISO
    # -----------------------------------

    def quitar_permiso(self, usuario_id: int, permiso_id: int):

        try:

            registro = (
                self.session.query(UsuarioPermiso)
                .filter(
                    UsuarioPermiso.usuario_id == usuario_id,
                    UsuarioPermiso.permiso_id == permiso_id
                )
                .first()
            )

            if not registro:
                return False

            self.session.delete(registro)
            self.session.commit()

            return True

        except Exception:

            self.session.rollback()
            logging.exception("Error quitar_permiso")
            raise

    # -----------------------------------
    # VALIDAR PERMISO
    # -----------------------------------

    def usuario_tiene_permiso(self, usuario_id: int, permiso_codigo: str):

        try:

            return (
                self.session.query(UsuarioPermiso)
                .join(Permiso)
                .join(Usuario)
                .filter(
                    Usuario.id == usuario_id,
                    Permiso.codigo == permiso_codigo
                )
                .first()
                is not None
            )

        except Exception:

            logging.exception("Error usuario_tiene_permiso")
            raise