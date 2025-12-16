from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app import models, schemas
from app.db import get_session

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/{session_id}/result", response_model=schemas.SessionResultResponse)
async def get_result(session_id: int, session=Depends(get_session)):
    result = await session.exec(
        select(models.FittingSession).where(models.FittingSession.id == session_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="session not found")

    return schemas.SessionResultResponse(
        status=row.status,
        cloth3d_url=None,  # optional: add if stored
        avatar_preset_id=row.avatar_preset_id,
        fitted_gltf_url=row.fitted_gltf_url,
        thumb_url=row.thumb_url,
    )


