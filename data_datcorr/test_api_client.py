import sys
import os
import json
import urllib.request
from unittest.mock import patch, Mock
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.api_client import ApiClient
from core.api_database_client import ApiDatabaseClient
from core.api_reportes_client import ApiReportesClient


MOCK_OK = {"success": True}
MOCK_BASES = {"success": True, "bases": [{"nombre": "IPS", "tipo": "postgres"}]}
MOCK_CONSULTA = {"success": True, "total": 10, "columnas": ["id"], "registros": [[1]]}
MOCK_BUSQUEDA = {"success": True, "total": 1, "columnas": ["id"], "registros": [[1]], "base": "IPS"}
MOCK_COLUMNAS = {"success": True, "columnas": [{"nombre": "id", "tipo": "integer"}]}
MOCK_CREAR = {"success": True, "mensaje": "Creado", "registro_id": 1}
MOCK_ACTUALIZAR = {"success": True, "mensaje": "Actualizado"}
MOCK_ELIMINAR = {"success": True, "mensaje": "Eliminado"}
MOCK_AUTOCOMPLETE = {"success": True, "resultados": [[1, "test"], [2, "test2"]]}
MOCK_REGISTRO = {"success": True, "registro": {"denominacion": "test", "expediente": "exp"}}
MOCK_KPIS = {"success": True, "datos": {}}
MOCK_REFRESH_OK = {"success": True, "access_token": "new_token", "refresh_token": "new_refresh"}
MOCK_LOGIN_OK = {
    "success": True, "token": "abc", "refresh_token": "def",
    "usuario": {"id": 1, "usuario": "admin", "nombre": "Admin", "apellido": "",
                "rol": "admin", "nivel_seguridad": 10, "es_superusuario": True}
}


def _mock_urlopen(data, status=200):
    """Retorna un mock de context manager para urlopen."""
    cm = Mock()
    cm.__enter__ = Mock(return_value=cm)
    cm.__exit__ = Mock(return_value=None)
    cm.read = Mock(return_value=json.dumps(data).encode("utf-8"))
    cm.status = status
    cm.code = status
    return cm


def _mock_http_error(data, status=401):
    """Simula un HTTPError."""
    err = urllib.error.HTTPError(
        url="http://test/",
        code=status,
        msg="Error",
        hdrs={},
        fp=None
    )
    err.read = Mock(return_value=json.dumps(data).encode("utf-8"))
    err.code = status
    return err


# ===================== ApiClient =====================

def test_client_get():
    client = ApiClient("http://test:8000")
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = client.get("/test")
    assert result == MOCK_OK, f"Esperaba {MOCK_OK}, obtuvo {result}"
    print("  test_client_get OK")


def test_client_post():
    client = ApiClient("http://test:8000")
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = client.post("/test", {"key": "value"})
    assert result == MOCK_OK, f"Esperaba {MOCK_OK}, obtuvo {result}"
    print("  test_client_post OK")


def test_client_put():
    client = ApiClient("http://test:8000")
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = client.put("/test", {"key": "value"})
    assert result == MOCK_OK, f"Esperaba {MOCK_OK}, obtuvo {result}"
    print("  test_client_put OK")


def test_client_patch():
    client = ApiClient("http://test:8000")
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = client.patch("/test", {"key": "value"})
    assert result == MOCK_OK, f"Esperaba {MOCK_OK}, obtuvo {result}"
    print("  test_client_patch OK")


def test_client_delete():
    client = ApiClient("http://test:8000")
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = client.delete("/test/1")
    assert result == MOCK_OK, f"Esperaba {MOCK_OK}, obtuvo {result}"
    print("  test_client_delete OK")


def test_client_headers_with_token():
    client = ApiClient("http://test:8000")
    client.set_tokens("my_token", "my_refresh")
    assert client._headers()["Authorization"] == "Bearer my_token"
    print("  test_client_headers_with_token OK")


def test_client_login_sets_tokens():
    client = ApiClient("http://test:8000")
    with patch("core.api_client.ApiClient.post", return_value=MOCK_LOGIN_OK):
        with patch("core.api_client.ApiClient.set_tokens") as mock_set:
            client.login("admin", "pass")
            mock_set.assert_called_once_with("abc", "def")
    print("  test_client_login_sets_tokens OK")


def test_client_auto_refresh_on_401():
    client = ApiClient("http://test:8000")
    client.set_tokens("old_token", "refresh_abc")

    refresh_urlopen = _mock_urlopen(MOCK_REFRESH_OK)
    retry_urlopen = _mock_urlopen(MOCK_OK)

    urlopen_calls = [refresh_urlopen, retry_urlopen]
    urlopen_iter = Mock(side_effect=urlopen_calls)

    with patch("urllib.request.urlopen", urlopen_iter):
        err = _mock_http_error({"detail": "Token expirado"}, status=401)
        result = client._handle_http_error(err, Mock(full_url="http://test/", data=None, method="GET"))

    assert result == MOCK_OK, f"Auto-refresh deberia retornar datos OK, obtuvo {result}"
    assert client.token == "new_token", f"Token deberia actualizarse a 'new_token', obtuvo '{client.token}'"
    print("  test_client_auto_refresh_on_401 OK")


# ===================== ApiDatabaseClient =====================

def test_db_listar_bases():
    client = ApiClient("http://test:8000")
    db = ApiDatabaseClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_BASES)):
        result = db.listar_bases()
    assert result == MOCK_BASES
    print("  test_db_listar_bases OK")


def test_db_listar_tablas():
    client = ApiClient("http://test:8000")
    db = ApiDatabaseClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = db.listar_tablas("IPS")
    assert result == MOCK_OK
    print("  test_db_listar_tablas OK")


