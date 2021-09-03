from app.controllers.cameras import CameraController
from app.database import get_session
from app.schemas.cameras import Camera, CameraCreate, CameraUpdate
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


router = APIRouter()


@router.get('/', response_model=List[Camera])
async def get_cameras(
    db: Session = Depends(get_session)
) -> List[Camera]:
    """
    Get cameras list
    """
    return CameraController.get_cameras(db)


@router.post('/', response_model=Camera)
async def create_camera(
    payload: CameraCreate,
    db: Session = Depends(get_session)
) -> Camera:
    """
    Create camera
    """
    return CameraController.create_camera(db, payload)


@router.get('/{camera_id}', response_model=Camera)
async def get_camera(
    camera_id: UUID,
    db: Session = Depends(get_session)
) -> Camera:
    """
    Get camera
    """
    return CameraController.get_camera(db, camera_id)


@router.put('/{camera_id}', response_model=Camera)
async def update_camera(
    camera_id: UUID,
    payload: CameraUpdate,
    db: Session = Depends(get_session)
) -> Camera:
    """
    Update camera
    """
    return CameraController.update_camera(db, camera_id, payload)


@router.delete('/{camera_id}')
async def delete_camera(
    camera_id: UUID,
    db: Session = Depends(get_session)
) -> None:
    """
    Delete camera
    """
    return CameraController.delete_camera(db, camera_id)


@router.get('/{camera_id}/live')
async def stream_camera(
    camera_id: UUID,
    db: Session = Depends(get_session)
):
    """
    Get camera stream
    """
    try:
        stream = CameraController.get_stream(db, camera_id)

        return StreamingResponse(
            CameraController.live(stream),
            media_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
