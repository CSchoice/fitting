from fastapi import APIRouter, Depends
from sqlmodel import select

from app import models, schemas
from app.db import get_session

router = APIRouter(prefix="/avatar-presets", tags=["avatar-presets"])


@router.get("", response_model=schemas.AvatarPresetListResponse)
async def list_presets(session=Depends(get_session)):
    presets = await session.exec(select(models.AvatarPreset))
    items = presets.all()
    return schemas.AvatarPresetListResponse(items=items)


