from app.db.session import engine

try:
    conn = engine.connect()
    print("Conectado correctamente a PostgreSQL")
    conn.close()

except Exception as e:
    print("ERROR:")
    print(e)