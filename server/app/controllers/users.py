import logging

from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


logger = logging.getLogger(__name__)


class UserController:
    @classmethod
    def get_users(cls, db: Session) -> List[User]:
        return db.query(User).order_by(User.username.asc()).all()

    @classmethod
    def get_user(cls, db: Session, id: UUID) -> User:
        return db.query(User).filter_by(id=id).one()

    @classmethod
    def create_user(cls, db: Session, payload: UserCreate) -> User:
        user = User()
        user.username = payload.username
        user.is_admin = payload.is_admin
        
        db.add(user)
        db.commit()

        return user

    @classmethod
    def update_user(cls, db: Session, id: UUID, payload: UserUpdate) -> User:
        user = cls.get_user(db, id)
        user.is_admin = payload.is_admin

        db.commit()

        return user

    @classmethod
    def delete_user(cls, db: Session, id: UUID) -> None:
        user = cls.get_user(db, id)

        db.delete(user)
        db.commit()

    @classmethod
    def get_or_create_user(cls, db: Session, username: str, is_admin: bool) -> User:
        user = db.query(User).filter_by(username=username).first()

        if not user:
            user = cls.create_user(db, UserCreate(username=username, is_admin=is_admin))
        else:
            if user.is_admin != is_admin:
                user = cls.update_user(db, user.id, UserUpdate(is_admin=is_admin))

        return user
