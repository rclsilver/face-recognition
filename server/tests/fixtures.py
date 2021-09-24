from .test_data.cameras import insert_camera
from .test_data.identities import insert_identity
from .test_data.users import insert_user
from .test_data.recognition import insert_query
from pytest import fixture
from sqlalchemy.orm.session import Session


@fixture
def identity(database: Session):
    yield insert_identity(database)


@fixture
def camera(database: Session):
    yield insert_camera(database)


@fixture
def user(database: Session):
    yield insert_user(database)


@fixture
def query(database: Session):
    yield insert_query(database)
