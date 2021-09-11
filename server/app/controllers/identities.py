import shutil

from app.constants import FACES_DIR
from app.models.identities import Identity
from app.models.recognition import FaceEncoding
from app.schemas.identities import IdentityCreate, IdentityUpdate
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


class IdentityController:
    @classmethod
    def get_identities(cls, db: Session) -> List[Identity]:
        return db.query(Identity).order_by(
            Identity.last_name.asc(),
            Identity.first_name.asc()
        ).all()

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

    @classmethod
    def update_identity(cls, db: Session, id: UUID, payload: IdentityUpdate) -> Identity:
        identity = cls.get_identity(db, id)
        identity.first_name = payload.first_name
        identity.last_name = payload.last_name

        db.commit()

        return identity

    @classmethod
    def delete_identity(cls, db: Session, id: UUID) -> None:
        identity = cls.get_identity(db, id)
        identity_dir = FACES_DIR / str(identity.id)

        db.query(FaceEncoding).filter_by(identity=identity).delete()
        db.delete(identity)

        if identity_dir.exists():
            shutil.rmtree(identity_dir)

        db.commit()

    @classmethod
    def clear_identity(cls, db: Session, id: UUID) -> None:
        identity = cls.get_identity(db, id)
        identity_dir = FACES_DIR / str(identity.id)

        db.query(FaceEncoding).filter_by(identity=identity).delete()

        if identity_dir.exists():
            shutil.rmtree(identity_dir)

        db.commit()
