from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import projects, tracks, clips, transitions, keyframes, media


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Video Editor API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(tracks.router)
app.include_router(clips.router)
app.include_router(transitions.router)
app.include_router(keyframes.router)
app.include_router(media.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
