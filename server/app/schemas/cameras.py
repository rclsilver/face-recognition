from app.schemas import Base
from pydantic import BaseModel
from typing import Optional


class CameraCreate(BaseModel):
    """
    Camera creation payload
    """
    label: str
    url: str
    username: str
    password: str


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
    username: Optional[str]
    password: Optional[str]

    class Config:
        orm_mode = True


class CameraRecord(BaseModel):
    """
    Camera record
    """
    created_at: str
    updated_at: str
    filename: str
