from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Keyframe, Clip
from schemas import KeyframeCreate, KeyframeUpdate, KeyframeResponse

router = APIRouter(tags=["keyframes"])


@router.get("/api/clips/{clip_id}/keyframes", response_model=list[KeyframeResponse])
def list_keyframes(clip_id: int, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    return db.query(Keyframe).filter(Keyframe.clip_id == clip_id).order_by(Keyframe.time).all()


@router.post("/api/clips/{clip_id}/keyframes", response_model=KeyframeResponse, status_code=201)
def create_keyframe(clip_id: int, data: KeyframeCreate, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    keyframe = Keyframe(clip_id=clip_id, **data.model_dump())
    db.add(keyframe)
    db.commit()
    db.refresh(keyframe)
    return keyframe


@router.put("/api/keyframes/{keyframe_id}", response_model=KeyframeResponse)
def update_keyframe(keyframe_id: int, data: KeyframeUpdate, db: Session = Depends(get_db)):
    keyframe = db.query(Keyframe).filter(Keyframe.id == keyframe_id).first()
    if not keyframe:
        raise HTTPException(status_code=404, detail="Keyframe not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(keyframe, key, value)
    db.commit()
    db.refresh(keyframe)
    return keyframe


@router.delete("/api/keyframes/{keyframe_id}", status_code=204)
def delete_keyframe(keyframe_id: int, db: Session = Depends(get_db)):
    keyframe = db.query(Keyframe).filter(Keyframe.id == keyframe_id).first()
    if not keyframe:
        raise HTTPException(status_code=404, detail="Keyframe not found")
    db.delete(keyframe)
    db.commit()
