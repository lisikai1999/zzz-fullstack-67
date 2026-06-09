from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


# --- Media ---
class MediaResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    original_path: str
    proxy_path: Optional[str]
    thumbnail_path: Optional[str]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    file_size: Optional[int]
    mime_type: Optional[str]

    class Config:
        from_attributes = True


# --- Keyframes ---
class KeyframeCreate(BaseModel):
    time: float
    property: Literal["scale_x", "scale_y", "position_x", "position_y", "rotation", "opacity"]
    value: float
    easing: Literal["linear", "ease_in", "ease_out", "ease_in_out"] = "linear"


class KeyframeUpdate(BaseModel):
    time: Optional[float] = None
    value: Optional[float] = None
    easing: Optional[Literal["linear", "ease_in", "ease_out", "ease_in_out"]] = None


class KeyframeResponse(BaseModel):
    id: int
    clip_id: int
    time: float
    property: str
    value: float
    easing: str

    class Config:
        from_attributes = True


# --- Transitions ---
class TransitionCreate(BaseModel):
    type: Literal["fade_in", "fade_out", "dissolve", "wipe_left", "wipe_right"]
    duration: float = 0.5
    position: Literal["start", "end"] = "end"


class TransitionUpdate(BaseModel):
    type: Optional[Literal["fade_in", "fade_out", "dissolve", "wipe_left", "wipe_right"]] = None
    duration: Optional[float] = None


class TransitionResponse(BaseModel):
    id: int
    clip_id: int
    type: str
    duration: float
    position: str

    class Config:
        from_attributes = True


# --- Clips ---
class ClipCreate(BaseModel):
    media_id: int
    position: float = 0
    in_point: float = 0
    out_point: float
    layer: int = 0
    pip_x: float = 0
    pip_y: float = 0
    pip_scale_x: float = 1.0
    pip_scale_y: float = 1.0
    pip_rotation: float = 0
    pip_opacity: float = 1.0


class ClipUpdate(BaseModel):
    position: Optional[float] = None
    in_point: Optional[float] = None
    out_point: Optional[float] = None
    track_id: Optional[int] = None
    layer: Optional[int] = None
    pip_x: Optional[float] = None
    pip_y: Optional[float] = None
    pip_scale_x: Optional[float] = None
    pip_scale_y: Optional[float] = None
    pip_rotation: Optional[float] = None
    pip_opacity: Optional[float] = None


class ClipSplit(BaseModel):
    split_time: float


class ClipResponse(BaseModel):
    id: int
    track_id: int
    media_id: int
    position: float
    in_point: float
    out_point: float
    duration: float
    layer: int
    pip_x: float
    pip_y: float
    pip_scale_x: float
    pip_scale_y: float
    pip_rotation: float
    pip_opacity: float
    transitions: list[TransitionResponse] = []
    keyframes: list[KeyframeResponse] = []

    class Config:
        from_attributes = True


# --- Tracks ---
class TrackCreate(BaseModel):
    name: str
    type: Literal["video", "audio"]
    order: int = 0


class TrackUpdate(BaseModel):
    name: Optional[str] = None
    order: Optional[int] = None
    muted: Optional[bool] = None
    locked: Optional[bool] = None


class TrackResponse(BaseModel):
    id: int
    project_id: int
    name: str
    type: str
    order: int
    muted: bool
    locked: bool
    clips: list[ClipResponse] = []

    class Config:
        from_attributes = True


# --- Projects ---
class ProjectCreate(BaseModel):
    name: str
    width: int = 1920
    height: int = 1080
    fps: int = 30


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    width: int
    height: int
    fps: int
    created_at: datetime
    updated_at: datetime
    tracks: list[TrackResponse] = []

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    id: int
    name: str
    width: int
    height: int
    fps: int
    created_at: datetime

    class Config:
        from_attributes = True
