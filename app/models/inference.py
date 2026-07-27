import os
import tempfile
from typing import Any

_models: dict[str, Any] = {}


def load_model(model_name: str):
    if model_name in _models:
        return _models[model_name]
    import whisper
    _models[model_name] = whisper.load_model(model_name, device="cpu")
    return _models[model_name]


def get_available_models() -> list[str]:
    return list(_models.keys())


class InferenceEngine:
    def __init__(self, model_name: str):
        self._model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            self._model = load_model(self._model_name)
        return self._model

    def transcribe(self, audio_bytes: bytes) -> dict:
        model = self._get_model()
        if model is None:
            raise RuntimeError("Model is not loaded")
        if not audio_bytes:
            raise ValueError("Audio bytes are empty")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        try:
            result = model.transcribe(temp_path)
            segments = result.get("segments", [])
            duration = result.get("duration", 0.0)
            if duration == 0.0 and segments:
                duration = max(seg["end"] for seg in segments)
            return {
                "text": result.get("text", ""),
                "duration": duration,
                "segments": [
                    {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
                    for seg in segments
                ],
            }
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass