from app.schemas import Base
from pydantic import BaseModel


class UserCreate(BaseModel):
    """
    User creation payload
    """
    username: str
    is_admin: bool


class UserUpdate(BaseModel):
    """
    User update payload
    """
    is_admin: bool


class User(Base):
    """
    User row
    """
    username: str
    is_admin: bool

    class Config:
        orm_mode = True
