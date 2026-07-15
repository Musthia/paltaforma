from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    text,
    ForeignKey
)

from sqlalchemy.orm import (
    declarative_base,
    relationship
)

from sqlalchemy.orm import relationship

from database.modelos_auditoria import (
    Auditoria
)

from database.conexion import Base

from database.modelos_refresh import (
    RefreshToken
)
from database.modelos_reset import (
    PasswordResetToken
)

from database.modelos_roles import (
    Rol,
    UsuarioRol
)

# -----------------------------------
# TABLA USUARIOS
# -----------------------------------

class Usuario(Base):

    __tablename__ = "usuarios"

    # -----------------------------------
    # CAMPOS
    # -----------------------------------
    

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nombre = Column(
        String(100),
        nullable=False
    )

    apellido = Column(
        String(100),
        nullable=False
    )

    usuario = Column(
        String(50),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    rol = Column(
        String(50),
        nullable=False
    )

    nivel_seguridad = Column(
        Integer,
        default=1
    )

    activo = Column(
        Boolean,
        default=True
    )

    es_superusuario = Column(
        Boolean,
        default=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=True
    )

    ultimo_login = Column(
        TIMESTAMP,
        nullable=True
    )

    ultimo_cambio_password = Column(
        TIMESTAMP,
        nullable=True
    )

    intentos_fallidos = Column(
        Integer,
        default=0
    )

    bloqueado_hasta = Column(
        TIMESTAMP,
        nullable=True
    )

    fecha_creacion = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )

    fecha_actualizacion = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    usuario_permisos = relationship(
        "UsuarioPermiso",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    roles = relationship(
        "UsuarioRol",
        cascade="all, delete-orphan"
    )
    
# -----------------------------------
# TABLA PERMISOS
# -----------------------------------

class Permiso(Base):

    __tablename__ = "permisos"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    codigo = Column(
        String(100),
        unique=True,
        nullable=False
    )

    descripcion = Column(
        String(255),
        nullable=False
    )

# -----------------------------------
# TABLA RELACIÓN
# USUARIOS ↔ PERMISOS
# -----------------------------------

class UsuarioPermiso(Base):

    __tablename__ = "usuarios_permisos"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    permiso_id = Column(
        Integer,
        ForeignKey("permisos.id"),
        nullable=False
    )

    # -----------------------------------
    # RELACIONES ORM
    # -----------------------------------

    usuario = relationship(
        "Usuario",
        back_populates="usuario_permisos"
    )

    permiso = relationship(
        "Permiso"
    )