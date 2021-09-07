from app.schemas import Base
from app.schemas.identities import Identity
from pydantic import BaseModel
from typing import List, Optional


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


class QuerySuggestion(Base):
    """
    Recognition query suggestion
    """
    identity: Optional[Identity]
    rect: Rect
    score: Optional[float]

    class Config:
        orm_mode = True


class Query(Base):
    """
    Recognition query
    """
    suggestions: List[QuerySuggestion]

    class Config:
        orm_mode = True


class QueryConfirm(BaseModel):
    identity: Optional[Identity]

    class Config:
        orm_mode = True
