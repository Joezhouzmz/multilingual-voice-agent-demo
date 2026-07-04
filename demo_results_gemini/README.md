# Gemini Demo Results

This folder contains selected outputs from the Gemini-backed agent run.

The run still uses sidecar `.txt` transcripts for the ASR input source and macOS `say` for TTS. The agent response stage uses Gemini through the REST fallback in `agent.py`.

## Included Files

| Language | Result JSON | Response audio |
| --- | --- | --- |
| English | `result_en_gemini.json` | `response_en_gemini.wav` |
| Japanese | `result_ja_gemini.json` | `response_ja_gemini.wav` |
| Chinese | `result_zh_gemini.json` | `response_zh_gemini.wav` |

## Run Mode

These files were generated with:

- sidecar `.txt` transcripts as the ASR input source
- Gemini `gemini-2.5-flash` for agent response generation
- macOS `say` for TTS
- RMS energy-threshold VAD
