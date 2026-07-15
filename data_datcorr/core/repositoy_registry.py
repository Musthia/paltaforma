# -----------------------------------
# REPOSITORY REGISTRY
# -----------------------------------

REPOSITORIES = {
    # SEGURIDAD (POSTGRESQL)
    "usuarios": "postgresql",
    "permisos": "postgresql",
    "usuarios_permisos": "postgresql",
    "refresh_tokens": "postgresql",
    "token_blacklist": "postgresql",
    "auditoria": "postgresql",

    # MÓDULOS FUNCIONALES (EN MIGRACIÓN)
    "catastro": "pending",
    "modulo_2": "pending",
    "modulo_3": "pending",
}

# -----------------------------------

def get_repo_backend(nombre_modulo: str) -> str:
    return REPOSITORIES.get(nombre_modulo, "unknown")


def is_postgresql(nombre_modulo: str) -> bool:
    return get_repo_backend(nombre_modulo) == "postgresql"