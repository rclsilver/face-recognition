from app.models import Base
from app.models.identities import Identity
from sqlalchemy import Column, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.schema import ForeignKey


class FaceEncoding(Base):
    """
    Known face encoding
    """
    __tablename__ = 'face_encoding'

    identity_id = Column(UUID(as_uuid=True), ForeignKey('identity.id'), nullable=False)
    identity = relationship(Identity, backref=backref('face_encodings', uselist=True, cascade='all, delete-orphan'))

    vec_low = Column(ARRAY(Float), nullable=False)
    vec_high = Column(ARRAY(Float), nullable=False)
