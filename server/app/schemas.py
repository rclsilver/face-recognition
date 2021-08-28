import datetime

from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Tuple


class Base(BaseModel):
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime


class IdentityCreate(BaseModel):
    """
    Identity creation payload
    """
    first_name: str
    last_name: str


class Identity(Base):
    """
    Identity row
    """
    first_name: str
    last_name: str
    avatar: Optional[str] = None

    class Config:
        orm_mode = True


class Point(BaseModel):
    """
    A point
    """
    x: int
    y: int


class Rect(BaseModel):
    """
    A rectangle identified with two opposite points
    """
    start: Point
    end: Point


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
