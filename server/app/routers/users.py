from app.auth import check_is_admin, get_user
from app.controllers.users import UserController
from app.database import get_session
from app.schemas.users import User, UserCreate, UserUpdate
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


router = APIRouter()


@router.get('/', response_model=List[User])
async def get_users(
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> List[User]:
    """
    Get users list
    """
    return UserController.get_users(db)


@router.get('/{user_id}', response_model=User)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_session)
) -> User:
    """
    Get user
    """
    return UserController.get_user(db, user_id)


@router.delete('/{user_id}')
async def delete_user(
    user_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> None:
    """
    Delete user
    """
    check_is_admin(user)
    return UserController.delete_user(db, user_id)
