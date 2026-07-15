from platformcore.jwt import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)


class TestJWT:

    def test_create_and_verify_access_token(self):
        data = {"sub": "testuser", "role": "admin"}
        result = create_access_token(data)
        assert "access_token" in result
        assert "jti" in result
        assert "expires_at" in result

        payload = verify_access_token(result["access_token"])
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"

    def test_create_and_verify_refresh_token(self):
        data = {"sub": "testuser"}
        result = create_refresh_token(data)
        assert "refresh_token" in result
        assert "jti" in result

        payload = verify_refresh_token(result["refresh_token"])
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"

    def test_access_token_rejected_as_refresh(self):
        data = {"sub": "testuser"}
        result = create_access_token(data)
        payload = verify_refresh_token(result["access_token"])
        assert payload is None

    def test_invalid_token(self):
        assert verify_access_token("invalid.token.here") is None
        assert verify_refresh_token("invalid.token.here") is None
