from app.models import Identity
from app.schemas import IdentityCreate
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


class IdentityController:
    @classmethod
    def get_identities(cls, db: Session) -> List[Identity]:
        return db.query(Identity).all()

    @classmethod
    def get_identity(cls, db: Session, id: UUID) -> Identity:
        return db.query(Identity).filter_by(id=id).one()

    @classmethod
    def create_identity(cls, db: Session, payload: IdentityCreate) -> Identity:
        identity = Identity()
        identity.first_name = payload.first_name
        identity.last_name = payload.last_name
        
        db.add(identity)
        db.commit()

        return identity
