import logging

logger = logging.getLogger(
    "datcorr"
)

# -----------------------------------
# EXCEPCION BASE API
# -----------------------------------

class DatcorrException(
    Exception
):

    def __init__(
        self,
        mensaje: str,
        status_code: int = 400
    ):

        self.mensaje = mensaje

        self.status_code = status_code

        super().__init__(
            mensaje
        )

        logger.error(
            f"DatcorrException: "
            f"{mensaje}"
        )