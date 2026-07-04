from __future__ import annotations

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
    backend: str = "auto",
    model: str = "base",
) -> ASRResult:
    language = normalize_language(language)
    backend = backend.strip().lower()

    if manual_transcript:
        detected = language if language != "auto" else detect_language_from_text(manual_transcript)
        return ASRResult(
            transcript=manual_transcript.strip(),
            language=detected,
            backend="manual",
            model="sidecar_or_cli_transcript",
            note="Used provided transcript so the rest of the pipeline can run without ASR setup.",
        )

    if backend in ("auto", "faster-whisper", "faster_whisper"):
        try:
            return _transcribe_with_faster_whisper(audio_path, language, model)
        except ImportError:
            if backend not in ("auto",):
                raise
        except Exception as exc:
            if backend not in ("auto",):
                raise ASRUnavailable(str(exc)) from exc

    if backend in ("auto", "whisper"):
        try:
            return _transcribe_with_whisper(audio_path, language, model)
        except ImportError:
            if backend != "auto":
                raise
        except Exception as exc:
            if backend != "auto":
                raise ASRUnavailable(str(exc)) from exc

    raise ASRUnavailable(
        "No ASR backend available. Install faster-whisper/openai-whisper, "
        "or pass --transcript, or add a sidecar .txt file next to the audio."
    )


def _transcribe_with_faster_whisper(audio_path: Path, language: str, model: str) -> ASRResult:
    from faster_whisper import WhisperModel

    whisper = WhisperModel(model, device="auto", compute_type="auto")
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
