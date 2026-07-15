import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from jose import JWTError

from platformcore.config import settings
from platformcore.jwt import decode_token_payload
from platformcore.database import SessionLocal
from platformcore.logger import logger


class JWTMiddleware(BaseHTTPMiddleware):

    public_paths = {
        "/docs",
        "/openapi.json",
        "/redoc",
        "/auth/login",
        "/auth/refresh",
        "/auth/forgot-password",
        "/auth/reset-password",
        "/health",
        "/",
    }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/")

        if request.method == "OPTIONS":
            return await call_next(request)

        if path in self.public_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            request.state.user = None
            return await call_next(request)

        try:
            parts = auth_header.split()
            if len(parts) != 2:
                return JSONResponse(status_code=401, content={"detail": "Token inválido"})

            scheme, token = parts
            if scheme.lower() != "bearer":
                return JSONResponse(status_code=401, content={"detail": "Esquema inválido"})

            payload = decode_token_payload(token)
            if not payload:
                return JSONResponse(status_code=401, content={"detail": "Token inválido o expirado"})

            jti = payload.get("jti")
            username = payload.get("sub")

            # blacklist check
            db = SessionLocal()
            try:
                from platformcore.services.identity import IdentityService
                if jti and IdentityService.is_token_blacklisted(db, jti):
                    logger.warning(f"JWT BLOQUEADO | user={username} | jti={jti}")
                    return JSONResponse(status_code=401, content={"detail": "Token revocado globalmente"})

                # inactivity check
                from platformcore.models.identity import PlatformUser, PlatformRefreshToken
                from datetime import datetime

                user = db.query(PlatformUser).filter(PlatformUser.username == username).first()
                if user:
                    rt = db.query(PlatformRefreshToken).filter(
                        PlatformRefreshToken.user_id == user.id,
                        PlatformRefreshToken.revoked == False,
                    ).order_by(PlatformRefreshToken.id.desc()).first()

                    if rt:
                        ultima = rt.last_activity or rt.created_at
                        if ultima and (datetime.now() - ultima).total_seconds() > settings.INACTIVITY_MINUTES * 60:
                            rt.revoked = True
                            db.commit()
                            from platformcore.services.audit import AuditService
                            AuditService.record(
                                db=db, username=username, action="SESSION_EXPIRED_INACTIVITY",
                                entity="auth", detail=f"Inactividad > {settings.INACTIVITY_MINUTES} min",
                                token_jti=jti,
                            )
                            return JSONResponse(
                                status_code=401,
                                content={"detail": "Sesión expirada por inactividad."}
                            )
                        rt.last_activity = datetime.now()
                        db.commit()

                request.state.user = {
                    "username": username,
                    "user_id": payload.get("user_id"),
                    "role": payload.get("role"),
                    "nivel": payload.get("nivel"),
                    "is_superuser": payload.get("is_superuser", False),
                    "jti": jti,
                }
            finally:
                db.close()

        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Token inválido o expirado"})
        except Exception as e:
            logger.error(f"ERROR JWT MIDDLEWARE: {e}")
            return JSONResponse(status_code=500, content={"detail": "Error interno de autenticación"})

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, max_attempts: int = 5, window_seconds: int = 300, ban_seconds: int = 900):
        super().__init__(app)
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.ban_seconds = ban_seconds
        self.attempts: dict = defaultdict(list)
        self.banned: dict = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # check ban
        if client_ip in self.banned:
            if now - self.banned[client_ip] < self.ban_seconds:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Demasiados intentos. IP bloqueada temporalmente."},
                )
            else:
                del self.banned[client_ip]

        response = await call_next(request)

        # rate-limit solo en login
        if request.url.path.rstrip("/") == "/auth/login" and response.status_code == 401:
            self.attempts[client_ip] = [
                t for t in self.attempts[client_ip]
                if now - t < self.window_seconds
            ]
            self.attempts[client_ip].append(now)

            if len(self.attempts[client_ip]) >= self.max_attempts:
                self.banned[client_ip] = now
                logger.warning(f"RATE LIMIT BAN | ip={client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Demasiados intentos. IP bloqueada temporalmente."},
                )

        return response
