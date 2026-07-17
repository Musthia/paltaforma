import json
import urllib.parse
import urllib.request
import urllib.error


class ApiClient:

    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.refresh_token = None

    def set_tokens(self, token, refresh_token=None):
        self.token = token
        self.refresh_token = refresh_token

    def _headers(self):
        headers = {
            "Content-Type": "application/json"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    def login(self, usuario, password):
        data = {"usuario": usuario, "password": password}
        result = self.post("/auth/login", data)
        if result.get("success"):
            self.set_tokens(
                result.get("token"),
                result.get("refresh_token")
            )
        return result

    def _try_refresh(self):
        if not self.refresh_token:
            return False
        try:
            req = urllib.request.Request(
                self.base_url + "/auth/refresh",
                data=json.dumps({"refresh_token": self.refresh_token}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("success"):
                self.token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                return True
        except Exception:
            pass
        self.token = None
        self.refresh_token = None
        return False

    def get(self, url, params=None):
        full_url = self.base_url + url
        if params:
            query = urllib.parse.urlencode(params, doseq=True)
            full_url += "?" + query
        req = urllib.request.Request(full_url, headers=self._headers(), method="GET")
        return self._open(req)

    def get_raw(self, url, params=None):
        full_url = self.base_url + url
        if params:
            query = urllib.parse.urlencode(params, doseq=True)
            full_url += "?" + query
        req = urllib.request.Request(full_url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            return self._handle_raw_http_error(e, req)
        except Exception:
            return {
                "success": False,
                "mensaje": "Error de conexión con el servidor"
            }

    def _handle_raw_http_error(self, error, original_req):
        status = error.code
        try:
            body = error.read().decode("utf-8")
            data = json.loads(body)
        except Exception:
            data = {"success": False, "mensaje": f"HTTP {status}"}

        if status == 401 and self.refresh_token:
            if self._try_refresh():
                new_req = urllib.request.Request(
                    original_req.full_url,
                    data=original_req.data,
                    headers=self._headers(),
                    method=original_req.method
                )
                return self.get_raw(new_req.full_url)

        if not isinstance(data, dict) or "success" not in data:
            detail = data.get("detail") if isinstance(data, dict) else None
            if detail is None:
                detail = data if isinstance(data, str) else f"HTTP {status}"
            elif isinstance(detail, list):
                detail = "; ".join(
                    d.get("msg", str(d)) for d in detail if isinstance(d, dict)
                ) or str(detail)
            data = {
                "success": False,
                "mensaje": detail,
                "status": status
            }

        return data

    def post(self, url, data):
        req = urllib.request.Request(
            self.base_url + url,
            data=json.dumps(data).encode("utf-8"),
            headers=self._headers(),
            method="POST"
        )
        return self._open(req)

    def put(self, url, data):
        req = urllib.request.Request(
            self.base_url + url,
            data=json.dumps(data).encode("utf-8"),
            headers=self._headers(),
            method="PUT"
        )
        return self._open(req)

    def patch(self, url, data):
        req = urllib.request.Request(
            self.base_url + url,
            data=json.dumps(data).encode("utf-8"),
            headers=self._headers(),
            method="PATCH"
        )
        return self._open(req)

    def delete(self, url):
        req = urllib.request.Request(
            self.base_url + url,
            headers=self._headers(),
            method="DELETE"
        )
        return self._open(req)

    def _open(self, req):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body) if body else {"success": True}
        except urllib.error.HTTPError as e:
            return self._handle_http_error(e, req)
        except Exception:
            return {
                "success": False,
                "mensaje": "Error de conexión con el servidor"
            }

    def _handle_http_error(self, error, original_req):
        status = error.code
        try:
            body = error.read().decode("utf-8")
            data = json.loads(body)
        except Exception:
            data = {"success": False, "mensaje": f"HTTP {status}"}

        if status == 401 and self.refresh_token:
            if self._try_refresh():
                new_req = urllib.request.Request(
                    original_req.full_url,
                    data=original_req.data,
                    headers=self._headers(),
                    method=original_req.method
                )
                return self._open(new_req)

        if not isinstance(data, dict) or "success" not in data:
            detail = data.get("detail") if isinstance(data, dict) else None
            if detail is None:
                detail = data if isinstance(data, str) else f"HTTP {status}"
            elif isinstance(detail, list):
                detail = "; ".join(
                    d.get("msg", str(d)) for d in detail if isinstance(d, dict)
                ) or str(detail)
            data = {
                "success": False,
                "mensaje": detail,
                "status": status
            }

        return data