from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import json

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "voice_profile.json"

app = FastAPI(title="VoiceClone Lab", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VoiceProfile(BaseModel):
    name: str = "My Voice"
    pitch: float = 1.0
    rate: float = 1.0
    duration: float = 0.0
    tags: List[str] = Field(default_factory=lambda: ["Warm", "Conversational", "Balanced"])
    sampleUrl: Optional[str] = None


def load_profile() -> VoiceProfile:
    if DATA_FILE.exists():
        try:
            raw = json.loads(DATA_FILE.read_text())
            return VoiceProfile(**raw)
        except Exception:
            pass
    return VoiceProfile()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "message": "VoiceClone Lab API is running."}


@app.get("/api/profile")
def get_profile() -> dict:
    return load_profile().model_dump()


@app.post("/api/profile")
def save_profile(profile: VoiceProfile) -> dict:
    DATA_FILE.write_text(json.dumps(profile.model_dump(), indent=2))
    return profile.model_dump()


@app.post("/api/generate")
def generate_clone(payload: dict) -> dict:
    text = str(payload.get("text", "")).strip()
    if not text:
        return {"status": "error", "message": "Text is required."}

    profile = load_profile()
    return {
        "status": "ok",
        "message": "Clone generation request accepted.",
        "profile": profile.model_dump(),
        "text": text,
        "pitch": float(payload.get("pitch", profile.pitch)),
        "rate": float(payload.get("rate", profile.rate)),
    }


app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
