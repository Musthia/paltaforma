import pytest
from platformcore.services.identity import IdentityService
from platformcore.services.security import UserService, RoleService
from platformcore.services.audit import AuditService
from platformcore.models.identity import PlatformUser
from platformcore.exceptions import NotFoundError, ConflictError


class TestIdentityService:

    def test_login_success(self, db_session, test_user):
        result = IdentityService.login(db_session, "testuser", "test1234")
        assert result["success"] is True
        assert "access_token" in result
        assert "refresh_token" in result

    def test_login_wrong_password(self, db_session, test_user):
        result = IdentityService.login(db_session, "testuser", "wrong")
        assert result["success"] is False

    def test_login_inactive_user(self, db_session, test_user):
        test_user.is_active = False
        db_session.commit()
        result = IdentityService.login(db_session, "testuser", "test1234")
        assert result["success"] is False
        assert "inactivo" in result["mensaje"].lower()

    def test_refresh_token(self, db_session, test_user):
        login_result = IdentityService.login(db_session, "testuser", "test1234")
        refresh_result = IdentityService.refresh(db_session, login_result["refresh_token"])
        assert refresh_result["success"] is True
        assert "access_token" in refresh_result

    def test_logout(self, db_session, test_user):
        login_result = IdentityService.login(db_session, "testuser", "test1234")
        result = IdentityService.logout(db_session, login_result["refresh_token"])
        assert result["success"] is True


class TestUserService:

    def test_create_user(self, db_session):
        class FakeData:
            username = "newuser"
            password = "pass1234"
            full_name = "New User"
            email = "new@example.com"
            role = "consulta"
            nivel_seguridad = 1
            is_active = True
            is_superuser = False

        user = UserService.create_user(db_session, FakeData())
        assert user.username == "newuser"
        assert user.email == "new@example.com"

    def test_create_duplicate_username(self, db_session, test_user):
        class FakeData:
            username = "testuser"
            password = "pass1234"
            full_name = "Dup"
            email = "dup@example.com"
            role = "consulta"
            nivel_seguridad = 1
            is_active = True

        with pytest.raises(ConflictError):
            UserService.create_user(db_session, FakeData())

    def test_get_user_not_found(self, db_session):
        with pytest.raises(NotFoundError):
            UserService.get_user(db_session, 9999)

    def test_list_users(self, db_session, test_user):
        result = UserService.list_users(db_session)
        assert result["total"] >= 1
        assert len(result["users"]) >= 1


class TestAuditService:

    def test_record_and_list(self, db_session):
        AuditService.record(
            db_session,
            username="testuser",
            action="LOGIN_SUCCESS",
            entity="auth",
            detail="Login exitoso",
        )
        result = AuditService.list_logs(db_session)
        assert result["total"] == 1
        assert result["logs"][0].action == "LOGIN_SUCCESS"
