from app.auth import BaseAuth, check_is_admin, get_auth, get_user
from app.controllers.cameras import CameraController
from app.database import get_session
from app.schemas.cameras import Camera, CameraCreate, CameraRecord, CameraUpdate
from app.schemas.users import User
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID


router = APIRouter()


@router.get('/', response_model=List[Camera])
async def get_cameras(
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> List[Camera]:
    """
    Get cameras list
    """
    return CameraController.get_cameras(db)


@router.post('/', response_model=Camera)
async def create_camera(
    payload: CameraCreate,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> Camera:
    """
    Create camera
    """
    check_is_admin(user)
    return CameraController.create_camera(db, payload)


@router.get('/{camera_id}', response_model=Camera)
async def get_camera(
    camera_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> Camera:
    """
    Get camera
    """
    check_is_admin(user)
    return CameraController.get_camera(db, camera_id)


@router.get('/{camera_id}/records', response_model=List[CameraRecord])
async def get_camera_records(
    camera_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> Camera:
    """
    Get camera records
    """
    check_is_admin(user)
    return CameraController.get_camera_records(db, camera_id)


@router.delete('/{camera_id}/records')
async def delete_camera_records(
    camera_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> Camera:
    """
    Delete camera records
    """
    check_is_admin(user)
    return CameraController.delete_camera_records(db, camera_id)


@router.delete('/{camera_id}/records/{record_name}')
async def delete_camera_records(
    camera_id: UUID,
    record_name: str,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> Camera:
    """
    Delete camera record
    """
    check_is_admin(user)
    return CameraController.delete_camera_record(db, camera_id, record_name)


@router.put('/{camera_id}', response_model=Camera)
async def update_camera(
    camera_id: UUID,
    payload: CameraUpdate,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> Camera:
    """
    Update camera
    """
    check_is_admin(user)
    return CameraController.update_camera(db, camera_id, payload)


@router.delete('/{camera_id}')
async def delete_camera(
    camera_id: UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_session)
) -> None:
    """
    Delete camera
    """
    check_is_admin(user)
    return CameraController.delete_camera(db, camera_id)


@router.get('/{camera_id}/live')
async def stream_camera(
    camera_id: UUID,
    token: Optional[str] = None,
    auth: BaseAuth = Depends(get_auth),
    db: Session = Depends(get_session)
):
    """
    Get camera stream
    """
    user = auth.get_user_with_token(token, db)

    try:
        stream = CameraController.get_stream(db, camera_id)

        return StreamingResponse(
            CameraController.live(stream),
            media_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
