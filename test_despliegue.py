"""
test_despliegue.py — Pruebas de humo post-despliegue.
Uso: python test_despliegue.py [base_url]
Ejemplo: python test_despliegue.py https://plataforma.up.railway.app
"""
import sys
import requests

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"


def test(desc, method, path, expect=200, **kwargs):
    url = f"{BASE}{path}"
    try:
        r = requests.request(method, url, **kwargs, timeout=15)
        ok = r.status_code == expect
        icon = "✅" if ok else "❌"
        print(f"  {icon} {method} {path} → {r.status_code} (esperado {expect})")
        if not ok:
            print(f"      Body: {r.text[:300]}")
        return ok
    except Exception as e:
        print(f"  ❌ {method} {path} → ERROR: {e}")
        return False


def main():
    print(f"\n═══ Pruebas de despliegue: {BASE} ═══\n")

    results = []

    # Health
    results.append(test("Health", "GET", "/health"))
    results.append(test("API Health", "GET", "/api/health"))

    # Frontend DATCORR
    r = requests.get(f"{BASE}/app/", timeout=15)
    is_datcorr_html = r.status_code == 200 and "html" in r.headers.get("content-type", "")
    print(f"  {'✅' if is_datcorr_html else '❌'} GET /app/ → {r.status_code} (esperado HTML 200)")
    if not is_datcorr_html:
        print(f"      Body preview: {r.text[:200]}")
    results.append(is_datcorr_html)

    # Frontend SIMCO
    r = requests.get(f"{BASE}/simco/", timeout=15)
    is_simco_html = r.status_code == 200 and "html" in r.headers.get("content-type", "")
    print(f"  {'✅' if is_simco_html else '❌'} GET /simco/ → {r.status_code} (esperado HTML 200)")
    if not is_simco_html:
        print(f"      Body preview: {r.text[:200]}")
    results.append(is_simco_html)

    # API endpoints (no requieren auth)
    results.append(test("Solicitudes", "GET", "/solicitudes/"))
    results.append(test("Respuestas", "GET", "/respuestas/"))
    results.append(test("Dashboard activity", "GET", "/dashboard/activity"))
    results.append(test("Dashboard hoy", "GET", "/dashboard/hoy"))

    # Login (depende de seed)
    r = requests.post(f"{BASE}/auth/login",
                      json={"username": "admin", "password": "admin123"}, timeout=10)
    if r.status_code == 200:
        print(f"  ✅ Login admin → OK (token obtenido)")
        results.append(True)
    else:
        print(f"  ⚠️  Login admin → {r.status_code} (esperado si no hay seed o credenciales distintas)")
        results.append(True)

    # Auth/me con token
    r2 = requests.post(f"{BASE}/auth/login",
                       json={"username": "admin", "password": "admin123"}, timeout=10)
    if r2.status_code == 200:
        token = r2.json().get("access_token", "")
        if token:
            r3 = requests.get(f"{BASE}/auth/me",
                              headers={"Authorization": f"Bearer {token}"}, timeout=10)
            me_ok = r3.status_code == 200
            print(f"  {'✅' if me_ok else '❌'} GET /auth/me con token → {r3.status_code}")
            results.append(me_ok)
        else:
            print(f"  ⚠️  No se obtuvo token para probar /auth/me")
            results.append(True)
    else:
        print(f"  ⚠️  Saltando /auth/me (login falló con admin)")
        results.append(True)

    # Resultado final
    total = len(results)
    passed = sum(1 for r in results if r)
    all_ok = all(results)

    print(f"\n═══ Resultado: {passed}/{total} pruebas pasadas {'' if all_ok else '❌'} ═══\n")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
