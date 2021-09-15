from app.models import Base
from app.models.identities import Identity
from sqlalchemy import ARRAY, Column, Float, Integer
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


class Query(Base):
    """
    Query
    """
    __tablename__ = 'query'


class Suggestion(Base):
    """
    Query suggestion
    """
    __tablename__ = 'suggestion'

    query_id = Column(UUID(as_uuid=True), ForeignKey('query.id'), nullable=False)
    query = relationship(Query, backref=backref('suggestions', uselist=True))

    identity_id = Column(UUID(as_uuid=True), ForeignKey('identity.id'), nullable=True)
    identity = relationship(Identity, backref=backref('suggestions', uselist=True))

    vec_low = Column(ARRAY(Float), nullable=False)
    vec_high = Column(ARRAY(Float), nullable=False)

    rect = Column(ARRAY(Integer), nullable=False)
    score = Column(Float, nullable=True)
