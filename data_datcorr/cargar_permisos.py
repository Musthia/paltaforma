from database.conexion import SessionLocal

from database.modelos import Permiso

# -----------------------------------
# SESIÓN DB
# -----------------------------------

db = SessionLocal()

# -----------------------------------
# PERMISOS INICIALES
# -----------------------------------

permisos_iniciales = [

    {
        "codigo": "CONSULTAR",
        "descripcion": "Consultar registros"
    },

    {
        "codigo": "EDITAR",
        "descripcion": "Editar registros"
    },

    {
        "codigo": "ELIMINAR",
        "descripcion": "Eliminar registros"
    },

    {
        "codigo": "EXPORTAR",
        "descripcion": "Exportar información"
    },

    {
        "codigo": "IMPORTAR",
        "descripcion": "Importar archivos"
    },

    {
        "codigo": "ADMIN_USUARIOS",
        "descripcion": "Administrar usuarios"
    }

]

# -----------------------------------
# INSERTAR PERMISOS
# -----------------------------------

print("\nCargando permisos...\n")

for permiso_data in permisos_iniciales:

    permiso_existente = (
        db.query(Permiso)
        .filter(
            Permiso.codigo ==
            permiso_data["codigo"]
        )
        .first()
    )

    if permiso_existente:

        print(
            f"[EXISTE] "
            f"{permiso_data['codigo']}"
        )

        continue

    nuevo_permiso = Permiso(
        codigo=permiso_data["codigo"],
        descripcion=permiso_data["descripcion"]
    )

    db.add(nuevo_permiso)

    print(
        f"[CREADO] "
        f"{permiso_data['codigo']}"
    )

# -----------------------------------
# COMMIT FINAL
# -----------------------------------

db.commit()

db.close()

print("\nPermisos cargados correctamente.\n")