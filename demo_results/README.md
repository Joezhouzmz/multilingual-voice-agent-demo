# Demo Results

This folder contains selected committed outputs from the local smoke-test run.

The generated working directory `outputs/` is ignored by git, but these files are intentionally committed so reviewers can inspect the prototype result without running the pipeline first.

## Included Files

| Language | Result JSON | Response audio |
| --- | --- | --- |
| English | `result_en.json` | `response_en.wav` |
| Japanese | `result_ja.json` | `response_ja.wav` |
| Chinese | `result_zh.json` | `response_zh.wav` |

## Run Mode

These files were generated with:

- sidecar `.txt` transcripts as the ASR input source
- local deterministic agent responses
- macOS `say` for TTS
- RMS energy-threshold VAD

This is the version 1 local smoke-test mode. Real ASR and Gemini-backed agent runs are supported by the code but are not represented in this folder yet.
