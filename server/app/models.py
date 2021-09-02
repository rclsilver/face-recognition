import uuid

from sqlalchemy import Column, DateTime, func, String, cast, literal, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import UserDefinedType

from typing import List


class Base:
    """
    Base class for a model in database
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)


Base = declarative_base(cls=Base)


class BOX(UserDefinedType):
    def get_col_spec(self, **kw):
        return 'BOX'


class CUBE(UserDefinedType):
    def get_col_spec(self):
        return 'CUBE'

    def bind_processor(self, dialect):
        def process(value):
            return func.cube(value)
        return process

    def result_processor(self, dialect, coltype):
        print(f'result_processor({dialect}, {coltype})')
        def process(value):
            print(f'result_processor::process({value})')
            return value
        return process


class Identity(Base):
    __tablename__ = 'identity'

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    avatar = Column(String, nullable=True)


class FaceEncoding(Base):
    __tablename__ = 'face_encoding'

    identity_id = Column(UUID(as_uuid=True), ForeignKey('identity.id'), nullable=False)
    identity = relationship(Identity, backref=backref('face_encodings', uselist=True, cascade='all, delete-orphan'))

    vec_low = Column(ARRAY(Float), nullable=False)
    vec_high = Column(ARRAY(Float), nullable=False)


class Camera(Base):
    __tablename__ = 'camera'

    label = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
