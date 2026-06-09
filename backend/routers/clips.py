from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Clip, Track, Keyframe, Transition
from schemas import ClipCreate, ClipUpdate, ClipSplit, ClipResponse

router = APIRouter(tags=["clips"])


@router.post("/api/tracks/{track_id}/clips", response_model=ClipResponse, status_code=201)
def create_clip(track_id: int, data: ClipCreate, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    clip = Clip(track_id=track_id, **data.model_dump())
    db.add(clip)
    db.commit()
    db.refresh(clip)
    return _clip_response(clip)


@router.put("/api/clips/{clip_id}", response_model=ClipResponse)
def update_clip(clip_id: int, data: ClipUpdate, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(clip, key, value)
    db.commit()
    db.refresh(clip)
    return _clip_response(clip)


@router.post("/api/clips/{clip_id}/split", response_model=list[ClipResponse])
def split_clip(clip_id: int, data: ClipSplit, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")

    relative_split = data.split_time - clip.position
    clip_duration = clip.out_point - clip.in_point

    if relative_split <= 0 or relative_split >= clip_duration:
        raise HTTPException(status_code=400, detail="Split time must be within clip bounds")

    original_out = clip.out_point

    new_clip = Clip(
        track_id=clip.track_id,
        media_id=clip.media_id,
        position=data.split_time,
        in_point=clip.in_point + relative_split,
        out_point=original_out,
        layer=clip.layer,
    )
    db.add(new_clip)
    db.flush()

    clip.out_point = clip.in_point + relative_split

    for kf in list(clip.keyframes):
        if kf.time >= relative_split:
            kf.clip_id = new_clip.id
            kf.time -= relative_split

    for tr in list(clip.transitions):
        if tr.position == "end":
            tr.clip_id = new_clip.id

    db.commit()
    db.refresh(clip)
    db.refresh(new_clip)
    return [_clip_response(clip), _clip_response(new_clip)]


@router.delete("/api/clips/{clip_id}", status_code=204)
def delete_clip(clip_id: int, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    db.delete(clip)
    db.commit()


def _clip_response(clip: Clip) -> ClipResponse:
    return ClipResponse(
        id=clip.id,
        track_id=clip.track_id,
        media_id=clip.media_id,
        position=clip.position,
        in_point=clip.in_point,
        out_point=clip.out_point,
        duration=clip.out_point - clip.in_point,
        layer=clip.layer,
        transitions=[t for t in clip.transitions],
        keyframes=[k for k in clip.keyframes],
    )
