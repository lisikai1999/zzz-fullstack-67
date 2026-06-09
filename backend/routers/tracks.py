from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Track, Project
from schemas import TrackCreate, TrackUpdate, TrackResponse

router = APIRouter(tags=["tracks"])


@router.post("/api/projects/{project_id}/tracks", response_model=TrackResponse, status_code=201)
def create_track(project_id: int, data: TrackCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    track = Track(project_id=project_id, **data.model_dump())
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


@router.put("/api/tracks/{track_id}", response_model=TrackResponse)
def update_track(track_id: int, data: TrackUpdate, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(track, key, value)
    db.commit()
    db.refresh(track)
    return track


@router.delete("/api/tracks/{track_id}", status_code=204)
def delete_track(track_id: int, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    db.delete(track)
    db.commit()
