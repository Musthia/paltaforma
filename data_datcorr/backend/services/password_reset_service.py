import secrets
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from database.modelos import Usuario
from database.modelos_reset import PasswordResetToken
from database.modelos_refresh import RefreshToken
from utils.hash import hash_password

logger = logging.getLogger("datcorr")

RESET_TOKEN_EXPIRE_MINUTES = 30


def solicitar_reset(db: Session, email: str, ip: str = None) -> str:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        logger.info(f"Solicitud de reset para email no registrado: {email}")
        return ""

    # revocar tokens pendientes previos
    db.query(PasswordResetToken).filter(
        PasswordResetToken.usuario_id == usuario.id,
        PasswordResetToken.usado == False
    ).update({"usado": True})

    token_plano = secrets.token_urlsafe(32)
    token_hash = hash_password(token_plano)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

    nuevo = PasswordResetToken(
        usuario_id=usuario.id,
        token_hash=token_hash,
        expires_at=expires_at,
        ip_solicitud=ip,
    )
    db.add(nuevo)
    db.commit()

    return token_plano


def resetear_password(db: Session, token: str, nueva_password: str) -> bool:
    ahora = datetime.now(timezone.utc)
    candidatos = db.query(PasswordResetToken).filter(
        PasswordResetToken.usado == False,
        PasswordResetToken.expires_at > ahora
    ).all()

    registro = None
    for r in candidatos:
        from utils.hash import verificar_password
        if verificar_password(token, r.token_hash):
            registro = r
            break

    if not registro:
        return False

    usuario = db.query(Usuario).filter(Usuario.id == registro.usuario_id).first()
    if not usuario:
        return False

    usuario.password_hash = hash_password(nueva_password)
    usuario.ultimo_cambio_password = ahora

    registro.usado = True

    # invalidar todos los refresh tokens del usuario
    db.query(RefreshToken).filter(
        RefreshToken.usuario_id == usuario.id,
        RefreshToken.revoked == False
    ).update({"revoked": True})

    db.commit()
    return True


def enviar_email_reset(destinatario: str, enlace: str):
    import os
    import smtplib
    from email.mime.text import MIMEText

    # Siempre loguear el link (útil en desarrollo/producción como fallback)
    logger.info(f"Reset link para {destinatario}: {enlace}")

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_host or not smtp_user:
        logger.warning(f"SMTP no configurado. El link solo está disponible en logs.")
        return

    msg = MIMEText(
        f"Ha solicitado restablecer su contraseña.\n\n"
        f"Ingrese al siguiente enlace:\n{enlace}\n\n"
        f"Este enlace expira en {RESET_TOKEN_EXPIRE_MINUTES} minutos."
    )
    msg["Subject"] = "Recuperación de contraseña - DATCORR"
    msg["From"] = smtp_user
    msg["To"] = destinatario

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info(f"Email de reset enviado a {destinatario}")
    except Exception as e:
        logger.error(f"Error enviando email a {destinatario}: {e}")
