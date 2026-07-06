# Multilingual Voice Agent Demo

A compact speech-to-speech AI agent prototype for multilingual customer-support workflows.

The committed demo path is real audio processing end to end:

```text
audio -> Silero VAD -> faster-whisper ASR transcription -> Gemini -> macOS TTS -> JSON + WAV artifacts
```

The goal is not to train custom models or build a full application shell. The goal is to demonstrate practical voice-agent engineering: segmentation, transcription, response generation, speech synthesis, latency logging, and honest limitations across English, Japanese, and Chinese.

## Highlights

- Real Voice Activity Detection with Silero VAD.
- Real ASR transcription with faster-whisper.
- Gemini-backed response generation through the Gemini REST API.
- Real response audio generation with macOS `say` and `afconvert`.
- English, Japanese, and Chinese sample audio inputs.
- JSON artifacts that record backend, model, transcript, response text, output audio path, and per-stage latency.

## Architecture

```text
sample_inputs/input_*.wav
        |
        v
vad.py
  Silero VAD segments speech into speech_segment_*.wav
        |
        v
asr.py
  faster-whisper transcribes the speech segment
        |
        v
agent.py
  Gemini generates a short same-language support response
        |
        v
tts.py
  macOS say + afconvert produce response_*.wav
        |
        v
demo_results/result_*.json
demo_results/response_*.wav
```

## Pipeline Components

| Stage | File | Demo backend | Why this choice |
| --- | --- | --- | --- |
| Voice activity detection | `vad.py` | Silero VAD | Free, local, stronger than RMS thresholding, and appropriate for voice-agent endpointing demos. |
| Speech-to-text | `asr.py` | faster-whisper | Practical local multilingual ASR with CPU int8 support. |
| Agent response | `agent.py` | Gemini `gemini-2.5-flash` | Low-latency response generation for short customer-support turns. |
| Text-to-speech | `tts.py` | macOS `say` + `afconvert` | Produces a real voice file without adding a paid TTS dependency. |
| Metrics | `metrics.py` | JSON timing logs | Makes latency and backend choices inspectable. |

## Quick Start

Requirements:

- macOS with `say` and `afconvert`
- Python 3.11
- Gemini API key for the real agent path

Set up the local environment:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r requirements-optional.txt
```

Generate or refresh the sample input audio files:

```bash
.venv/bin/python scripts/create_demo_audio.py
```

Run the real demo path:

```bash
export GEMINI_API_KEY="your-api-key"
.venv/bin/python main.py sample_inputs/input_en.wav --language en --run-id en
.venv/bin/python main.py sample_inputs/input_ja.wav --language ja --run-id ja
.venv/bin/python main.py sample_inputs/input_zh.wav --language zh --run-id zh
```

The CLI always runs the real pipeline: Silero VAD, faster-whisper ASR, Gemini, and macOS TTS. The default ASR model is `small`. To reproduce the committed artifact set exactly, set `ASR_MODEL=local_models/faster-whisper-base` after downloading that ignored local model folder.

## Demo Inputs

| Language | Input audio | Sample request |
| --- | --- | --- |
| English | `sample_inputs/input_en.wav` | I want to reschedule my appointment. |
| Japanese | `sample_inputs/input_ja.wav` | 予約を変更したいです。 |
| Chinese | `sample_inputs/input_zh.wav` | 我想更改我的预约时间。 |

The `.txt` files in `sample_inputs/` document the intended sample phrases. `main.py` does not read them.

## Demo Results

Committed artifacts are in [demo_results/](demo_results/). Each JSON file proves the real backends used:

- `vad.backend == "silero"`
- `asr.backend == "faster-whisper"`
- `agent.backend == "gemini"`

| Input | ASR transcript | Gemini response | Response audio | Total latency |
| --- | --- | --- | --- | --- |
| `sample_inputs/input_en.wav` | I want to reschedule my appointment. | I can help you with that. What is the appointment you would like to reschedule? | `demo_results/response_en.wav` | 6.0067s |
| `sample_inputs/input_ja.wav` | 予約を変更したいです | 予約の変更ですね。予約番号を教えていただけますか？ | `demo_results/response_ja.wav` | 7.7829s |
| `sample_inputs/input_zh.wav` | 我想更改我的预约时间 | 好的，请问您想将预约更改到什么时间？ | `demo_results/response_zh.wav` | 6.3455s |

Detailed JSON outputs:

- [demo_results/result_en.json](demo_results/result_en.json)
- [demo_results/result_ja.json](demo_results/result_ja.json)
- [demo_results/result_zh.json](demo_results/result_zh.json)

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

## Limitations

- The sample input audio is synthetic macOS-generated speech, not real human recordings.
- The pipeline is file-based, not real-time streaming.
- macOS `say` is useful for a local demo but is not production-grade neural TTS.
- Model weights are not committed. They download on first use or can be stored locally under ignored `local_models/`.
- On some macOS environments, Torch/Silero and CTranslate2 can load duplicate OpenMP runtimes; the faster-whisper backend sets a scoped compatibility environment variable for this local demo.

## Production Direction

- Replace macOS `say` with managed neural TTS or a local neural TTS model.
- Evaluate ASR with real recorded English/Japanese/Chinese audio, not only synthetic samples.
- Add streaming endpointing and barge-in handling.
- Add structured intent extraction and tool calls after Gemini response generation.
- Track WER, endpointing accuracy, and latency across more samples.

More design rationale is in [docs/PIPELINE_DESIGN_AND_MODEL_CHOICES.md](docs/PIPELINE_DESIGN_AND_MODEL_CHOICES.md). Evaluation notes are in [docs/EVALUATION.md](docs/EVALUATION.md).
