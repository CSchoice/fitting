from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import select

from app import models, schemas
from app.db import get_session
from app.tasks import enqueue_fit

router = APIRouter(prefix="/fit", tags=["fit"])


@router.post("", response_model=schemas.FitResponse)
async def fit(
    payload: schemas.FitRequest,
    background_tasks: BackgroundTasks,
    session=Depends(get_session),
):
    cloth3d = await session.exec(
        select(models.Cloth3D).where(models.Cloth3D.id == payload.cloth3d_id)
    )
    cloth3d_obj = cloth3d.one_or_none()
    if not cloth3d_obj:
        raise HTTPException(status_code=404, detail="cloth3d not found")

    preset = await session.exec(
        select(models.AvatarPreset).where(models.AvatarPreset.id == payload.avatar_preset_id)
    )
    preset_obj = preset.one_or_none()
    if not preset_obj:
        raise HTTPException(status_code=404, detail="avatar preset not found")

    session_row = models.FittingSession(
        cloth3d_id=payload.cloth3d_id,
        avatar_preset_id=payload.avatar_preset_id,
        status="processing",
    )
    session.add(session_row)
    await session.commit()
    await session.refresh(session_row)

    enqueue_fit(background_tasks, cloth3d_id=payload.cloth3d_id, avatar_preset_id=payload.avatar_preset_id)

    return schemas.FitResponse(fitting_session_id=session_row.id, status=session_row.status)


