from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import json
import uuid
from datetime import datetime

from voice_engine import generate_clone_audio

BASE_DIR = Path(__file__).resolve().parent
LIBRARY_FILE = BASE_DIR / "voice_library.json"
HISTORY_FILE = BASE_DIR / "generation_history.json"
AUDIO_DIR = BASE_DIR / "audio_vault"
AUDIO_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Personal Voice Lab", version="2.0.0")

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
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class GeneratedAudio(BaseModel):
    id: str = Field(default_factory=lambda: f"audio-{uuid.uuid4().hex[:8]}")
    text: str
    profileId: str
    profileName: str
    pitch: float = 1.0
    rate: float = 1.0
    generatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    filePath: Optional[str] = None
    backend: str = "browser"
    duration: float = 0.0


def load_library() -> Dict[str, Any]:
    if LIBRARY_FILE.exists():
        try:
            return json.loads(LIBRARY_FILE.read_text())
        except Exception:
            return {"profiles": []}
    return {"profiles": []}


def save_library(data: Dict[str, Any]) -> None:
    LIBRARY_FILE.write_text(json.dumps(data, indent=2))


def load_history() -> List[Dict[str, Any]]:
    if HISTORY_FILE.exists():
        try:
            data = json.loads(HISTORY_FILE.read_text())
            return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def save_history(history: List[Dict[str, Any]]) -> None:
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


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
    return library


@app.post("/api/profiles")
def save_profile(profile: VoiceProfile) -> Dict[str, Any]:
    library = load_library()
    profiles = library.setdefault("profiles", [])
    profile.updatedAt = datetime.utcnow().isoformat()

    existing_index = next((i for i, item in enumerate(profiles) if item.get("id") == profile.id), None)
    if existing_index is not None:
        profiles[existing_index] = profile.model_dump()
    else:
        profiles.append(profile.model_dump())

    save_library(library)
    return library


@app.delete("/api/profile/{profile_id}")
def delete_profile(profile_id: str) -> Dict[str, Any]:
    library = load_library()
    profiles = library.get("profiles", [])
    library["profiles"] = [p for p in profiles if p.get("id") != profile_id]
    save_library(library)
    return library


@app.get("/api/profile/{profile_id}")
def get_profile(profile_id: str) -> Dict[str, Any]:
    library = load_library()
    for profile in library.get("profiles", []):
        if profile.get("id") == profile_id:
            return profile
    return default_profile().model_dump()


@app.get("/api/history")
def get_history() -> Dict[str, Any]:
    history = load_history()
    return {"history": sorted(history, key=lambda x: x.get("generatedAt", ""), reverse=True)}


@app.post("/api/history")
def add_to_history(audio: GeneratedAudio) -> Dict[str, Any]:
    history = load_history()
    history.append(audio.model_dump())
    save_history(history)
    return {"history": history}


@app.delete("/api/history/{audio_id}")
def delete_from_history(audio_id: str) -> Dict[str, Any]:
    history = load_history()
    history = [h for h in history if h.get("id") != audio_id]
    save_history(history)
    return {"history": history}


@app.post("/api/clear-history")
def clear_history() -> Dict[str, Any]:
    save_history([])
    return {"message": "History cleared."}


@app.post("/api/generate")
def generate_clone(payload: Dict[str, Any]) -> Dict[str, Any]:
    text = str(payload.get("text", "")).strip()
    if not text:
        return {"status": "error", "message": "Text is required."}

    profile = payload.get("profile") or {}
    output_file = AUDIO_DIR / f"audio-{uuid.uuid4().hex[:8]}.wav"

    synthesis = generate_clone_audio(
        text=text,
        profile=profile,
        output_path=str(output_file),
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


@app.post("/api/upload-audio")
async def upload_audio(file: UploadFile = File(...)) -> Dict[str, Any]:
    try:
        content = await file.read()
        filename = f"upload-{uuid.uuid4().hex[:8]}.wav"
        filepath = AUDIO_DIR / filename
        with open(filepath, "wb") as f:
            f.write(content)
        return {"status": "ok", "filename": filename, "path": str(filepath)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/download/{filename}")
def download_audio(filename: str):
    filepath = AUDIO_DIR / filename
    if filepath.exists():
        return FileResponse(filepath, filename=filename)
    return {"status": "error", "message": "File not found."}


@app.post("/api/export-library")
def export_library() -> Dict[str, Any]:
    return load_library()


@app.post("/api/import-library")
def import_library(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        profiles = payload.get("profiles", [])
        library = {"profiles": profiles}
        save_library(library)
        return {"status": "ok", "message": f"Imported {len(profiles)} profiles."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/settings")
def get_settings() -> Dict[str, Any]:
    return {
        "backend": "browser",
        "autoSave": True,
        "maxHistoryItems": 100,
        "theme": "dark",
    }


app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