def test_db_consultar_datos():
    client = ApiClient("http://test:8000")
    db = ApiDatabaseClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_CONSULTA)):
        result = db.consultar_datos("IPS")
    assert result == MOCK_CONSULTA
    print("  test_db_consultar_datos OK")


def test_db_buscar_datos():
    client = ApiClient("http://test:8000")
    db = ApiDatabaseClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_BUSQUEDA)):
        result = db.buscar_datos("IPS", "test")
    assert result == MOCK_BUSQUEDA
    print("  test_db_buscar_datos OK")


def test_db_listar_columnas():
    client = ApiClient("http://test:8000")
    db = ApiDatabaseClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_COLUMNAS)):
        result = db.listar_columnas("IPS")
    assert result == MOCK_COLUMNAS
    print("  test_db_listar_columnas OK")


def test_db_crear_registro():
    client = ApiClient("http://test:8000")
    db = ApiDatabaseClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_CREAR)):
        result = db.crear_registro("IPS", {"nombre": "test"})
    assert result == MOCK_CREAR
    print("  test_db_crear_registro OK")


def test_db_actualizar():
    client = ApiClient("http://test:8000")
    db = ApiDatabaseClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_ACTUALIZAR)):
        result = db.actualizar("IPS", 1, {"nombre": "test2"})
    assert result == MOCK_ACTUALIZAR
    print("  test_db_actualizar OK")


def test_db_eliminar():
    client = ApiClient("http://test:8000")
    db = ApiDatabaseClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_ELIMINAR)):
        result = db.eliminar("IPS", 1)
    assert result == MOCK_ELIMINAR
    print("  test_db_eliminar OK")


# ===================== ApiReportesClient =====================

def test_db_autocomplete():
    client = ApiClient("http://test:8000")
    db = ApiDatabaseClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_AUTOCOMPLETE)):
        result = db.autocomplete("IPS", "denominacion", "test")
    assert result == MOCK_AUTOCOMPLETE
    print("  test_db_autocomplete OK")


def test_db_obtener_registro():
    client = ApiClient("http://test:8000")
    db = ApiDatabaseClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_REGISTRO)):
        result = db.obtener_registro("IPS", 1)
    assert result == MOCK_REGISTRO
    print("  test_db_obtener_registro OK")


def test_rep_listar_consultas():
    client = ApiClient("http://test:8000")
    rep = ApiReportesClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = rep.listar_consultas()
    assert result == MOCK_OK
    print("  test_rep_listar_consultas OK")


def test_rep_kpis():
    client = ApiClient("http://test:8000")
    rep = ApiReportesClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_KPIS)):
        result = rep.kpis()
    assert result == MOCK_KPIS
    print("  test_rep_kpis OK")


def test_rep_actividad_usuarios():
    client = ApiClient("http://test:8000")
    rep = ApiReportesClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = rep.actividad_usuarios("2024-01-01", "2024-12-31")
    assert result == MOCK_OK
    print("  test_rep_actividad_usuarios OK")


def test_rep_evolucion_diaria():
    client = ApiClient("http://test:8000")
    rep = ApiReportesClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = rep.evolucion_diaria("2024-01-01", "2024-12-31")
    assert result == MOCK_OK
    print("  test_rep_evolucion_diaria OK")


def test_rep_tipos_operacion():
    client = ApiClient("http://test:8000")
    rep = ApiReportesClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = rep.tipos_operacion("2024-01-01", "2024-12-31")
    assert result == MOCK_OK
    print("  test_rep_tipos_operacion OK")


def test_rep_usuarios_inactivos():
    client = ApiClient("http://test:8000")
    rep = ApiReportesClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = rep.usuarios_inactivos()
    assert result == MOCK_OK
    print("  test_rep_usuarios_inactivos OK")


def test_rep_actividad_bases():
    client = ApiClient("http://test:8000")
    rep = ApiReportesClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = rep.actividad_bases()
    assert result == MOCK_OK
    print("  test_rep_actividad_bases OK")


def test_rep_alertas():
    client = ApiClient("http://test:8000")
    rep = ApiReportesClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = rep.alertas()
    assert result == MOCK_OK
    print("  test_rep_alertas OK")


def test_rep_ejecutar_consulta():
    client = ApiClient("http://test:8000")
    rep = ApiReportesClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = rep.ejecutar_consulta("reporte_test")
    assert result == MOCK_OK
    print("  test_rep_ejecutar_consulta OK")


def test_rep_exportar_consulta():
    client = ApiClient("http://test:8000")
    rep = ApiReportesClient(client)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(MOCK_OK)):
        result = rep.exportar_consulta("reporte_test", formato="xlsx")
    assert result == MOCK_OK
    print("  test_rep_exportar_consulta OK")


if __name__ == "__main__":
    try:
        test_client_get()
        test_client_post()
        test_client_put()
        test_client_patch()
        test_client_delete()
        test_client_headers_with_token()
        test_client_login_sets_tokens()
        test_client_auto_refresh_on_401()
        test_db_listar_bases()
        test_db_listar_tablas()
        test_db_consultar_datos()
        test_db_buscar_datos()
        test_db_listar_columnas()
        test_db_crear_registro()
        test_db_actualizar()
        test_db_eliminar()
        test_db_autocomplete()
        test_db_obtener_registro()
        test_rep_listar_consultas()
        test_rep_kpis()
        test_rep_actividad_usuarios()
        test_rep_evolucion_diaria()
        test_rep_tipos_operacion()
        test_rep_usuarios_inactivos()
        test_rep_actividad_bases()
        test_rep_alertas()
        test_rep_ejecutar_consulta()
        test_rep_exportar_consulta()
        print("\n=== TODAS LAS PRUEBAS PASARON ===")
    except AssertionError as e:
        print(f"\nFALLO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR INESPERADO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)