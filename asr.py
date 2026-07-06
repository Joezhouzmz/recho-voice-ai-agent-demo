from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path

from languages import normalize_language


class ASRUnavailable(RuntimeError):
    pass


@dataclass
class ASRResult:
    transcript: str
    language: str
    backend: str
    model: str
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def transcribe_audio(
    audio_path: Path,
    language: str = "auto",
    model: str = "small",
) -> ASRResult:
    language = normalize_language(language)
    try:
        return _transcribe_with_faster_whisper(audio_path, language, model)
    except ImportError as exc:
        raise ASRUnavailable(
            "faster-whisper is not installed. Run `.venv/bin/python -m pip install -r requirements-optional.txt`."
        ) from exc
    except Exception as exc:
        raise ASRUnavailable(str(exc)) from exc


def _transcribe_with_faster_whisper(audio_path: Path, language: str, model: str) -> ASRResult:
    # Local macOS demo environments can load OpenMP twice through Torch/Silero
    # and CTranslate2. Keep this scoped to the faster-whisper backend.
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    os.environ.setdefault("OMP_NUM_THREADS", "1")

    from faster_whisper import WhisperModel

    whisper = WhisperModel(model, device="cpu", compute_type="int8")
    language_arg = None if language == "auto" else language
    segments, info = whisper.transcribe(str(audio_path), language=language_arg)
    transcript = " ".join(segment.text.strip() for segment in segments).strip()
    detected_language = language if language != "auto" else getattr(info, "language", "en")
    return ASRResult(
        transcript=transcript,
        language=detected_language,
        backend="faster-whisper",
        model=model,
        note="Transcribed with faster-whisper.",
    )
