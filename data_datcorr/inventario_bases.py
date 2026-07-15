import sqlite3
import os

CARPETA = "bases_g"

for archivo in os.listdir(CARPETA):

    if not archivo.endswith(".db"):
        continue

    ruta = os.path.join(CARPETA, archivo)

    print("\n" + "=" * 80)
    print(f"BASE: {archivo}")
    print("=" * 80)

    conn = sqlite3.connect(ruta)

    cur = conn.cursor()

    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)

    tablas = cur.fetchall()

    for (tabla,) in tablas:

        print(f"\nTABLA: {tabla}")

        try:

            cur.execute(f"SELECT COUNT(*) FROM {tabla}")
            cantidad = cur.fetchone()[0]

            print(f"REGISTROS: {cantidad}")

        except:
            pass

        try:

            cur.execute(f"PRAGMA table_info({tabla})")

            columnas = cur.fetchall()

            print("COLUMNAS:")

            for col in columnas:

                print(
                    f"   {col[1]} ({col[2]})"
                )

        except:
            pass

    conn.close()