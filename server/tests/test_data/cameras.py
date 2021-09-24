from . import create_row, load_defaults
from app.models.cameras import Camera
from sqlalchemy.orm.session import Session


def insert_camera(database: Session, **kwargs):
    return create_row(database, Camera, load_defaults('camera.json'), kwargs)
