import logging

from app.cameras.clients import SocketClient
from app.models.cameras import Camera
from app.schemas.cameras import CameraCreate, CameraUpdate
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
    def create_camera(cls, db: Session, payload: CameraCreate) -> Camera:
        camera = Camera()
        camera.label = payload.label
        camera.url = payload.url
        
        db.add(camera)
        db.commit()

        return camera

    @classmethod
    def update_camera(cls, db: Session, id: UUID, payload: CameraUpdate) -> Camera:
        camera = cls.get_camera(db, id)
        camera.label = payload.label
        camera.url = payload.url

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
