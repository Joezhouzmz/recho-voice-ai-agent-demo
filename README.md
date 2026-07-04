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
- Gemini-backed response generation for the committed demo path.
- Explicit development-only mock mode for pipeline checks without API usage.
- Optional Whisper/faster-whisper ASR backend for real transcription.
- Committed Gemini-backed demo artifacts in [demo_results_gemini/](demo_results_gemini/).
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
  sidecar transcript for reproducible demo runs
  optional Whisper / faster-whisper for real ASR
        |
        v
agent.py
  Gemini Flash-family model
  explicit mock backend for development checks
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
| Agent response | `agent.py` | Gemini `gemini-2.5-flash` | Gemini model comparison / tool-enabled agent |
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

Set a Gemini API key and run all three demo examples:

```bash
export GEMINI_API_KEY="your-api-key"
python3 main.py sample_inputs/input_en.wav --language en --gemini-model gemini-2.5-flash --run-id en_gemini
python3 main.py sample_inputs/input_ja.wav --language ja --gemini-model gemini-2.5-flash --run-id ja_gemini
python3 main.py sample_inputs/input_zh.wav --language zh --gemini-model gemini-2.5-flash --run-id zh_gemini
```

Generated working outputs are written to:

```text
outputs/
  speech_segment_*.wav
  response_*.wav
  result_*.json
  run_log.json
```

`outputs/` is ignored by git. Selected Gemini-backed outputs are committed in [demo_results_gemini/](demo_results_gemini/).

## Demo Inputs

| Language | Input audio | Sidecar transcript |
| --- | --- | --- |
| English | `sample_inputs/input_en.wav` | `I want to reschedule my appointment.` |
| Japanese | `sample_inputs/input_ja.wav` | `請求書について確認したいです。` |
| Chinese | `sample_inputs/input_zh.wav` | `我想更改我的预约时间。` |

## Demo Results

The committed demo result set uses `gemini-2.5-flash` for the agent response stage.

| Input | Agent backend | Response text | Response audio | Total latency |
| --- | --- | --- | --- | --- |
| `sample_inputs/input_en.wav` | Gemini | I can help you with that. What is the appointment you would like to reschedule? | `demo_results_gemini/response_en_gemini.wav` | 6.3034s |
| `sample_inputs/input_ja.wav` | Gemini | はい、承知いたしました。請求書についてどのような情報をお探しですか？ | `demo_results_gemini/response_ja_gemini.wav` | 6.7762s |
| `sample_inputs/input_zh.wav` | Gemini | 好的，请问您想将预约更改到什么日期和时间？ | `demo_results_gemini/response_zh_gemini.wav` | 10.5106s |

Detailed JSON outputs:

- [demo_results_gemini/result_en_gemini.json](demo_results_gemini/result_en_gemini.json)
- [demo_results_gemini/result_ja_gemini.json](demo_results_gemini/result_ja_gemini.json)
- [demo_results_gemini/result_zh_gemini.json](demo_results_gemini/result_zh_gemini.json)

## Development Mock Mode

The demo path requires Gemini. For local development checks without API usage, use the explicit `mock` backend:

```bash
python3 main.py sample_inputs/input_en.wav --language en --agent-backend mock --run-id en_mock
```

The mock backend returns a static development-only response. It is not used for committed demo results.

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
├── demo_results_gemini/
│   ├── response_en_gemini.wav
│   ├── response_ja_gemini.wav
│   ├── response_zh_gemini.wav
│   ├── result_en_gemini.json
│   ├── result_ja_gemini.json
│   └── result_zh_gemini.json
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
- The default ASR path uses sidecar transcripts for repeatable demo runs.
- macOS `say` is useful for local WAV generation but is not production-grade neural TTS.
- The Gemini agent path requires an API key with available quota.
- This is a file-based prototype, not a real-time streaming voice application.

## Roadmap

- Add Silero VAD as an optional backend.
- Run faster-whisper on the sample inputs and compare transcripts against sidecar text.
- Replace macOS `say` with a higher-quality TTS backend for final presentation.
- Add a short demo video or GIF showing input audio, transcript, response, and generated voice.

## References

Design notes and model/API reasoning live in [docs/PIPELINE_DESIGN_AND_MODEL_CHOICES.md](docs/PIPELINE_DESIGN_AND_MODEL_CHOICES.md). Evaluation notes live in [docs/EVALUATION.md](docs/EVALUATION.md).
