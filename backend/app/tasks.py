from fastapi import BackgroundTasks

from app.logger import logger


def enqueue_generate_3d(background_tasks: BackgroundTasks, cloth_id: int, model: str, quality: str) -> None:
    # Placeholder for AI pipeline; replace with Celery if needed.
    background_tasks.add_task(run_generate_3d, cloth_id, model, quality)


def enqueue_fit(background_tasks: BackgroundTasks, cloth3d_id: int, avatar_preset_id: int) -> None:
    background_tasks.add_task(run_fit, cloth3d_id, avatar_preset_id)


def run_generate_3d(cloth_id: int, model: str, quality: str) -> None:
    logger.info("Stub generate_3d called", extra={"cloth_id": cloth_id, "model": model, "quality": quality})
    # TODO: integrate Zero123 + InstantMesh pipeline and persist outputs.


def run_fit(cloth3d_id: int, avatar_preset_id: int) -> None:
    logger.info("Stub fit called", extra={"cloth3d_id": cloth3d_id, "avatar_preset_id": avatar_preset_id})
    # TODO: implement fitting pipeline and upload fitted glTF.


