from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlmodel import select

from app import models, schemas
from app.db import get_session
from app.storage import presigned_url, upload_bytes
from app.tasks import enqueue_generate_3d

router = APIRouter(prefix="/clothes", tags=["clothes"])


@router.post("/upload-image", response_model=schemas.ClothUploadResponse)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: int | None = None,
    session=Depends(get_session),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")
    key = upload_bytes(content, content_type=file.content_type or "application/octet-stream")
    image_url = presigned_url(key)

    cloth = models.Cloth(user_id=user_id, image_url=image_url, status="uploaded")
    session.add(cloth)
    await session.commit()
    await session.refresh(cloth)

    return schemas.ClothUploadResponse(cloth_id=cloth.id, image_url=image_url, status=cloth.status)


@router.post("/{cloth_id}/generate-3d", response_model=schemas.Generate3DResponse)
async def generate_3d(
    cloth_id: int,
    payload: schemas.Generate3DRequest,
    background_tasks: BackgroundTasks,
    session=Depends(get_session),
):
    cloth = await session.exec(select(models.Cloth).where(models.Cloth.id == cloth_id))
    cloth_obj = cloth.one_or_none()
    if not cloth_obj:
        raise HTTPException(status_code=404, detail="cloth not found")

    cloth3d = models.Cloth3D(
        cloth_id=cloth_id,
        model_used=payload.model,
        status="processing",
    )
    session.add(cloth3d)
    await session.commit()
    await session.refresh(cloth3d)

    enqueue_generate_3d(background_tasks, cloth_id=cloth_id, model=payload.model, quality=payload.quality)

    return schemas.Generate3DResponse(cloth3d_id=cloth3d.id, status=cloth3d.status)


