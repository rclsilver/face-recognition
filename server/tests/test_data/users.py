from . import create_row, load_defaults
from app.models.users import User
from sqlalchemy.orm.session import Session


def insert_user(database: Session, **kwargs):
    return create_row(database, User, load_defaults('user.json'), kwargs)
