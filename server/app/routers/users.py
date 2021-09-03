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
    db: Session = Depends(get_session)
) -> List[User]:
    """
    Get users list
    """
    return UserController.get_users(db)


@router.post('/', response_model=User)
async def create_user(
    payload: UserCreate,
    db: Session = Depends(get_session)
) -> User:
    """
    Create user
    """
    return UserController.create_user(db, payload)


@router.get('/{user_id}', response_model=User)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_session)
) -> User:
    """
    Get user
    """
    return UserController.get_user(db, user_id)


@router.put('/{user_id}', response_model=User)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_session)
) -> User:
    """
    Update user
    """
    return UserController.update_user(db, user_id, payload)


@router.delete('/{user_id}')
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_session)
) -> None:
    """
    Delete user
    """
    return UserController.delete_user(db, user_id)
