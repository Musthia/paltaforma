import smtplib
from email.mime.text import MIMEText

from platformcore.services.identity import IdentityService
from platformcore.config import settings
from platformcore.logger import logger


def solicitar_reset(db, email, ip=None):
    return IdentityService.solicitar_reset(db, email)


def resetear_password(db, token, nueva_password):
    return IdentityService.resetear_password(db, token, nueva_password)


def enviar_email_reset(email: str, enlace: str):
    if not settings.SMTP_HOST:
        logger.warning(f"SMTP no configurado. No se envía email a {email}")
        return
    msg = MIMEText(f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n\n{enlace}")
    msg["Subject"] = "Restablecimiento de contraseña"
    msg["From"] = settings.SMTP_USER
    msg["To"] = email
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)
    logger.info(f"Email de reset enviado a {email}")
