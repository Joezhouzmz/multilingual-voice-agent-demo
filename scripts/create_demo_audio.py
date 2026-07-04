from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from languages import LANGUAGE_PROFILES
from tts import synthesize_speech


def main() -> int:
    sample_inputs_dir = ROOT / "sample_inputs"
    sample_inputs_dir.mkdir(parents=True, exist_ok=True)

    for code, profile in LANGUAGE_PROFILES.items():
        audio_path = sample_inputs_dir / "input_{}.wav".format(code)
        text_path = sample_inputs_dir / "input_{}.txt".format(code)
        text_path.write_text(profile.sample_text + "\n", encoding="utf-8")
        synthesize_speech(
            profile.sample_text,
            audio_path,
            language=code,
            voice=profile.macos_voice,
        )
        print("created {} and {}".format(audio_path, text_path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
