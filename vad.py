from __future__ import annotations

import shutil
import struct
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List


@dataclass
class VADResult:
    input_path: str
    output_path: str
    backend: str
    sample_rate: int
    channels: int
    sample_width: int
    total_seconds: float
    speech_start_seconds: float
    speech_end_seconds: float
    speech_seconds: float
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def trim_silence(
    input_path: Path,
    output_path: Path,
    frame_ms: int = 30,
    threshold_ratio: float = 0.18,
    padding_ms: int = 250,
    min_speech_ms: int = 150,
) -> VADResult:
    """Energy-based VAD fallback for short demo WAV files."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with wave.open(str(input_path), "rb") as source:
            params = source.getparams()
            frames = source.readframes(params.nframes)
    except (wave.Error, FileNotFoundError):
        shutil.copyfile(input_path, output_path)
        return VADResult(
            input_path=str(input_path),
            output_path=str(output_path),
            backend="copy_fallback",
            sample_rate=0,
            channels=0,
            sample_width=0,
            total_seconds=0.0,
            speech_start_seconds=0.0,
            speech_end_seconds=0.0,
            speech_seconds=0.0,
            note="Input was not a readable PCM WAV file; copied without trimming.",
        )

    bytes_per_frame = params.sampwidth * params.nchannels
    samples_per_chunk = max(1, int(params.framerate * frame_ms / 1000))
    chunk_bytes = samples_per_chunk * bytes_per_frame
    chunks = [
        frames[index : index + chunk_bytes]
        for index in range(0, len(frames), chunk_bytes)
        if frames[index : index + chunk_bytes]
    ]

    if not chunks:
        shutil.copyfile(input_path, output_path)
        return _empty_audio_result(input_path, output_path, params, "No audio frames found.")

    rms_values: List[int] = [_rms(chunk, params.sampwidth) for chunk in chunks if chunk]
    max_rms = max(rms_values) if rms_values else 0
    if max_rms == 0:
        shutil.copyfile(input_path, output_path)
        return _empty_audio_result(input_path, output_path, params, "Silent audio; copied without trimming.")

    threshold = max(1, int(max_rms * threshold_ratio))
    speech_indices = [
        index for index, rms in enumerate(rms_values) if rms >= threshold
    ]

    min_speech_chunks = max(1, int(min_speech_ms / frame_ms))
    if len(speech_indices) < min_speech_chunks:
        shutil.copyfile(input_path, output_path)
        return _empty_audio_result(
            input_path,
            output_path,
            params,
            "Speech below minimum duration; copied without trimming.",
        )

    padding_chunks = max(0, int(padding_ms / frame_ms))
    start_chunk = max(0, speech_indices[0] - padding_chunks)
    end_chunk = min(len(chunks), speech_indices[-1] + padding_chunks + 1)

    trimmed_frames = b"".join(chunks[start_chunk:end_chunk])
    with wave.open(str(output_path), "wb") as target:
        target.setparams(params)
        target.writeframes(trimmed_frames)

    total_seconds = params.nframes / float(params.framerate)
    speech_start = start_chunk * frame_ms / 1000.0
    speech_end = min(total_seconds, end_chunk * frame_ms / 1000.0)
    return VADResult(
        input_path=str(input_path),
        output_path=str(output_path),
        backend="energy_threshold",
        sample_rate=params.framerate,
        channels=params.nchannels,
        sample_width=params.sampwidth,
        total_seconds=round(total_seconds, 3),
        speech_start_seconds=round(speech_start, 3),
        speech_end_seconds=round(speech_end, 3),
        speech_seconds=round(max(0.0, speech_end - speech_start), 3),
        note="Trimmed with simple RMS threshold; use Silero VAD for stronger production comparison.",
    )


def _empty_audio_result(input_path: Path, output_path: Path, params: wave._wave_params, note: str) -> VADResult:
    total_seconds = params.nframes / float(params.framerate) if params.framerate else 0.0
    return VADResult(
        input_path=str(input_path),
        output_path=str(output_path),
        backend="energy_threshold",
        sample_rate=params.framerate,
        channels=params.nchannels,
        sample_width=params.sampwidth,
        total_seconds=round(total_seconds, 3),
        speech_start_seconds=0.0,
        speech_end_seconds=round(total_seconds, 3),
        speech_seconds=round(total_seconds, 3),
        note=note,
    )


def _rms(chunk: bytes, sample_width: int) -> int:
    if not chunk:
        return 0

    if sample_width == 1:
        values = [sample - 128 for sample in chunk]
    elif sample_width == 2:
        sample_count = len(chunk) // 2
        values = struct.unpack("<{}h".format(sample_count), chunk[: sample_count * 2])
    elif sample_width == 4:
        sample_count = len(chunk) // 4
        values = struct.unpack("<{}i".format(sample_count), chunk[: sample_count * 4])
    else:
        return 0

    if not values:
        return 0
    mean_square = sum(value * value for value in values) / float(len(values))
    return int(mean_square ** 0.5)
