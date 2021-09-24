import pytest

from .. import database
from ..fixtures import user
from app.controllers.users import UserController
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate
from uuid import UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session


def test_get_users_without_result(database: Session):
    result = UserController.get_users(database)
    assert isinstance(result, list)
    assert len(result) == 0

def test_get_users(database: Session, user: User):
    result = UserController.get_users(database)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], User)
    assert result[0].id == user.id
    assert result[0].username == user.username
    assert result[0].is_admin == user.is_admin

def test_get_user_not_found(database):
    with pytest.raises(NoResultFound):
        UserController.get_user(database, UUID('00000000-0000-0000-0000-000000000000'))

def test_get_user(database: Session, user: User):
    result = UserController.get_user(database, user.id)
    assert isinstance(result, User)
    assert result.id == user.id
    assert result.username == user.username
    assert result.is_admin == user.is_admin

def test_create_user(database: Session):
    payload = UserCreate(username='dummy.user', is_admin=True)
    result = UserController.create_user(database, payload)
    assert isinstance(result, User)
    assert result.id is not None
    assert result.username == payload.username
    assert result.is_admin == payload.is_admin

def test_update_user(database: Session, user: User):
    payload = UserUpdate(is_admin=True)
    result = UserController.update_user(database, user.id, payload)
    assert isinstance(result, User)
    assert result.id == user.id
    assert result.username == user.username
    assert result.is_admin == payload.is_admin

def test_delete_user(database: Session, user: User):
    UserController.get_user(database, user.id)
    UserController.delete_user(database, user.id)

    with pytest.raises(NoResultFound):
        UserController.get_user(database, user.id)

    with pytest.raises(NoResultFound):
        UserController.delete_user(database, UUID('00000000-0000-0000-0000-000000000000'))

def test_get_or_create_user(database: Session, user: User):
    # Retrieve existing user
    result = UserController.get_or_create_user(database, user.username, user.is_admin)
    assert result.id == user.id
    assert result.username == user.username
    assert not result.is_admin

    # Retrieve existing user and modify it
    result = UserController.get_or_create_user(database, user.username, True)
    assert result.id == user.id
    assert result.username == user.username
    assert result.is_admin

    # Retrieve new user
    result = UserController.get_or_create_user(database, 'admin', True)
    assert result.id is not None
    assert result.username == 'admin'
    assert result.is_admin
