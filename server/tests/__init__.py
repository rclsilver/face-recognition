from app import get_app
from app.database import SessionLocal
from fastapi.testclient import TestClient
from pytest import fixture
from unittest.mock import MagicMock, patch


@fixture
def client():
    # Patching OidcAuth class
    OidcAuthMock = MagicMock()

    # Creating the application
    with patch('app.auth.oidc.OidcAuth', OidcAuthMock):
        app = get_app(
            'http://sso.example.com',
            '/tests',
            production=False,
            debug=True,
            source_whitelist=[]
        )

    # Return the client
    yield TestClient(app)


@fixture
def database():
    try:
        db = SessionLocal()
        yield db
    finally:
        # Clear data
        for table_name in ['user', 'identity', 'face_encoding', 'camera', 'query', 'suggestion']:
            db.execute(f'TRUNCATE TABLE "{table_name}" CASCADE;')
        db.commit()

        # Close the connection
        db.close()
