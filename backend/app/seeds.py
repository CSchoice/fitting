from sqlmodel import select

from app import models
from app.config import settings
from app.logger import logger


async def seed_avatar_presets(session) -> None:
    # Check if any presets exist
    existing = await session.exec(select(models.AvatarPreset))
    if existing.first():
        return

    presets = [
        models.AvatarPreset(
            name="slim",
            height_cm=170,
            notes="슬림 체형 프리셋",
            gltf_url=settings.preset_slim_gltf,
            thumbnail_url=settings.preset_slim_thumb,
        ),
        models.AvatarPreset(
            name="regular",
            height_cm=170,
            notes="일반 체형 프리셋",
            gltf_url=settings.preset_regular_gltf,
            thumbnail_url=settings.preset_regular_thumb,
        ),
        models.AvatarPreset(
            name="curvy",
            height_cm=170,
            notes="볼륨 체형 프리셋",
            gltf_url=settings.preset_curvy_gltf,
            thumbnail_url=settings.preset_curvy_thumb,
        ),
    ]

    for preset in presets:
        session.add(preset)
    await session.commit()
    logger.info("Seeded avatar presets", extra={"count": len(presets)})


