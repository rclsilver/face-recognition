from . import create_row, load_defaults
from app.models.identities import Identity
from sqlalchemy.orm.session import Session


def insert_identity(database: Session, **kwargs):
    return create_row(database, Identity, load_defaults('identity.json'), kwargs)
