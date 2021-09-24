from . import create_row, load_defaults
from app.models.identities import Identity
from app.models.recognition import FaceEncoding, Query, Suggestion
from sqlalchemy.orm.session import Session
from typing import Optional


def insert_face_encoding(database: Session, identity: Identity, **kwargs):
    return create_row(database, FaceEncoding, load_defaults('face_encoding.json', identity_id=identity.id), kwargs)

def insert_query(database: Session, **kwargs):
    return create_row(database, Query, load_defaults('query.json'), kwargs)

def insert_suggestion(database: Session, query: Query, identity: Optional[Identity] = None, **kwargs):
    return create_row(database, Suggestion, load_defaults('suggestion.json', query_id=query.id, identity_id=identity.id if identity else None), kwargs)
