from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Transition, Clip
from schemas import TransitionCreate, TransitionUpdate, TransitionResponse

router = APIRouter(tags=["transitions"])


@router.post("/api/clips/{clip_id}/transitions", response_model=TransitionResponse, status_code=201)
def create_transition(clip_id: int, data: TransitionCreate, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    transition = Transition(clip_id=clip_id, **data.model_dump())
    db.add(transition)
    db.commit()
    db.refresh(transition)
    return transition


@router.put("/api/transitions/{transition_id}", response_model=TransitionResponse)
def update_transition(transition_id: int, data: TransitionUpdate, db: Session = Depends(get_db)):
    transition = db.query(Transition).filter(Transition.id == transition_id).first()
    if not transition:
        raise HTTPException(status_code=404, detail="Transition not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(transition, key, value)
    db.commit()
    db.refresh(transition)
    return transition


@router.delete("/api/transitions/{transition_id}", status_code=204)
def delete_transition(transition_id: int, db: Session = Depends(get_db)):
    transition = db.query(Transition).filter(Transition.id == transition_id).first()
    if not transition:
        raise HTTPException(status_code=404, detail="Transition not found")
    db.delete(transition)
    db.commit()
