# Multilingual Voice Agent Demo

An end-to-end multilingual voice-agent prototype that turns spoken customer-support requests into spoken AI responses.

This project uses real speech and language-model stages:

```text
WAV audio -> Silero VAD -> faster-whisper ASR -> Gemini -> macOS TTS -> JSON + WAV artifacts
```

The demo is intentionally compact. It is designed to show practical voice-agent engineering skills: speech segmentation, multilingual transcription, LLM response generation, speech synthesis, latency tracking, and clear evaluation.

## What It Demonstrates

- Real audio input, not text-only chatbot input.
- Real Voice Activity Detection with Silero VAD.
- Real multilingual ASR transcription with faster-whisper.
- Real Gemini response generation through the Gemini API.
- Real output voice files generated with macOS `say` and `afconvert`.
- English, Japanese, and Chinese sample requests.
- Per-stage metadata and latency in committed JSON artifacts.

## Pipeline

```text
sample_inputs/input_*.wav
        |
        v
vad.py
  Silero VAD detects speech and writes speech_segment_*.wav
        |
        v
asr.py
  faster-whisper transcribes the detected speech segment
        |
        v
agent.py
  Gemini generates a concise same-language support reply
        |
        v
tts.py
  macOS say + afconvert generate response_*.wav
        |
        v
demo_results/result_*.json
```

## Demo Inputs

| Language | Audio file | Spoken request |
| --- | --- | --- |
| English | `sample_inputs/input_en.wav` | I want to reschedule my appointment. |
| Japanese | `sample_inputs/input_ja.wav` | 予約を変更したいです。 |
| Chinese | `sample_inputs/input_zh.wav` | 我想更改我的预约时间。 |

The `.txt` files in `sample_inputs/` document the intended sample phrases. The application does not read those files during the pipeline; ASR transcription comes from the WAV audio.

## Demo Results

Committed result artifacts live in [demo_results/](demo_results/). Each JSON file records the actual backend metadata:

- `vad.backend == "silero"`
- `asr.backend == "faster-whisper"`
- `agent.backend == "gemini"`

| Input audio | ASR transcript | Gemini response | Output audio | Total latency |
| --- | --- | --- | --- | --- |
| `sample_inputs/input_en.wav` | I want to reschedule my appointment. | I can help you with that. What is the appointment you would like to reschedule? | `demo_results/response_en.wav` | 6.0067s |
| `sample_inputs/input_ja.wav` | 予約を変更したいです | 予約の変更ですね。予約番号を教えていただけますか？ | `demo_results/response_ja.wav` | 7.7829s |
| `sample_inputs/input_zh.wav` | 我想更改我的预约时间 | 好的，请问您想将预约更改到什么时间？ | `demo_results/response_zh.wav` | 6.3455s |

Detailed outputs:

- [demo_results/result_en.json](demo_results/result_en.json)
- [demo_results/result_ja.json](demo_results/result_ja.json)
- [demo_results/result_zh.json](demo_results/result_zh.json)

## Run Locally

Requirements:

- macOS with `say` and `afconvert`
- Python 3.11
- Gemini API key

Set up the environment:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r requirements-optional.txt
```

Generate sample input audio if needed:

```bash
.venv/bin/python scripts/create_demo_audio.py
```

Run the real pipeline:

```bash
export GEMINI_API_KEY="your-api-key"
.venv/bin/python main.py sample_inputs/input_en.wav --language en --run-id en
.venv/bin/python main.py sample_inputs/input_ja.wav --language ja --run-id ja
.venv/bin/python main.py sample_inputs/input_zh.wav --language zh --run-id zh
```

The default ASR model is `small`. To reproduce the committed demo results exactly, use the same local CTranslate2 model folder:

```bash
ASR_MODEL=local_models/faster-whisper-base \
GEMINI_API_KEY="your-api-key" \
.venv/bin/python main.py sample_inputs/input_en.wav --language en --run-id en
```

`local_models/` is ignored by git because model weights should not be committed.

## Repository Structure

```text
.
├── main.py                         # Pipeline entry point
├── vad.py                          # Silero VAD speech segmentation
├── asr.py                          # faster-whisper transcription
├── agent.py                        # Gemini response generation
├── tts.py                          # macOS TTS to WAV
├── metrics.py                      # JSON output and latency logging
├── languages.py                    # Language profiles and sample phrases
├── requirements.txt
├── requirements-optional.txt
├── sample_inputs/
│   ├── input_en.wav
│   ├── input_en.txt
│   ├── input_ja.wav
│   ├── input_ja.txt
│   ├── input_zh.wav
│   └── input_zh.txt
├── demo_results/
│   ├── README.md
│   ├── speech_segment_en.wav
│   ├── speech_segment_ja.wav
│   ├── speech_segment_zh.wav
│   ├── response_en.wav
│   ├── response_ja.wav
│   ├── response_zh.wav
│   ├── result_en.json
│   ├── result_ja.json
│   ├── result_zh.json
│   └── run_log.json
├── scripts/
│   └── create_demo_audio.py
└── docs/
    ├── PROJECT_BRIEF.md
    ├── PIPELINE_DESIGN_AND_MODEL_CHOICES.md
    └── EVALUATION.md
```

## Design Choices

| Stage | Choice | Reason |
| --- | --- | --- |
| VAD | Silero VAD | Free, local, stronger than hand-written amplitude thresholding. |
| ASR | faster-whisper | Practical multilingual transcription with CPU int8 support. |
| Agent | Gemini 2.5 Flash | Good latency/cost profile for short support-agent responses. |
| TTS | macOS `say` + `afconvert` | Produces real local WAV output without requiring a paid TTS service. |
| Metrics | JSON logs | Makes backend choices, transcripts, output paths, and latency inspectable. |

## Limitations

- Sample input audio is synthetic macOS-generated speech, not real human recordings.
- The prototype is file-based, not a real-time streaming voice agent.
- macOS `say` is useful for local output files but is not production-grade neural TTS.
- Model weights and API keys are intentionally not committed.

## Next Steps

- Add real self-recorded English, Japanese, and Chinese samples.
- Compare `base`, `small`, and managed ASR APIs on the same audio set.
- Add word error rate or character error rate evaluation.
- Replace macOS TTS with a higher-quality neural TTS backend.
- Extend the Gemini stage with structured intent extraction or tool calls.

Additional design rationale is in [docs/PIPELINE_DESIGN_AND_MODEL_CHOICES.md](docs/PIPELINE_DESIGN_AND_MODEL_CHOICES.md). Evaluation notes are in [docs/EVALUATION.md](docs/EVALUATION.md).
