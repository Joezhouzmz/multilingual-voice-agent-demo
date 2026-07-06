# Demo Results

These artifacts were generated from real audio pipeline runs:

```text
sample WAV -> Silero VAD -> faster-whisper ASR -> Gemini 2.5 Flash -> macOS TTS
```

Each `result_*.json` records the exact VAD, ASR, agent, and TTS backend metadata. The committed runs use `faster-whisper` with a local `faster-whisper-base` CTranslate2 model folder, which is ignored by git.

The `response_*.wav` files are the spoken Gemini responses. The `speech_segment_*.wav` files are the audio segments emitted by Silero VAD and passed into ASR.
