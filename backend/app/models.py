import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )


class Cloth(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    image_url: str
    status: str = Field(default="uploaded")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )


class Cloth3D(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cloth_id: int = Field(foreign_key="cloth.id")
    model_used: str
    gltf_url: Optional[str] = None
    obj_url: Optional[str] = None
    thumb_url: Optional[str] = None
    status: str = Field(default="processing")
    log: Optional[str] = None
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )


class AvatarPreset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    height_cm: Optional[float] = None
    notes: Optional[str] = None
    gltf_url: str
    thumbnail_url: Optional[str] = None
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )


class FittingSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    cloth3d_id: int = Field(foreign_key="cloth3d.id")
    avatar_preset_id: int = Field(foreign_key="avatarpreset.id")
    fitted_gltf_url: Optional[str] = None
    thumb_url: Optional[str] = None
    status: str = Field(default="processing")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )


