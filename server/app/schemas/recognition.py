from app.schemas import Base
from app.schemas.identities import Identity
from pydantic import BaseModel


class Point(BaseModel):
    """
    A point
    """
    x: int
    y: int

    class Config:
        orm_mode = True


class Rect(BaseModel):
    """
    A rectangle identified with two opposite points
    """
    start: Point
    end: Point

    class Config:
        orm_mode = True


class FaceEncoding(Base):
    """
    A face linked to an identity
    """
    identity: Identity

    class Config:
        orm_mode = True


class Recognition(BaseModel):
    """
    Identified face
    """
    identity: Identity
    score: float
    rect: Rect

    class Config:
        orm_mode = True
