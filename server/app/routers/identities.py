from app.controllers.identities import IdentityController
from app.controllers.recognition import RecognitionController
from app.database import get_session
from app.schemas import FaceEncoding, Identity, IdentityCreate, IdentityUpdate
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


router = APIRouter()


@router.get('/', response_model=List[Identity])
async def get_identities(
    db: Session = Depends(get_session)
) -> List[Identity]:
    """
    Get identities list
    """
    return IdentityController.get_identities(db)


@router.post('/', response_model=Identity)
async def create_identity(
    payload: IdentityCreate,
    db: Session = Depends(get_session)
) -> Identity:
    """
    Create identity
    """
    return IdentityController.create_identity(db, payload)


@router.get('/{identity_id}', response_model=Identity)
async def get_identity(
    identity_id: UUID,
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
    db: Session = Depends(get_session)
) -> Identity:
    """
    Update identity
    """
    return IdentityController.update_identity(db, identity_id, payload)


@router.delete('/{identity_id}')
async def delete_identity(
    identity_id: UUID,
    db: Session = Depends(get_session)
) -> Identity:
    """
    Delete identity
    """
    return IdentityController.delete_identity(db, identity_id)


@router.post('/{identity_id}/learn', response_model=FaceEncoding)
async def learn(
    identity_id: UUID,
    picture: UploadFile = File(...),
    db: Session = Depends(get_session)
) -> FaceEncoding:
    """
    Learn face on a picture
    """
    identity = IdentityController.get_identity(db, identity_id)
    image = RecognitionController.load_uploaded_file(picture)
    faces = RecognitionController.get_faces_locations(image)

    if not faces:
        raise Exception('No face found')
    elif len(faces) > 1:
        raise Exception('More than one face found')
        # todo, on retourne une erreur avec les locations trouvées

    return RecognitionController.create_face_encoding(db, identity, image, faces[0])
