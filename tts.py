from __future__ import annotations

import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from languages import language_profile, normalize_language


@dataclass
class TTSResult:
    text: str
    language: str
    output_path: str
    backend: str
    voice: str
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def synthesize_speech(
    text: str,
    output_path: Path,
    language: str = "en",
    voice: Optional[str] = None,
    backend: str = "macos_say",
) -> TTSResult:
    language = normalize_language(language)
    if language == "auto":
        language = "en"
    backend = backend.strip().lower()

    if backend != "macos_say":
        raise ValueError("Only macos_say is implemented in version 1.")

    if not shutil.which("say"):
        raise RuntimeError("macOS 'say' command was not found.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    selected_voice = voice or language_profile(language).macos_voice

    if output_path.suffix.lower() == ".aiff":
        aiff_path = output_path
        wav_note = "Generated AIFF directly with macOS say."
    else:
        aiff_path = output_path.with_suffix(".aiff")
        wav_note = "Generated AIFF with macOS say, then converted to WAV with afconvert."

    subprocess.run(
        ["say", "-v", selected_voice, "-o", str(aiff_path), text],
        check=True,
    )

    if output_path.suffix.lower() != ".aiff":
        if not shutil.which("afconvert"):
            raise RuntimeError("macOS 'afconvert' command was not found.")
        subprocess.run(
            ["afconvert", str(aiff_path), str(output_path), "-f", "WAVE", "-d", "LEI16"],
            check=True,
        )
        if aiff_path != output_path:
            aiff_path.unlink(missing_ok=True)

    return TTSResult(
        text=text,
        language=language,
        output_path=str(output_path),
        backend="macos_say",
        voice=selected_voice,
        note=wav_note,
    )
