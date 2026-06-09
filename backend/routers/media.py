import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Media, Project
from schemas import MediaResponse
from services.proxy import generate_proxy, probe_video_metadata

router = APIRouter(prefix="/api/media", tags=["media"])

MEDIA_DIR = Path(__file__).parent.parent / "media"
ORIGINALS_DIR = MEDIA_DIR / "originals"
PROXIES_DIR = MEDIA_DIR / "proxies"


@router.post("/upload", response_model=MediaResponse, status_code=201)
async def upload_media(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)

    file_path = ORIGINALS_DIR / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(file_path)

    media = Media(
        project_id=project_id,
        filename=file.filename,
        original_path=str(file_path),
        mime_type=file.content_type,
        file_size=file_size,
    )

    width, height, duration = _probe_media(file_path, file.content_type)
    media.width = width
    media.height = height
    media.duration = duration

    db.add(media)
    db.commit()
    db.refresh(media)

    proxy_path = generate_proxy(media, PROXIES_DIR)
    if proxy_path:
        media.proxy_path = str(proxy_path)
        db.commit()
        db.refresh(media)

    return media


@router.get("/{media_id}", response_model=MediaResponse)
def get_media(media_id: int, db: Session = Depends(get_db)):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media


@router.get("/{media_id}/stream")
def stream_media(media_id: int, db: Session = Depends(get_db)):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not os.path.exists(media.original_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(media.original_path, media_type=media.mime_type)


@router.get("/{media_id}/proxy")
def stream_proxy(media_id: int, db: Session = Depends(get_db)):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not media.proxy_path or not os.path.exists(media.proxy_path):
        if os.path.exists(media.original_path):
            return FileResponse(media.original_path, media_type=media.mime_type)
        raise HTTPException(status_code=404, detail="No proxy available")
    proxy_mime = "video/mp4" if media.proxy_path.endswith(".mp4") else "image/jpeg"
    return FileResponse(media.proxy_path, media_type=proxy_mime)


def _probe_media(file_path: Path, content_type: str | None):
    width, height, duration = None, None, None
    if content_type and content_type.startswith("image/"):
        try:
            from PIL import Image
            img = Image.open(file_path)
            width, height = img.size
            img.close()
        except Exception:
            pass
    elif content_type and content_type.startswith("video/"):
        info = probe_video_metadata(file_path)
        width = info.get("width", 1920)
        height = info.get("height", 1080)
        duration = info.get("duration", 10.0)
    return width, height, duration
