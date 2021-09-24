from typing import Generator
import pytest

from .. import database
from ..fixtures import camera
from app.cameras import VideoStream
from app.cameras.clients import SocketClient
from app.controllers.cameras import CameraController
from app.constants import RECORDS_DIR
from app.models.cameras import Camera
from app.schemas.cameras import CameraCreate, CameraUpdate, CameraRecord
from unittest.mock import Mock, patch
from uuid import UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session


def test_get_cameras_without_result(database: Session):
    result = CameraController.get_cameras(database)
    assert isinstance(result, list)
    assert len(result) == 0

def test_get_cameras(database: Session, camera: Camera):
    result = CameraController.get_cameras(database)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Camera)
    assert result[0].id == camera.id
    assert result[0].label == camera.label
    assert result[0].url == camera.url
    assert result[0].username == camera.username
    assert result[0].password == camera.password

def test_get_camera_not_found(database: Session):
    with pytest.raises(NoResultFound):
        CameraController.get_camera(database, UUID('00000000-0000-0000-0000-000000000000'))

def test_get_camera(database: Session, camera: Camera):
    result = CameraController.get_camera(database, camera.id)
    assert isinstance(result, Camera)
    assert result.id == camera.id
    assert result.label == camera.label
    assert result.url == camera.url
    assert result.username == camera.username
    assert result.password == camera.password

def test_create_camera(database: Session):
    payload = CameraCreate(label='Dummy', url='http://example.com/')
    camera = CameraController.create_camera(database, payload)
    assert isinstance(camera, Camera)
    assert camera.id is not None
    assert camera.label == payload.label
    assert camera.url == payload.url
    assert camera.username is None
    assert camera.password is None

def test_update_camera(database: Session, camera: Camera):
    payload = CameraUpdate(label='New label', url='http://new.example.com/', username='new username', password='new password')
    updated_camera = CameraController.update_camera(database, camera.id, payload)
    assert isinstance(updated_camera, Camera)
    assert updated_camera.label == payload.label
    assert updated_camera.url == payload.url
    assert updated_camera.username == payload.username
    assert updated_camera.password == payload.password

def test_delete_camera(database: Session, camera: Camera):
    CameraController.get_camera(database, camera.id)
    CameraController.delete_camera(database, camera.id)

    with pytest.raises(NoResultFound):
        CameraController.get_camera(database, camera.id)

    with pytest.raises(NoResultFound):
        CameraController.delete_camera(database, UUID('00000000-0000-0000-0000-000000000000'))

def test_get_camera_records(database: Session, camera: Camera):
    record_file = RECORDS_DIR / str(camera.id) / f'record.{VideoStream.RECORD_EXTENSION}'

    if not record_file.parent.exists():
        record_file.parent.mkdir(parents=True)

    record_file.open('w').close()

    result = CameraController.get_camera_records(database, camera.id)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CameraRecord)
    assert result[0].filename == record_file.name

def test_delete_camera_records(database: Session, camera: Camera):
    record_file = RECORDS_DIR / str(camera.id) / f'record.{VideoStream.RECORD_EXTENSION}'

    if not record_file.parent.exists():
        record_file.parent.mkdir(parents=True)

    record_file.open('w').close()

    assert record_file.exists()

    CameraController.delete_camera_records(database, camera.id)
    assert not record_file.exists()

def test_delete_camera_record(database: Session, camera: Camera):
    record_dir = RECORDS_DIR / str(camera.id)
    record_1 = record_dir / f'record-1.{VideoStream.RECORD_EXTENSION}'
    record_2 = record_dir / f'record-2.{VideoStream.RECORD_EXTENSION}'

    if not record_dir.exists():
        record_dir.mkdir(parents=True)

    record_1.open('w').close()
    record_2.open('w').close()

    assert record_1.exists()
    assert record_2.exists()

    CameraController.delete_camera_record(database, camera.id, record_1.name)

    assert not record_1.exists()
    assert record_2.exists()

def test_get_stream(database: Session, camera: Camera):
    with patch('app.cameras.clients.SocketClient.__init__', return_value=None) as mock:
        stream = CameraController.get_stream(database, camera.id)
        assert isinstance(stream, SocketClient)
        mock.assert_called_with(camera)

def test_live():
    def next_value(self):
        if self._i < 2:
            self._i += 1
            return f'dummy jpeg {self._i}'.encode('utf-8')
        raise GeneratorExit()

    client = Mock()
    client._i = 0
    client.__next__ = next_value
    client.__iter__ = lambda self: self
    result = CameraController.live(client)
    assert isinstance(result, Generator)
    result = list(result)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == b'--frame\r\nContent-Type: image/jpeg\r\n\r\ndummy jpeg 1\r\n\r\n'
    assert result[1] == b'--frame\r\nContent-Type: image/jpeg\r\n\r\ndummy jpeg 2\r\n\r\n'
    client.close.assert_called_once()
