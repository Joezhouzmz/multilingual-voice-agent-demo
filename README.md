# Multilingual Voice Agent Demo

A compact speech-to-speech AI agent prototype for multilingual customer-support workflows.

This project demonstrates a full local voice-agent loop:

```text
audio input -> VAD -> ASR -> agent response -> TTS -> response audio + run log
```

It is intentionally small: the goal is to show practical understanding of speech AI systems, not to train custom models or build a production service.

## Highlights

- End-to-end voice pipeline with modular Python stages.
- English, Japanese, and Chinese sample inputs.
- Local smoke-test mode that runs on macOS without API keys.
- Optional Gemini agent backend when `GEMINI_API_KEY` is available.
- Optional Whisper/faster-whisper ASR backend for real transcription.
- Committed demo artifacts in [demo_results/](demo_results/).
- Per-stage latency and result logging in JSON.

## Architecture

```text
sample_inputs/input_*.wav
        |
        v
vad.py
  trims silence / non-speech regions
        |
        v
asr.py
  sidecar transcript for smoke tests
  optional Whisper / faster-whisper for real ASR
        |
        v
agent.py
  deterministic local support responses
  optional Gemini Flash-family model
        |
        v
tts.py
  macOS say + afconvert -> WAV response
        |
        v
outputs/result_*.json
outputs/response_*.wav
```

## Pipeline Components

| Stage | File | Current backend | Production comparison path |
| --- | --- | --- | --- |
| Voice activity detection | `vad.py` | RMS energy threshold | Silero VAD / endpointing from managed ASR |
| Speech-to-text | `asr.py` | sidecar `.txt` transcript for smoke tests | faster-whisper, Whisper, managed ASR APIs |
| Agent response | `agent.py` | local deterministic rules | Gemini Flash-family model |
| Text-to-speech | `tts.py` | macOS `say` + `afconvert` | Google TTS, Azure Speech, Polly, Piper |
| Metrics | `metrics.py` | JSON timing logs | benchmark table / latency dashboard |

## Quick Start

Requirements for the default local demo:

- macOS
- Python 3.8+
- built-in `say` and `afconvert` commands

Generate the sample input audio files:

```bash
python3 scripts/create_demo_audio.py
```

Run all three local examples:

```bash
python3 main.py sample_inputs/input_en.wav --language en --agent-backend local --run-id en
python3 main.py sample_inputs/input_ja.wav --language ja --agent-backend local --run-id ja
python3 main.py sample_inputs/input_zh.wav --language zh --agent-backend local --run-id zh
```

Generated working outputs are written to:

```text
outputs/
  speech_segment_*.wav
  response_*.wav
  result_*.json
  run_log.json
```

`outputs/` is ignored by git. Selected reviewable outputs are committed in [demo_results/](demo_results/).

## Demo Inputs

| Language | Input audio | Sidecar transcript |
| --- | --- | --- |
| English | `sample_inputs/input_en.wav` | `I want to reschedule my appointment.` |
| Japanese | `sample_inputs/input_ja.wav` | `請求書について確認したいです。` |
| Chinese | `sample_inputs/input_zh.wav` | `我想更改我的预约时间。` |

## Demo Results

Local smoke-test mode has been run successfully on the three committed inputs.

| Input | Transcript source | Agent backend | Response audio | Total latency |
| --- | --- | --- | --- | --- |
| `sample_inputs/input_en.wav` | sidecar `.txt` | local rules | `demo_results/response_en.wav` | 2.1370s |
| `sample_inputs/input_ja.wav` | sidecar `.txt` | local rules | `demo_results/response_ja.wav` | 2.4811s |
| `sample_inputs/input_zh.wav` | sidecar `.txt` | local rules | `demo_results/response_zh.wav` | 2.5936s |

Detailed JSON outputs:

- [demo_results/result_en.json](demo_results/result_en.json)
- [demo_results/result_ja.json](demo_results/result_ja.json)
- [demo_results/result_zh.json](demo_results/result_zh.json)

## Optional Gemini Agent

The local agent fallback is deterministic so the repository can run without credentials. To use Gemini for response generation:

```bash
export GEMINI_API_KEY="your-api-key"
python3 main.py sample_inputs/input_en.wav --language en --agent-backend gemini --run-id en_gemini
```

API keys should stay local. `.env`, `.env.*`, `gemini_api.txt`, and common Gemini key text-file patterns are ignored by git.

## Optional Real ASR

The default demo uses sidecar transcripts so the rest of the pipeline can be validated before installing speech models.

To run real ASR with faster-whisper:

```bash
python3 -m pip install -r requirements-optional.txt
python3 main.py sample_inputs/input_en.wav --language en --asr-backend faster-whisper --run-id en_asr
```

If no ASR backend is installed and no sidecar transcript is available, the pipeline exits with an explicit ASR setup message.

## Repository Layout

```text
.
├── main.py
├── vad.py
├── asr.py
├── agent.py
├── tts.py
├── metrics.py
├── languages.py
├── sample_inputs/
│   ├── input_en.wav
│   ├── input_en.txt
│   ├── input_ja.wav
│   ├── input_ja.txt
│   ├── input_zh.wav
│   └── input_zh.txt
├── demo_results/
│   ├── response_en.wav
│   ├── response_ja.wav
│   ├── response_zh.wav
│   ├── result_en.json
│   ├── result_ja.json
│   └── result_zh.json
├── scripts/
│   └── create_demo_audio.py
└── docs/
    ├── PROJECT_BRIEF.md
    ├── PIPELINE_DESIGN_AND_MODEL_CHOICES.md
    └── EVALUATION.md
```

## Why This Project Exists

This prototype was built as a targeted speech-AI portfolio project. It focuses on the pieces that matter in a voice-agent system:

- VAD and endpointing awareness
- multilingual ASR path
- low-latency agent response generation
- TTS output as an actual audio file
- measurable latency and reproducible examples
- clear limitations instead of exaggerated claims

## Limitations

- VAD is currently a simple energy-threshold implementation, not Silero VAD.
- The default ASR path uses sidecar transcripts for repeatable local smoke tests.
- macOS `say` is useful for local WAV generation but is not production-grade neural TTS.
- The local agent is intentionally shallow; Gemini is wired but requires a key.
- This is a file-based prototype, not a real-time streaming voice application.

## Roadmap

- Add Silero VAD as an optional backend.
- Run faster-whisper on the sample inputs and compare transcripts against sidecar text.
- Add a Gemini-backed demo result set.
- Replace macOS `say` with a higher-quality TTS backend for final presentation.
- Add a short demo video or GIF showing input audio, transcript, response, and generated voice.

## References

Design notes and model/API reasoning live in [docs/PIPELINE_DESIGN_AND_MODEL_CHOICES.md](docs/PIPELINE_DESIGN_AND_MODEL_CHOICES.md). Evaluation notes live in [docs/EVALUATION.md](docs/EVALUATION.md).
