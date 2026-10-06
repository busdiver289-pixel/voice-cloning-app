from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import json
import uuid

from voice_engine import generate_clone_audio

BASE_DIR = Path(__file__).resolve().parent
LIBRARY_FILE = BASE_DIR / "voice_library.json"

app = FastAPI(title="Personal Voice Lab", version="1.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VoiceProfile(BaseModel):
    id: str = Field(default_factory=lambda: f"profile-{uuid.uuid4().hex[:8]}")
    name: str = "My Voice"
    notes: str = ""
    pitch: float = 1.0
    rate: float = 1.0
    duration: float = 0.0
    tags: List[str] = Field(default_factory=lambda: ["Warm", "Conversational", "Balanced"])
    sampleUrl: Optional[str] = None


def load_library() -> Dict[str, Any]:
    if LIBRARY_FILE.exists():
        try:
            return json.loads(LIBRARY_FILE.read_text())
        except Exception:
            return {"profiles": []}
    return {"profiles": []}


def save_library(data: Dict[str, Any]) -> None:
    LIBRARY_FILE.write_text(json.dumps(data, indent=2))


def default_profile() -> VoiceProfile:
    return VoiceProfile(name="My Voice")


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "message": "Personal voice lab is running."}


@app.get("/api/profiles")
def get_profiles() -> Dict[str, Any]:
    library = load_library()
    profiles = library.get("profiles", [])
    if not profiles:
        default = default_profile().model_dump()
        library["profiles"] = [default]
        save_library(library)
    return load_library()


@app.post("/api/profiles")
def save_profile(profile: VoiceProfile) -> Dict[str, Any]:
    library = load_library()
    profiles = library.setdefault("profiles", [])

    existing_index = next((i for i, item in enumerate(profiles) if item.get("id") == profile.id), None)
    if existing_index is not None:
        profiles[existing_index] = profile.model_dump()
    else:
        profiles.append(profile.model_dump())

    save_library(library)
    return library


@app.get("/api/profile/{profile_id}")
def get_profile(profile_id: str) -> Dict[str, Any]:
    library = load_library()
    for profile in library.get("profiles", []):
        if profile.get("id") == profile_id:
            return profile
    return default_profile().model_dump()


@app.post("/api/generate")
def generate_clone(payload: Dict[str, Any]) -> Dict[str, Any]:
    text = str(payload.get("text", "")).strip()
    if not text:
        return {"status": "error", "message": "Text is required."}

    profile = payload.get("profile") or {}

    synthesis = generate_clone_audio(
        text=text,
        profile=profile,
        output_path=str(BASE_DIR / "generated_voice.wav"),
    )

    response = {
        "status": synthesis.get("status", "ok"),
        "backend": synthesis.get("backend", "browser"),
        "message": synthesis.get("message", "Clone generation request accepted."),
        "profile": profile,
        "text": text,
    }
    if synthesis.get("output"):
        response["output"] = synthesis["output"]
    if synthesis.get("details"):
        response["details"] = synthesis["details"]

    return response


app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
