"""Speech-to-text via Whisper (loaded once per worker process)."""
from functools import lru_cache
from app.core.config import settings


@lru_cache
def _model():
    import whisper
    return whisper.load_model(settings.WHISPER_MODEL)


def transcribe(audio_path: str) -> str:
    result = _model().transcribe(audio_path)
    return result["text"].strip()
