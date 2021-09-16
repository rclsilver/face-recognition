from app.auth import check_is_admin, get_user
from app.controllers.identities import IdentityController
from app.database import get_session
from app.schemas.identities import Identity, IdentityCreate, IdentityUpdate
from app.schemas.recognition import FaceEncoding
from app.schemas.users import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


router = APIRouter()


@router.get('/', response_model=List[Identity])
async def get_identities(
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> List[Identity]:
    """
    Get identities list
    """
    return IdentityController.get_identities(db)


@router.post('/', response_model=Identity)
async def create_identity(
    payload: IdentityCreate,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> Identity:
    """
    Create identity
    """
    check_is_admin(user)
    return IdentityController.create_identity(db, payload)


@router.get('/{identity_id}', response_model=Identity)
async def get_identity(
    identity_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> Identity:
    """
    Get identity
    """
    return IdentityController.get_identity(db, identity_id)


@router.put('/{identity_id}', response_model=Identity)
async def update_identity(
    identity_id: UUID,
    payload: IdentityUpdate,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> Identity:
    """
    Update identity
    """
    check_is_admin(user)
    return IdentityController.update_identity(db, identity_id, payload)


@router.delete('/{identity_id}')
async def delete_identity(
    identity_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
):
    """
    Delete identity
    """
    check_is_admin(user)
    return IdentityController.delete_identity(db, identity_id)


@router.get('/{identity_id}/faces')
async def get_identity_faces(
    identity_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> List[FaceEncoding]:
    """
    Get identity faces
    """
    check_is_admin(user)
    return IdentityController.get_identity_faces(db, identity_id)


@router.delete('/{identity_id}/faces/{face_id}')
async def get_identity_faces(
    identity_id: UUID,
    face_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> List[FaceEncoding]:
    """
    Delete identity face
    """
    check_is_admin(user)
    return IdentityController.delete_identity_face(db, identity_id, face_id)


@router.post('/{identity_id}/clear')
async def clear_identity(
    identity_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
):
    """
    Clear identity encodings
    """
    check_is_admin(user)
    return IdentityController.clear_identity(db, identity_id)
