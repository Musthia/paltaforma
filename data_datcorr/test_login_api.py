from core.api_client import ApiClient

# -----------------------------------
# CONFIGURAR CLIENTE
# -----------------------------------

api = ApiClient("http://127.0.0.1:8000")

# -----------------------------------
# LOGIN VIA FASTAPI
# -----------------------------------

resultado = api.post("/auth/login", {
    "usuario": "Musthia",
    "password": "0611"
})

# -----------------------------------
# VALIDAR RESPUESTA
# -----------------------------------

print("RESULTADO LOGIN:", resultado)

if resultado and resultado.get("success", True):

    token = resultado.get("token")
    refresh = resultado.get("refresh_token")

    api.set_tokens(token, refresh)

    print("🟢 LOGIN OK")
    print("TOKEN:", token)

else:

    print("🔴 LOGIN FALLIDO")