from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    width = Column(Integer, nullable=False, default=1920)
    height = Column(Integer, nullable=False, default=1080)
    fps = Column(Integer, nullable=False, default=30)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tracks = relationship("Track", back_populates="project", cascade="all, delete-orphan", order_by="Track.order")
    media = relationship("Media", back_populates="project", cascade="all, delete-orphan")


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    proxy_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="media")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    muted = Column(Boolean, nullable=False, default=False)
    locked = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        CheckConstraint("type IN ('video', 'audio')", name="check_track_type"),
    )

    project = relationship("Project", back_populates="tracks")
    clips = relationship("Clip", back_populates="track", cascade="all, delete-orphan")


class Clip(Base):
    __tablename__ = "clips"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=False)
    position = Column(Float, nullable=False, default=0)
    in_point = Column(Float, nullable=False, default=0)
    out_point = Column(Float, nullable=False)
    layer = Column(Integer, nullable=False, default=0)

    # Intrinsic transform (PiP base position/scale, independent of keyframes)
    pip_x = Column(Float, nullable=False, default=0)
    pip_y = Column(Float, nullable=False, default=0)
    pip_scale_x = Column(Float, nullable=False, default=1.0)
    pip_scale_y = Column(Float, nullable=False, default=1.0)
    pip_rotation = Column(Float, nullable=False, default=0)
    pip_opacity = Column(Float, nullable=False, default=1.0)

    track = relationship("Track", back_populates="clips")
    media = relationship("Media")
    transitions = relationship("Transition", back_populates="clip", cascade="all, delete-orphan")
    keyframes = relationship("Keyframe", back_populates="clip", cascade="all, delete-orphan")

    @property
    def duration(self):
        return self.out_point - self.in_point


class Transition(Base):
    __tablename__ = "transitions"

    id = Column(Integer, primary_key=True, index=True)
    clip_id = Column(Integer, ForeignKey("clips.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    duration = Column(Float, nullable=False, default=0.5)
    position = Column(String, nullable=False, default="end")

    __table_args__ = (
        CheckConstraint("type IN ('fade_in', 'fade_out', 'dissolve', 'wipe_left', 'wipe_right')", name="check_transition_type"),
        CheckConstraint("position IN ('start', 'end')", name="check_transition_position"),
    )

    clip = relationship("Clip", back_populates="transitions")


class Keyframe(Base):
    __tablename__ = "keyframes"

    id = Column(Integer, primary_key=True, index=True)
    clip_id = Column(Integer, ForeignKey("clips.id", ondelete="CASCADE"), nullable=False)
    time = Column(Float, nullable=False)
    property = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    easing = Column(String, nullable=False, default="linear")

    __table_args__ = (
        CheckConstraint(
            "property IN ('scale_x', 'scale_y', 'position_x', 'position_y', 'rotation', 'opacity')",
            name="check_keyframe_property"
        ),
        CheckConstraint(
            "easing IN ('linear', 'ease_in', 'ease_out', 'ease_in_out')",
            name="check_keyframe_easing"
        ),
    )

    clip = relationship("Clip", back_populates="keyframes")
