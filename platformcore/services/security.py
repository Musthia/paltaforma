from sqlalchemy.orm import Session
from sqlalchemy import or_

from platformcore.security import hash_password
from platformcore.logger import logger
from platformcore.exceptions import NotFoundError, ConflictError
from platformcore.models.identity import PlatformUser
from platformcore.models.security import PlatformRole, PlatformPermission, PlatformUserRole, PlatformUserPermission


class UserService:

    @staticmethod
    def list_users(
        db: Session,
        page: int = 1,
        limit: int = 20,
        search: str = "",
        role: str = "",
        is_active: bool | None = None,
        sort_by: str = "id",
        order: str = "asc",
        include_inactive: bool = False,
    ):
        query = db.query(PlatformUser)

        if not include_inactive:
            query = query.filter(PlatformUser.is_active == True)

        if search:
            texto = f"%{search}%"
            query = query.filter(
                or_(
                    PlatformUser.full_name.ilike(texto),
                    PlatformUser.username.ilike(texto),
                    PlatformUser.email.ilike(texto),
                )
            )

        if role:
            query = query.filter(PlatformUser.role == role)

        if is_active is not None:
            query = query.filter(PlatformUser.is_active == is_active)

        sort_columns = {
            "id": PlatformUser.id,
            "username": PlatformUser.username,
            "full_name": PlatformUser.full_name,
            "role": PlatformUser.role,
            "is_active": PlatformUser.is_active,
            "nivel_seguridad": PlatformUser.nivel_seguridad,
        }

        col = sort_columns.get(sort_by, PlatformUser.id)
        query = query.order_by(col.desc() if order == "desc" else col.asc())

        total = query.count()
        pages = max(1, (total + limit - 1) // limit)
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()

        return {"users": users, "total": total, "pages": pages, "page": page, "limit": limit}

    @staticmethod
    def get_user(db: Session, user_id: int):
        user = db.query(PlatformUser).filter(PlatformUser.id == user_id).first()
        if not user:
            raise NotFoundError("Usuario no encontrado.")
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(PlatformUser).filter(PlatformUser.username == username).first()

    @staticmethod
    def create_user(db: Session, data) -> PlatformUser:
        if len(data.password) < 4:
            raise ConflictError("Password demasiado corta.")

        exists = db.query(PlatformUser).filter(PlatformUser.username == data.username).first()
        if exists:
            raise ConflictError("Usuario ya existe.")

        if data.email:
            email_exists = db.query(PlatformUser).filter(PlatformUser.email == data.email).first()
            if email_exists:
                raise ConflictError("El correo ya está registrado.")

        user = PlatformUser(
            username=data.username,
            full_name=data.full_name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
            nivel_seguridad=data.nivel_seguridad,
            is_active=data.is_active,
            is_superuser=getattr(data, "is_superuser", False),
        )
        db.add(user)
        db.flush()

        if data.role:
            RoleService.assign_role_to_user(db, user.id, data.role)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, data) -> PlatformUser:
        user = db.query(PlatformUser).filter(PlatformUser.id == user_id).first()
        if not user:
            raise NotFoundError("Usuario no encontrado.")

        if data.username and data.username != user.username:
            exists = db.query(PlatformUser).filter(
                PlatformUser.username == data.username,
                PlatformUser.id != user_id,
            ).first()
            if exists:
                raise ConflictError("Nombre de usuario ya existe.")
            user.username = data.username

        if data.email and data.email != user.email:
            exists = db.query(PlatformUser).filter(
                PlatformUser.email == data.email,
                PlatformUser.id != user_id,
            ).first()
            if exists:
                raise ConflictError("El correo ya está registrado.")
            user.email = data.email

        if data.full_name is not None:
            user.full_name = data.full_name
        if data.role is not None:
            user.role = data.role
            RoleService.assign_role_to_user(db, user.id, data.role)
        if data.nivel_seguridad is not None:
            user.nivel_seguridad = data.nivel_seguridad
        if data.is_active is not None:
            user.is_active = data.is_active
        if data.password:
            if len(data.password) < 4:
                raise ConflictError("Password demasiado corta.")
            user.password_hash = hash_password(data.password)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> PlatformUser:
        user = db.query(PlatformUser).filter(PlatformUser.id == user_id).first()
        if not user:
            raise NotFoundError("Usuario no encontrado.")
        if user.is_superuser:
            raise ConflictError("No se puede desactivar un superusuario.")
        user.is_active = False
        db.commit()
        return user

    @staticmethod
    def reactivate_user(db: Session, user_id: int) -> PlatformUser:
        user = db.query(PlatformUser).filter(PlatformUser.id == user_id).first()
        if not user:
            raise NotFoundError("Usuario no encontrado.")
        user.is_active = True
        db.commit()
        return user


class RoleService:

    @staticmethod
    def list_roles(db: Session):
        return db.query(PlatformRole).order_by(PlatformRole.nivel_minimo.desc()).all()

    @staticmethod
    def get_role_by_name(db: Session, name: str):
        return db.query(PlatformRole).filter(PlatformRole.name == name).first()

    @staticmethod
    def assign_role_to_user(db: Session, user_id: int, role_name: str):
        role = RoleService.get_role_by_name(db, role_name)
        if not role:
            logger.warning(f"Rol '{role_name}' no encontrado, usando default.")
            role = RoleService.get_role_by_name(db, "consulta")
            if not role:
                return

        existing = db.query(PlatformUserRole).filter(PlatformUserRole.user_id == user_id).first()
        if existing:
            existing.role_id = role.id
        else:
            db.add(PlatformUserRole(user_id=user_id, role_id=role.id))
        db.flush()

    @staticmethod
    def get_user_roles(db: Session, user_id: int):
        registros = db.query(PlatformUserRole).filter(PlatformUserRole.user_id == user_id).all()
        roles = []
        for ur in registros:
            role = db.query(PlatformRole).filter(PlatformRole.id == ur.role_id).first()
            if role:
                roles.append(role)
        return roles


class PermissionService:

    @staticmethod
    def list_permissions(db: Session):
        return db.query(PlatformPermission).order_by(PlatformPermission.code).all()

    @staticmethod
    def get_user_permissions(db: Session, user_id: int):
        permisos_db = (
            db.query(PlatformPermission.code)
            .join(PlatformUserPermission, PlatformUserPermission.permission_id == PlatformPermission.id)
            .filter(PlatformUserPermission.user_id == user_id)
            .all()
        )
        return [p[0] for p in permisos_db]

    @staticmethod
    def user_has_permission(db: Session, user_id: int, permission_code: str) -> bool:
        user = db.query(PlatformUser).filter(PlatformUser.id == user_id).first()
        if user and user.is_superuser:
            return True
        return (
            db.query(PlatformUserPermission)
            .join(PlatformPermission)
            .filter(
                PlatformUserPermission.user_id == user_id,
                PlatformPermission.code == permission_code,
            )
            .first()
        ) is not None
