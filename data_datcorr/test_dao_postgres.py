import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.registry import initialize_postgres, db_registry
from sqlalchemy import text


def test_conexion():
    print("=== 1. Inicializar engine PostgreSQL ===")
    engine = initialize_postgres()
    assert engine is not None, "Engine no debería ser None"
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.scalar()
        print(f"   Conectado a: {db_name}")
        assert db_name == "datcorr", f"Esperaba 'datcorr', obtuve '{db_name}'"
    print("   OK")


def test_listar_schemas():
    print("\n=== 2. Listar schemas disponibles ===")
    schemas = ["escribania", "igpj", "igpj_listado_nuevo", "ips", "maternidad", "pediatrico"]
    conn = db_registry.get_engine().connect()
    for schema in schemas:
        result = conn.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = :s)"),
            {"s": schema}
        )
        exists = result.scalar()
        print(f"   Schema '{schema}': {'OK' if exists else 'FALTA'}")
        assert exists, f"Schema '{schema}' no encontrado"
    conn.close()
    print("   OK")


def test_utils_organismos():
    print("\n=== 3. Verificar utils.organismos ===")
    from utils.organismos import MAPA_SCHEMA, MAPEO_COLUMNAS_POR_ORGANISMO

    assert "IPS" in MAPA_SCHEMA
    assert MAPA_SCHEMA["IPS"] == "ips"
    assert MAPA_SCHEMA["ESCRIBANIA"] == "escribania"
    assert MAPA_SCHEMA["PEDIATRICO"] == "pediatrico"
    assert len(MAPA_SCHEMA) == 7

    assert "PEDIATRICO" in MAPEO_COLUMNAS_POR_ORGANISMO
    cols = MAPEO_COLUMNAS_POR_ORGANISMO["PEDIATRICO"]
    assert "caja" in cols
    assert "denominacion" in cols
    print(f"   PEDIATRICO columnas ({len(cols)}): {cols}")
    print("   OK")

    from utils.organismos import schema_para_base, columnas_para_base
    assert schema_para_base("IPS") == "ips"
    assert len(columnas_para_base("ESCRIBANIA")) == 9
    print("   Funciones schema_para_base y columnas_para_base OK")


if __name__ == "__main__":
    try:
        test_conexion()
        test_listar_schemas()
        test_utils_organismos()
        print("\n=== TODAS LAS PRUEBAS PASARON ===")
    except AssertionError as e:
        print(f"\nFALLO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR INESPERADO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)