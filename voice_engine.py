import os
from pathlib import Path
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent


def _backend() -> str:
    return os.getenv("VOICE_BACKEND", "browser").lower()


def build_voice_profile(profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    profile = profile or {}
    return {
        "name": profile.get("name", "My Voice"),
        "pitch": float(profile.get("pitch", 1.0)),
        "rate": float(profile.get("rate", 1.0)),
        "duration": float(profile.get("duration", 0.0)),
        "tags": profile.get("tags") or ["Warm", "Conversational", "Balanced"],
        "sampleUrl": profile.get("sampleUrl") or "",
    }


def generate_clone_audio(text: str, profile: Optional[Dict[str, Any]] = None, output_path: Optional[str] = None) -> Dict[str, Any]:
    profile = build_voice_profile(profile)
    backend = _backend()

    if backend == "xtts":
        try:
            from TTS.api import TTS
        except Exception as exc:  # pragma: no cover
            return {
                "status": "error",
                "message": "XTTS backend selected, but the TTS package is not installed.",
                "details": str(exc),
                "backend": backend,
                "profile": profile,
                "text": text,
            }

        model_name = os.getenv("XTTS_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2")
        output = Path(output_path) if output_path else BASE_DIR / "generated_voice.wav"
        tts = TTS(model_name=model_name, progress_bar=False, gpu=False)

        sample_audio = profile.get("sampleUrl")
        if sample_audio and sample_audio.startswith("http"):
            # This is intentionally a placeholder path for a configured audio reference.
            # In a real environment, you would read the uploaded/reference file and pass it to XTTS.
            reference = sample_audio
        else:
            reference = str(BASE_DIR / "voice_reference.wav")

        tts.tts_to_file(
            text=text,
            file_path=str(output),
            speaker_wav=reference,
            language="en",
        )

        return {
            "status": "ok",
            "backend": backend,
            "message": "Open-source XTTS synthesis completed.",
            "output": str(output),
            "profile": profile,
            "text": text,
        }

    return {
        "status": "demo",
        "backend": backend,
        "message": "Demo mode: browser speech synthesis is used for playback. Configure a local XTTS backend for real voice-cloning synthesis.",
        "profile": profile,
        "text": text,
    }
