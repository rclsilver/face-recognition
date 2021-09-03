import logging

from app.models.cameras import Camera
from app.schemas.cameras import CameraCreate, CameraUpdate
from app.streaming import VideoStream, NetworkStream
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
    def get_stream(cls, db: Session, id: UUID) -> VideoStream:
        camera = cls.get_camera(db, id)

        return NetworkStream(
            camera.url,
            db,
            label=camera.label,
            force_width=800
        )

    @classmethod
    def live(cls, stream: VideoStream):
        try:
            logger.debug('Starting streaming with %s', stream)

            while True:
                ret, frame = stream.get_frame()

                if not ret:
                    continue

                yield (
                    b'--frame\r\n' +
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    frame +
                    b'\r\n\r\n'
                )
        except GeneratorExit:
            logger.debug('Stop streaming of %s', stream)
