"""
Migrate roles, permissions and user-permission assignments
from datcorr database to platform database.

Usage: python migrate_roles_permisos.py
"""
import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("migrate")


def get_datcorr_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)


def get_platform_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('PLATFORM_DB_USER', os.getenv('DB_USER'))}"
        f":{os.getenv('PLATFORM_DB_PASSWORD', os.getenv('DB_PASSWORD'))}"
        f"@{os.getenv('PLATFORM_DB_HOST', os.getenv('DB_HOST'))}"
        f":{os.getenv('PLATFORM_DB_PORT', os.getenv('DB_PORT'))}"
        f"/{os.getenv('PLATFORM_DB_NAME', 'platform')}"
    )
    return create_engine(url)


def migrate_roles(dc, pc):
    log.info("=== Migrando roles ===")
    rows = dc.execute(text("SELECT id, nombre, descripcion, nivel_minimo FROM roles ORDER BY id")).fetchall()
    for row in rows:
        existing = pc.execute(
            text("SELECT id FROM platform_roles WHERE name = :name"),
            {"name": row.nombre}
        ).fetchone()
        if existing:
            log.info(f"  Rol '{row.nombre}' ya existe (id={existing[0]}), saltando.")
        else:
            pc.execute(
                text("INSERT INTO platform_roles (name, description, nivel_minimo) VALUES (:name, :desc, :nivel)"),
                {"name": row.nombre, "desc": row.descripcion, "nivel": row.nivel_minimo}
            )
            log.info(f"  Rol '{row.nombre}' creado.")
    pc.commit()
    log.info("Roles migrados OK.")


def migrate_permissions(dc, pc):
    log.info("=== Migrando permisos ===")
    rows = dc.execute(text("SELECT id, codigo, descripcion FROM permisos ORDER BY id")).fetchall()
    for row in rows:
        existing = pc.execute(
            text("SELECT id FROM platform_permissions WHERE code = :code"),
            {"code": row.codigo}
        ).fetchone()
        if existing:
            log.info(f"  Permiso '{row.codigo}' ya existe (id={existing[0]}), saltando.")
        else:
            pc.execute(
                text("INSERT INTO platform_permissions (code, description) VALUES (:code, :desc)"),
                {"code": row.codigo, "desc": row.descripcion}
            )
            log.info(f"  Permiso '{row.codigo}' creado.")
    pc.commit()
    log.info("Permisos migrados OK.")


def migrate_user_permissions(dc, pc):
    log.info("=== Migrando asignaciones usuario-permiso ===")
    rows = dc.execute(text("""
        SELECT up.usuario_id, p.codigo, u.usuario
        FROM usuarios_permisos up
        JOIN permisos p ON p.id = up.permiso_id
        JOIN usuarios u ON u.id = up.usuario_id
        ORDER BY up.usuario_id
    """)).fetchall()

    # build username->platform_id map
    plat_users = pc.execute(
        text("SELECT id, username FROM platform_users")
    ).fetchall()
    username_to_id = {u.username: u.id for u in plat_users}

    count = 0
    for row in rows:
        username = row.usuario
        platform_user_id = username_to_id.get(username)
        if not platform_user_id:
            log.warning(f"  Usuario '{username}' (id={row.usuario_id}) no encontrado en platform_users, saltando.")
            continue
        perm = pc.execute(
            text("SELECT id FROM platform_permissions WHERE code = :code"),
            {"code": row.codigo}
        ).fetchone()
        if not perm:
            log.warning(f"  Permiso '{row.codigo}' no existe en platform, saltando.")
            continue
        existing = pc.execute(
            text("SELECT id FROM platform_user_permissions WHERE user_id = :uid AND permission_id = :pid"),
            {"uid": platform_user_id, "pid": perm[0]}
        ).fetchone()
        if existing:
            continue
        pc.execute(
            text("INSERT INTO platform_user_permissions (user_id, permission_id) VALUES (:uid, :pid)"),
            {"uid": platform_user_id, "pid": perm[0]}
        )
        count += 1
    pc.commit()
    log.info(f"Asignaciones migradas: {count} nuevas.")


def main():
    dc_engine = get_datcorr_engine()
    pc_engine = get_platform_engine()

    with dc_engine.connect() as dc:
        with pc_engine.connect() as pc:
            with pc.begin():
                migrate_roles(dc, pc)
            with pc.begin():
                migrate_permissions(dc, pc)
            with pc.begin():
                migrate_user_permissions(dc, pc)

    log.info("Migración completada.")


if __name__ == "__main__":
    main()
