from app.schemas import Base
from pydantic import BaseModel
from typing import Optional


class IdentityCreate(BaseModel):
    """
    Identity creation payload
    """
    first_name: str
    last_name: str


class IdentityUpdate(IdentityCreate):
    """
    Identity update payload
    """
    pass


class Identity(Base):
    """
    Identity row
    """
    first_name: str
    last_name: str
    avatar: Optional[str] = None

    class Config:
        orm_mode = True
