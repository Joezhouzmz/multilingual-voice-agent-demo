# Project Brief: Multilingual Voice Agent Demo

## 1. Background

This project is a compact portfolio demo for speech AI and voice-agent engineering. It focuses on the core pieces behind conversational voice systems:

- Speech detection and endpointing
- Speech recognition
- LLM-based response generation
- Text-to-speech synthesis
- Latency and failure-case evaluation

The goal is to show practical system understanding without spending weeks on custom model training or a large application shell.

## 2. Task

Create a small speech-to-speech assistant that accepts a spoken customer-support request and returns a spoken answer.

The core task is:

```text
audio input -> transcript -> response text -> response audio
```

The prototype should be multilingual and language-aware, with English, Japanese, and Chinese examples.

## 3. Action Plan

Build the smallest useful version first.

### Step 1: Project Skeleton

Create a simple Python repo with clear module boundaries:

```text
multilingual-voice-agent-demo/
  README.md
  requirements.txt
  main.py
  vad.py
  asr.py
  agent.py
  tts.py
  sample_inputs/
  outputs/
  docs/
```

### Step 2: Audio Input

Use short manually recorded audio files:

- English customer-support request
- Japanese customer-support request
- Chinese customer-support request

### Step 3: Speech Pipeline

Run:

```text
VAD -> ASR -> Agent -> TTS
```

Use existing libraries or APIs. Do not train custom models.

### Step 4: Evaluation Notes

Document:

- Transcript quality
- Total latency
- ASR errors
- TTS quality
- What failed
- What would be improved in a production version

## 4. Goal / Expected Result

The goal is not to build a full product. The goal is to create targeted proof that I understand the speech AI technical domain.

Expected final output:

- Runnable local demo
- Sample input audio files
- Generated response audio files
- README result table
- Honest limitations and next steps

Example result table:

| Input | Language | ASR Transcript | Agent Response | Output | Total Latency |
| --- | --- | --- | --- | --- | --- |
| `sample_inputs/input_en.wav` | English | I want to reschedule my appointment. | Sure. What date and time would you prefer? | `outputs/response_en.wav` | 3.3s |
| `sample_inputs/input_ja.wav` | Japanese | 請求書について確認したいです。 | 請求書についてですね。確認したい内容を教えてください。 | `outputs/response_ja.wav` | 3.8s |
| `sample_inputs/input_zh.wav` | Chinese | 我想更改我的预约时间。 | 当然可以。您想改到哪一天和几点？ | `outputs/response_zh.wav` | 3.6s |

## 5. Scope Control

Do not build these in version 1:

- Custom ASR training
- Custom TTS training
- Full real-time streaming
- Web app
- Login/accounts
- Cloud deployment
- Large benchmark suite

Version 1 should be small enough to finish in 1-3 days and strong enough to discuss in an interview.

## 6. Interview Story

This project should support the following explanation:

```text
I built a minimal speech-to-speech AI agent to understand the practical engineering challenges behind conversational speech AI. The system performs voice activity detection, ASR transcription, response generation, and TTS synthesis. I evaluated latency, segmentation quality, transcription errors, and response usefulness, then documented what I would improve for a production enterprise voice agent.
```
