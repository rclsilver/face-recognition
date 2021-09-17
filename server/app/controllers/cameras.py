import logging

from app.cameras import VideoStream
from app.cameras.clients import SocketClient
from app.constants import RECORDS_DIR
from app.models.cameras import Camera
from app.schemas.cameras import CameraCreate, CameraRecord, CameraUpdate
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


logger = logging.getLogger(__name__)


class CameraController:
    @classmethod
    def get_cameras(cls, db: Session) -> List[Camera]:
        return db.query(Camera).order_by(Camera.label.asc()).all()

    @classmethod
    def get_camera(cls, db: Session, id: UUID) -> Camera:
        return db.query(Camera).filter_by(id=id).one()

    @classmethod
    def get_camera_records(cls, db: Session, id: UUID) -> List[CameraRecord]:
        camera = cls.get_camera(db, id)
        camera_dir = RECORDS_DIR / str(camera.id)
        records = []

        if camera_dir.exists():
            for record_file in camera_dir.glob(f'*.{VideoStream.RECORD_EXTENSION}'):
                stat = record_file.stat()
                record = {
                    'filename': record_file.name,
                    'created_at': str(datetime.fromtimestamp(stat.st_ctime)),
                    'updated_at': str(datetime.fromtimestamp(stat.st_mtime)),
                    'timestamp': stat.st_ctime,
                }
                records.append(record)

        return list(
            CameraRecord(**{
                'filename': record['filename'],
                'created_at': record['created_at'],
                'updated_at': record['updated_at'],
            }) for record in sorted(records, reverse=True, key=lambda record: record['timestamp'])
        )

    @classmethod
    def delete_camera_records(cls, db: Session, camera_id: UUID) -> None:
        camera = cls.get_camera(db, camera_id)
        camera_dir = RECORDS_DIR / str(camera.id)

        if camera_dir.exists():
            for record_file in camera_dir.glob(f'*.{VideoStream.RECORD_EXTENSION}'):
                record_file.unlink()

    @classmethod
    def delete_camera_record(cls, db: Session, camera_id: UUID, record_name: str) -> None:
        camera = cls.get_camera(db, camera_id)
        camera_dir = RECORDS_DIR / str(camera.id)
        record_file = camera_dir / record_name
        
        if record_file.exists():
            record_file.unlink()

    @classmethod
    def create_camera(cls, db: Session, payload: CameraCreate) -> Camera:
        camera = Camera()
        camera.label = payload.label
        camera.url = payload.url
        camera.username = payload.username
        camera.password = payload.password
        
        db.add(camera)
        db.commit()

        return camera

    @classmethod
    def update_camera(cls, db: Session, id: UUID, payload: CameraUpdate) -> Camera:
        camera = cls.get_camera(db, id)
        camera.label = payload.label
        camera.url = payload.url
        camera.username = payload.username
        camera.password = payload.password

        db.commit()

        return camera

    @classmethod
    def delete_camera(cls, db: Session, id: UUID) -> None:
        camera = cls.get_camera(db, id)

        db.delete(camera)
        db.commit()

    @classmethod
    def get_stream(cls, db: Session, id: UUID) -> SocketClient:
        camera = cls.get_camera(db, id)
        client = SocketClient(camera)

        return client

    @classmethod
    def live(cls, client: SocketClient):
        logger.debug('Starting streaming of camera %s', client.camera.id)

        try:
            for frame in client:
                yield (
                    b'--frame\r\n' +
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    frame +
                    b'\r\n\r\n'
                )
        except GeneratorExit:
            pass

        client.close()

        logger.debug('Stop streaming of camera %s', client.camera.id)
