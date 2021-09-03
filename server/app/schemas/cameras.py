from app.schemas import Base
from pydantic import BaseModel


class CameraCreate(BaseModel):
    """
    Camera creation payload
    """
    label: str
    url: str


class CameraUpdate(CameraCreate):
    """
    Camera update payload
    """
    pass


class Camera(Base):
    """
    Camera row
    """
    label: str
    url: str

    class Config:
        orm_mode = True
