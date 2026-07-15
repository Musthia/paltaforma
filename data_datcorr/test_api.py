import requests

BASE_URL = "http://127.0.0.1:8000"

def test_get_usuarios():
    url = f"{BASE_URL}/usuarios?page=1&limit=20"

    response = requests.get(url)

    print("STATUS:", response.status_code)
    print("DATA:", response.json())

test_get_usuarios()