from fastapi import (
    Request
)

from fastapi.responses import (
    JSONResponse
)

from backend.core.exceptions import (
    DatcorrException
)

import logging

logger = logging.getLogger(
    "datcorr"
)

# -----------------------------------
# HANDLER CUSTOM
# -----------------------------------

async def datcorr_exception_handler(

    request: Request,

    exc: DatcorrException
):

    logger.error(
        f"ERROR CONTROLADO: "
        f"{exc.mensaje}"
    )

    return JSONResponse(

        status_code=exc.status_code,

        content={

            "success": False,

            "error": exc.mensaje
        }
    )

# -----------------------------------
# HANDLER GLOBAL
# -----------------------------------

async def generic_exception_handler(

    request: Request,

    exc: Exception
):

    logger.exception(
        "ERROR NO CONTROLADO"
    )

    return JSONResponse(

        status_code=500,

        content={

            "success": False,

            "error": (
                "Error interno servidor."
            )
        }
    )