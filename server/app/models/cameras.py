from app.models import Base
from sqlalchemy import Column, String


class Camera(Base):
    """
    Network camera
    """
    __tablename__ = 'camera'

    label = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
