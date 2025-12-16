from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class ClothUploadResponse(BaseModel):
    cloth_id: int
    image_url: HttpUrl
    status: str


class Generate3DRequest(BaseModel):
    model: str = "zero123+instantmesh"
    quality: str = "low"


class Generate3DResponse(BaseModel):
    cloth3d_id: int
    status: str


class AvatarPresetResponse(BaseModel):
    id: int
    name: str
    height_cm: Optional[float] = None
    gltf_url: HttpUrl
    thumbnail_url: Optional[HttpUrl] = None


class FitRequest(BaseModel):
    cloth3d_id: int
    avatar_preset_id: int


class FitResponse(BaseModel):
    fitting_session_id: int
    status: str


class SessionResultResponse(BaseModel):
    status: str
    cloth3d_url: Optional[HttpUrl] = None
    avatar_preset_id: Optional[int] = None
    fitted_gltf_url: Optional[HttpUrl] = None
    thumb_url: Optional[HttpUrl] = None


class AvatarPresetListResponse(BaseModel):
    items: List[AvatarPresetResponse]


