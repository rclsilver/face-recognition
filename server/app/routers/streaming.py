from app.controllers.streaming import StreamingController
from app.database import get_session
from app.schemas import Camera, CameraCreate, CameraUpdate
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


router = APIRouter()


@router.get('/cameras/', response_model=List[Camera])
async def get_cameras(
    db: Session = Depends(get_session)
) -> List[Camera]:
    """
    Get cameras list
    """
    return StreamingController.get_cameras(db)


@router.post('/cameras/', response_model=Camera)
async def create_camera(
    payload: CameraCreate,
    db: Session = Depends(get_session)
) -> Camera:
    """
    Create camera
    """
    return StreamingController.create_camera(db, payload)


@router.get('/cameras/{camera_id}', response_model=Camera)
async def get_camera(
    camera_id: UUID,
    db: Session = Depends(get_session)
) -> Camera:
    """
    Get camera
    """
    return StreamingController.get_camera(db, camera_id)


@router.put('/cameras/{camera_id}', response_model=Camera)
async def update_camera(
    camera_id: UUID,
    payload: CameraUpdate,
    db: Session = Depends(get_session)
) -> Camera:
    """
    Update camera
    """
    return StreamingController.update_camera(db, camera_id, payload)


@router.delete('/cameras/{camera_id}')
async def delete_camera(
    camera_id: UUID,
    db: Session = Depends(get_session)
) -> None:
    """
    Delete camera
    """
    return StreamingController.delete_camera(db, camera_id)


@router.get('/cameras/{camera_id}/live')
async def stream_camera(
    camera_id: UUID,
    db: Session = Depends(get_session)
):
    """
    Get camera stream
    """
    stream = StreamingController.get_stream(db, camera_id)

    return StreamingResponse(
        StreamingController.live(stream),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )
