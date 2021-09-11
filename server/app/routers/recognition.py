from app.auth import check_is_admin, get_user
from app.controllers.recognition import RecognitionController
from app.database import get_session
from app.models.users import User
from app.schemas.recognition import FaceEncoding, Query, QueryConfirm, QuerySuggestion, Recognition
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List


router = APIRouter()


@router.post('/query', response_model=List[Recognition])
async def query(
    picture: UploadFile = File(...),
    db: Session = Depends(get_session)
) -> List[Recognition]:
    """
    Ask to recognize faces on a picture
    """
    image = RecognitionController.load_uploaded_file(picture)
    faces = RecognitionController.get_faces_locations(image)

    if not faces:
        return None

    return RecognitionController.query(db, image, faces)


@router.get('/queries', response_model=List[Query])
async def get_queries(
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> List[Query]:
    """
    List recorded queries
    """
    check_is_admin(user)

    return list(
        Query(**{
            'id': query.id,
            'created_at': query.created_at,
            'updated_at': query.updated_at,
            'suggestions': [
                QuerySuggestion(**{
                    'id': suggestion.id,
                    'created_at': suggestion.created_at,
                    'updated_at': suggestion.updated_at,
                    'rect': {
                        'start': {
                            'x': suggestion.rect[3],
                            'y': suggestion.rect[0],
                        },
                        'end': {
                            'x': suggestion.rect[1],
                            'y': suggestion.rect[2],
                        },
                    },
                    'score': suggestion.score,
                    'identity': suggestion.identity,
                }) for suggestion in query.suggestions
            ],
        }) for query in RecognitionController.get_queries(db)
    )


@router.post('/queries/{query_id}/{suggestion_id}', response_model=FaceEncoding)
async def confirm_suggestion(
    query_id: UUID,
    suggestion_id: UUID,
    payload: QueryConfirm,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> FaceEncoding:
    """
    Confirm a query suggestion
    """
    check_is_admin(user)

    encoding = RecognitionController.confirm_suggestion(db, query_id, suggestion_id, payload.identity)
    background_tasks.add_task(RecognitionController.compute_suggestions, db)
    return encoding


@router.delete('/queries/{query_id}/{suggestion_id}')
async def delete_suggestion(
    query_id: UUID,
    suggestion_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> None:
    """
    Delete a query suggestion
    """
    check_is_admin(user)

    return RecognitionController.delete_suggestion(db, query_id, suggestion_id)
