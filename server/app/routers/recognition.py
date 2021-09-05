from app.controllers.recognition import RecognitionController
from app.database import get_session
from app.schemas.recognition import Recognition
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
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

    results = []

    for face in faces:
        result = RecognitionController.identify(db, image, face)

        if result:
            results.append(result)

    # ici on enregistre la photo dans data/query/uuid
    # on propose une liste de reconnaissances pour chaque visage
    # on enregistre les résultat dans une table query

    return results
