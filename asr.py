from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from languages import detect_language_from_text, normalize_language


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
    manual_transcript: Optional[str] = None,
    backend: str = "faster-whisper",
    model: str = "small",
) -> ASRResult:
    language = normalize_language(language)
    backend = backend.strip().lower()

    if manual_transcript and backend != "manual":
        raise ASRUnavailable(
            "Manual transcripts are only allowed with --asr-backend manual. "
            "Use faster-whisper without --transcript for real ASR transcription."
        )

    if backend == "manual":
        if not manual_transcript:
            raise ASRUnavailable(
                "Manual ASR backend requires --transcript or a sidecar .txt file."
            )
        detected = language if language != "auto" else detect_language_from_text(manual_transcript)
        return ASRResult(
            transcript=manual_transcript.strip(),
            language=detected,
            backend="manual",
            model="sidecar_or_cli_transcript",
            note="Used provided transcript so the rest of the pipeline can run without ASR setup.",
        )

    if backend in ("faster-whisper", "faster_whisper"):
        try:
            return _transcribe_with_faster_whisper(audio_path, language, model)
        except ImportError as exc:
            raise ASRUnavailable(
                "faster-whisper is not installed. Run `.venv/bin/python -m pip install -r requirements-optional.txt`."
            ) from exc
        except Exception as exc:
            raise ASRUnavailable(str(exc)) from exc

    if backend == "whisper":
        try:
            return _transcribe_with_whisper(audio_path, language, model)
        except ImportError as exc:
            raise ASRUnavailable(
                "openai-whisper is not installed. Install it or use --asr-backend faster-whisper."
            ) from exc
        except Exception as exc:
            raise ASRUnavailable(str(exc)) from exc

    raise ASRUnavailable(
        "Unsupported ASR backend '{}'. Use faster-whisper, whisper, or manual.".format(backend)
    )


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


def _transcribe_with_whisper(audio_path: Path, language: str, model: str) -> ASRResult:
    import whisper

    whisper_model = whisper.load_model(model)
    language_arg = None if language == "auto" else language
    result = whisper_model.transcribe(str(audio_path), language=language_arg)
    transcript = result.get("text", "").strip()
    detected_language = language if language != "auto" else result.get("language", "en")
    return ASRResult(
        transcript=transcript,
        language=detected_language,
        backend="openai-whisper",
        model=model,
        note="Transcribed with openai-whisper.",
    )
