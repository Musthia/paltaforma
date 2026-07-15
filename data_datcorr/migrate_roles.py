"""
Migración: Crear tablas roles y usuarios_roles, migrar datos existentes.

Uso: python migrate_roles.py
"""
from database.conexion import SessionLocal, engine
from database.modelos_roles import Rol, UsuarioRol
from database.modelos import Usuario
from sqlalchemy import text

ROLES_POR_DEFECTO = [
    {"nombre": "Administrador", "descripcion": "Acceso completo al sistema", "nivel_minimo": 10},
    {"nombre": "Supervisor", "descripcion": "Supervisión y gestión de usuarios", "nivel_minimo": 5},
    {"nombre": "Operador", "descripcion": "Operaciones diarias del sistema", "nivel_minimo": 3},
    {"nombre": "Consulta", "descripcion": "Solo lectura de datos", "nivel_minimo": 1},
]


def crear_tablas():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(50) UNIQUE NOT NULL,
                descripcion VARCHAR(255),
                nivel_minimo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS usuarios_roles (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                rol_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
    print("Tablas roles y usuarios_roles creadas/verificadas.")


def insertar_roles_base():
    db = SessionLocal()
    try:
        existentes = {r.nombre for r in db.query(Rol).all()}
        for r in ROLES_POR_DEFECTO:
            if r["nombre"] not in existentes:
                db.add(Rol(**r))
                print(f"  + Rol creado: {r['nombre']}")
        db.commit()
    finally:
        db.close()


def migrar_roles_existentes():
    db = SessionLocal()
    try:
        usuarios_con_rol = db.query(Usuario).filter(
            Usuario.rol.isnot(None),
            Usuario.rol != ""
        ).all()

        roles_map = {r.nombre: r for r in db.query(Rol).all()}

        for u in usuarios_con_rol:
            rol_str = u.rol.strip()
            if not rol_str:
                continue
            rol = roles_map.get(rol_str)
            if not rol:
                print(f"  ? Rol '{rol_str}' no encontrado en roles por defecto, creándolo...")
                rol = Rol(nombre=rol_str, descripcion=f"Rol migrado: {rol_str}")
                db.add(rol)
                db.flush()
                roles_map[rol_str] = rol

            existe = db.query(UsuarioRol).filter(
                UsuarioRol.usuario_id == u.id,
                UsuarioRol.rol_id == rol.id
            ).first()
            if not existe:
                db.add(UsuarioRol(usuario_id=u.id, rol_id=rol.id))
                print("  > Usuario '%s' -> rol '%s'" % (u.usuario, rol.nombre))

        db.commit()
        print(f"\nMigrados {len(usuarios_con_rol)} usuarios a usuarios_roles.")
    finally:
        db.close()


def main():
    print("=== Migración: Normalización de Roles ===\n")
    crear_tablas()
    insertar_roles_base()
    migrar_roles_existentes()
    print("\nMigración completada.")


if __name__ == "__main__":
    main()
