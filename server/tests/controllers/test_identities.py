import pytest

from .. import database
from ..fixtures import identity
from ..test_data.recognition import insert_face_encoding
from app.constants import FACES_DIR
from app.controllers.identities import IdentityController
from app.models.identities import Identity
from app.models.recognition import FaceEncoding
from app.schemas.identities import IdentityCreate, IdentityUpdate
from uuid import UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session


def test_get_identities_without_result(database: Session):
    identities = IdentityController.get_identities(database)
    assert isinstance(identities, list)
    assert len(identities) == 0

def test_get_identities(database: Session, identity: Identity):
    identities = IdentityController.get_identities(database)
    assert isinstance(identities, list)
    assert len(identities) == 1
    assert isinstance(identities[0], Identity)
    assert identities[0].id == identity.id
    assert identities[0].first_name == identity.first_name
    assert identities[0].last_name == identity.last_name

def test_get_identity_not_found(database):
    with pytest.raises(NoResultFound):
        IdentityController.get_identity(database, UUID('00000000-0000-0000-0000-000000000000'))

def test_get_identity(database: Session, identity: Identity):
    result = IdentityController.get_identity(database, identity.id)
    assert isinstance(result, Identity)
    assert result.id == identity.id
    assert result.first_name == identity.first_name
    assert result.last_name == identity.last_name

def test_get_identity_faces_without_faces(database: Session, identity: Identity):
    result = IdentityController.get_identity_faces(database, identity.id)
    assert isinstance(result, list)
    assert len(result) == 0

def test_get_identity_faces(database: Session, identity: Identity):
    face = insert_face_encoding(database, identity, vec_low=[1.0], vec_high=[2.0])
    result = IdentityController.get_identity_faces(database, identity.id)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FaceEncoding)
    assert result[0].id == face.id
    assert result[0].identity.id == identity.id
    assert result[0].identity_id == identity.id
    assert result[0].vec_low == face.vec_low
    assert result[0].vec_high == face.vec_high

def test_create_identity(database: Session):
    payload = IdentityCreate(first_name='Creation', last_name='Test')
    identity = IdentityController.create_identity(database, payload)
    assert isinstance(identity, Identity)
    assert identity.id is not None
    assert identity.first_name == payload.first_name
    assert identity.last_name == payload.last_name
    assert identity.avatar is None

def test_update_identity(database: Session, identity: Identity):
    payload = IdentityUpdate(first_name='New firstname', last_name='New lastname')
    updated_identity = IdentityController.update_identity(database, identity.id, payload)
    assert isinstance(updated_identity, Identity)
    assert updated_identity.first_name == payload.first_name
    assert updated_identity.last_name == payload.last_name
    assert updated_identity.avatar is None

def test_delete_identity(database: Session, identity: Identity):
    IdentityController.get_identity(database, identity.id)
    IdentityController.delete_identity(database, identity.id)

    with pytest.raises(NoResultFound):
        IdentityController.get_identity(database, identity.id)

    with pytest.raises(NoResultFound):
        IdentityController.delete_identity(database, UUID('00000000-0000-0000-0000-000000000000'))

def test_delete_identity_with_data_directory(database: Session, identity: Identity):
    identity_directory = FACES_DIR / str(identity.id)

    if not identity_directory.exists():
        identity_directory.mkdir(parents=True)

    IdentityController.get_identity(database, identity.id)
    IdentityController.delete_identity(database, identity.id)

    assert not identity_directory.exists()

def test_delete_identity_face(database: Session, identity: Identity):
    face = insert_face_encoding(database, identity)
    result = IdentityController.get_identity_faces(database, identity.id)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FaceEncoding)
    assert result[0].id == face.id
    assert result[0].identity.id == identity.id
    assert result[0].identity_id == identity.id
    assert result[0].vec_low == face.vec_low
    assert result[0].vec_high == face.vec_high

    IdentityController.delete_identity_face(database, identity.id, face.id)
    result = IdentityController.get_identity_faces(database, identity.id)
    assert isinstance(result, list)
    assert len(result) == 0

def test_delete_identity_face_with_existing_file(database: Session, identity: Identity):
    face = insert_face_encoding(database, identity)

    # Create empty face file
    face_file = FACES_DIR / str(identity.id) / f'{face.id}.png'
    face_file.parent.mkdir(parents=True)
    face_file.open('w').close()
    assert face_file.exists()

    result = IdentityController.get_identity_faces(database, identity.id)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FaceEncoding)
    assert result[0].id == face.id
    assert result[0].identity.id == identity.id
    assert result[0].identity_id == identity.id
    assert result[0].vec_low == face.vec_low
    assert result[0].vec_high == face.vec_high

    IdentityController.delete_identity_face(database, identity.id, face.id)
    result = IdentityController.get_identity_faces(database, identity.id)
    assert isinstance(result, list)
    assert len(result) == 0

    assert not face_file.exists()

def test_clear_identity(database: Session, identity: Identity):
    insert_face_encoding(database, identity)
    insert_face_encoding(database, identity)
    result = IdentityController.get_identity_faces(database, identity.id)
    assert isinstance(result, list)
    assert len(result) == 2

    IdentityController.clear_identity(database, identity.id)
    result = IdentityController.get_identity_faces(database, identity.id)
    assert isinstance(result, list)
    assert len(result) == 0

def test_clear_identity_with_existing_directory(database: Session, identity: Identity):
    identity_dir = FACES_DIR / str(identity.id)
    identity_dir.mkdir(parents=True)

    insert_face_encoding(database, identity)
    insert_face_encoding(database, identity)
    result = IdentityController.get_identity_faces(database, identity.id)
    assert isinstance(result, list)
    assert len(result) == 2

    IdentityController.clear_identity(database, identity.id)
    result = IdentityController.get_identity_faces(database, identity.id)
    assert isinstance(result, list)
    assert len(result) == 0
    assert not identity_dir.exists()
