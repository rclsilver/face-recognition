from app.models import Base
from sqlalchemy import Column, String


class Identity(Base):
    """
    Known identity
    """
    __tablename__ = 'identity'

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    avatar = Column(String, nullable=True)
