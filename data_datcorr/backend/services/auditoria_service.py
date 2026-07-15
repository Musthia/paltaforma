from sqlalchemy.orm import Session

from database.modelos_auditoria import (
    Auditoria
)

import logging

logger = logging.getLogger(
    "datcorr"
)

# -----------------------------------
# REGISTRAR AUDITORIA
# -----------------------------------

def registrar_auditoria(

    db: Session,

    usuario: str,

    accion: str,

    tabla: str,

    registro_id: int = None,

    endpoint: str = "",

    ip: str = "",

    detalle: str = "",

    ip_address=None,

    user_agent=None,

    token_jti=None
):

    auditoria = Auditoria(

        usuario=usuario,

        accion=accion,

        tabla=tabla,

        registro_id=registro_id,

        endpoint=endpoint,

        ip=ip,

        detalle=detalle,

        ip_address=ip_address,

        user_agent=user_agent,

        token_jti=token_jti
    )

    db.add(auditoria)

    db.commit()

    logger.info(
        f"AUDITORIA: "
        f"{accion} "
        f"{tabla} "
        f"ID={registro_id}"
    )