from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from jose import jwt, JWTError

from backend.database.conexion import SessionLocal
from backend.security.jwt_manager import SECRET_KEY, ALGORITHM, INACTIVITY_MINUTES

from backend.services.blacklist_service import token_esta_revocado
from backend.services.auditoria_service import registrar_auditoria
from backend.core.logger import logger



class JWTMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        path = request.url.path.rstrip("/")

        # ===================================
        # 1. PERMITIR PREFLIGHT CORS (CRÍTICO)
        # ===================================

        if request.method == "OPTIONS":
            return await call_next(request)

        # ===================================
        # 2. RUTAS PÚBLICAS
        # ===================================

        public_paths = {
            "/docs",
            "/openapi.json",
            "/auth/login",
            "/auth/refresh",
        }

        if request.url.path in public_paths:
            return await call_next(request)

        # ===================================
        # 3. EXTRAER TOKEN (SEGURIDAD ROBUSTA)
        # ===================================

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            # No hay token → dejar pasar o bloquear según política
            request.state.user = None
            return await call_next(request)

        try:
            # ===================================
            # 4. VALIDAR FORMATO BEARER
            # ===================================

            parts = auth_header.split()

            if len(parts) != 2:
                logger.warning("JWT FORMATO INVÁLIDO")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token inválido"}
                )

            scheme, token = parts

            if scheme.lower() != "bearer":
                logger.warning("ESQUEMA JWT INVÁLIDO")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Esquema inválido"}
                )

            # ===================================
            # 5. DECODIFICAR JWT
            # ===================================

            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            jti = payload.get("jti")
            usuario = payload.get("sub")

            # ===================================
            # 6. DB SESSION SEGURA
            # ===================================

            db = SessionLocal()

            try:

                # ===================================
                # 7. BLACKLIST GLOBAL CHECK
                # ===================================

                if jti and token_esta_revocado(db, jti):

                    logger.critical(
                        f"JWT BLOQUEADO | usuario={usuario} | jti={jti}"
                    )

                    registrar_auditoria(
                        db=db,
                        usuario=usuario,
                        accion="TOKEN_REVOKED_GLOBAL",
                        tabla="auth",
                        detalle="Intento de acceso con token revocado"
                    )

                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Token revocado globalmente"}
                    )

                # ===================================
                # 8. INACTIVITY CHECK + TRACKING
                # ===================================

                from database.modelos import Usuario
                from database.modelos_refresh import RefreshToken

                user = db.query(Usuario).filter(Usuario.usuario == usuario).first()
                if user:
                    rt = db.query(RefreshToken).filter(
                        RefreshToken.usuario_id == user.id,
                        RefreshToken.revoked == False
                    ).order_by(RefreshToken.id.desc()).first()

                    if rt:
                        ultima = rt.last_activity or rt.created_at
                        if (datetime.now() - ultima).total_seconds() > INACTIVITY_MINUTES * 60:
                            rt.revoked = True
                            db.commit()
                            registrar_auditoria(
                                db=db, usuario=usuario, accion="SESSION_EXPIRED_INACTIVITY",
                                tabla="auth", detalle=f"Inactividad > {INACTIVITY_MINUTES} min",
                                token_jti=jti
                            )
                            return JSONResponse(
                                status_code=401,
                                content={"detail": "Sesión expirada por inactividad."}
                            )

                        rt.last_activity = datetime.now()
                        db.commit()

                # ===================================
                # 9. INYECTAR USUARIO EN REQUEST
                # ===================================

                request.state.user = {
                    "usuario": usuario,
                    "nivel": payload.get("nivel"),
                    "superusuario": payload.get("superusuario", False),
                    "jti": jti
                }

            finally:
                db.close()

        # ===================================
        # 10. TOKEN INVÁLIDO
        # ===================================

        except JWTError:
            logger.warning("JWT MALFORMADO O EXPIRADO")

            return JSONResponse(
                status_code=401,
                content={"detail": "Token inválido o expirado"}
            )

        # ===================================
        # 11. ERROR INESPERADO
        # ===================================

        except Exception as e:
            logger.error(f"ERROR JWT MIDDLEWARE: {e}")

            return JSONResponse(
                status_code=500,
                content={"detail": "Error interno de autenticación"}
            )

        # ===================================
        # 12. CONTINUAR REQUEST
        # ===================================

        return await call_next(request)