import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from platformcore.database import Base
from platformcore.models.identity import PlatformUser
from platformcore.models.security import PlatformRole, PlatformPermission
from platformcore.security import hash_password


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_user(db_session):
    user = PlatformUser(
        username="testuser",
        full_name="Test User",
        email="test@example.com",
        password_hash=hash_password("test1234"),
        role="admin",
        nivel_seguridad=3,
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_superuser(db_session):
    user = PlatformUser(
        username="super",
        full_name="Super User",
        email="super@example.com",
        password_hash=hash_password("super1234"),
        role="admin",
        nivel_seguridad=5,
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
