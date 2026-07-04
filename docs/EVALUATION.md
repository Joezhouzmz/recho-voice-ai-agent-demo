# Evaluation Notes

This file records what works, what fails, and what should be improved after each run.

## Version 1 Evaluation Plan

Run the same pipeline on three short customer-support inputs:

| Input | Language | Expected intent |
| --- | --- | --- |
| `sample_inputs/input_en.wav` | English | Appointment rescheduling |
| `sample_inputs/input_ja.wav` | Japanese | Invoice question |
| `sample_inputs/input_zh.wav` | Chinese | Appointment rescheduling |

For each run, record:

- VAD latency and whether speech was trimmed correctly.
- ASR backend and transcript quality.
- Agent backend and response usefulness.
- TTS backend and output audio path.
- Total latency.
- Any failure cases.

## Current Version 1 Behavior

The implementation supports two response-generation modes:

1. **Demo mode**: uses sidecar `.txt` transcripts next to the audio files, Gemini for agent responses, and macOS `say` for TTS.
2. **Development mock mode**: uses a static mock response to check VAD/TTS/logging without API usage.

The sidecar transcript mode is intentional. It lets the full VAD -> ASR interface -> Gemini agent -> TTS -> metrics loop run on a clean machine before optional ASR dependencies are installed.

## Gemini Demo Results

Gemini-backed agent execution is wired in `agent.py` through the optional `google-genai` client and a standard-library REST fallback. The committed Gemini demo results use `gemini-2.5-flash`.

Command set:

```bash
export GEMINI_API_KEY="your-api-key"
python3 main.py sample_inputs/input_en.wav --language en --agent-backend gemini --gemini-model gemini-2.5-flash --run-id en_gemini
python3 main.py sample_inputs/input_ja.wav --language ja --agent-backend gemini --gemini-model gemini-2.5-flash --run-id ja_gemini
python3 main.py sample_inputs/input_zh.wav --language zh --agent-backend gemini --gemini-model gemini-2.5-flash --run-id zh_gemini
```

Results:

| Input | Response | Total latency |
| --- | --- | --- |
| `sample_inputs/input_en.wav` | I can help you with that. What is the appointment you would like to reschedule? | 6.3034s |
| `sample_inputs/input_ja.wav` | はい、承知いたしました。請求書についてどのような情報をお探しですか？ | 6.7762s |
| `sample_inputs/input_zh.wav` | 好的，请问您想将预约更改到什么日期和时间？ | 10.5106s |

Committed artifacts are available in `demo_results_gemini/`.

## Development Mock Check

Command set:

```bash
python3 scripts/create_demo_audio.py
python3 main.py sample_inputs/input_en.wav --language en --agent-backend mock --run-id en_mock
```

Expected stage behavior:

- VAD runs on the WAV file and writes a trimmed speech segment.
- ASR interface ran in manual mode using sidecar `.txt` transcripts.
- The mock agent returns a static development-only response.
- macOS `say` produces a real WAV response audio file.
- The run log is written to `outputs/run_log.json`.

## Limitations

- The built-in VAD is a simple RMS energy threshold, not Silero VAD.
- The mock agent is development-only and is not a real response generator.
- macOS `say` is useful for demo audio generation but is not production-grade neural TTS.
- Real ASR quality is not measured until Whisper/faster-whisper is installed and run.

## Next Improvements

- Add Silero VAD as an optional stronger VAD backend.
- Run faster-whisper on the three sample audios and compare transcripts against sidecar text.
- Add a small result table copied from `outputs/run_log.json`.
