# Evaluation Notes

This file records what works, what fails, and what should be improved after each run.

## Current Evaluation Scope

Run the same real speech pipeline on three short customer-support inputs:

```text
audio -> Silero VAD -> faster-whisper ASR -> Gemini -> macOS TTS
```

| Input | Language | Expected intent |
| --- | --- | --- |
| `sample_inputs/input_en.wav` | English | Appointment rescheduling |
| `sample_inputs/input_ja.wav` | Japanese | Appointment rescheduling |
| `sample_inputs/input_zh.wav` | Chinese | Appointment rescheduling |

For each run, record:

- VAD backend, speech segment count, and VAD latency.
- ASR backend, model, and transcript quality.
- Agent backend and response usefulness.
- TTS backend and output audio path.
- Total latency.
- Any failure cases.

## Committed Gemini Demo Results

The committed result set lives in `demo_results/` and was generated with:

- VAD: `silero`
- ASR: `faster-whisper`
- ASR model: local CTranslate2 folder `local_models/faster-whisper-base`, equivalent to `Systran/faster-whisper-base`
- Agent: Gemini `gemini-2.5-flash`
- TTS: macOS `say` + `afconvert`

Command shape:

```bash
ASR_MODEL=local_models/faster-whisper-base GEMINI_API_KEY="$(tr -d '\r\n ' < gemini_api.txt)" .venv/bin/python main.py sample_inputs/input_en.wav --language en --output-dir demo_results --run-id en
ASR_MODEL=local_models/faster-whisper-base GEMINI_API_KEY="$(tr -d '\r\n ' < gemini_api.txt)" .venv/bin/python main.py sample_inputs/input_ja.wav --language ja --output-dir demo_results --run-id ja
ASR_MODEL=local_models/faster-whisper-base GEMINI_API_KEY="$(tr -d '\r\n ' < gemini_api.txt)" .venv/bin/python main.py sample_inputs/input_zh.wav --language zh --output-dir demo_results --run-id zh
```

Results:

| Input | ASR transcript | Gemini response | Total latency |
| --- | --- | --- | --- |
| `sample_inputs/input_en.wav` | I want to reschedule my appointment. | I can help you with that. What is the appointment you would like to reschedule? | 6.0067s |
| `sample_inputs/input_ja.wav` | 予約を変更したいです | 予約の変更ですね。予約番号を教えていただけますか？ | 7.7829s |
| `sample_inputs/input_zh.wav` | 我想更改我的预约时间 | 好的，请问您想将预约更改到什么时间？ | 6.3455s |

## Observations

- `faster-whisper-tiny` was enough for English but produced poor Japanese/Chinese transcripts on synthetic macOS voices.
- `faster-whisper-base` produced acceptable transcripts for the committed multilingual demo.
- The Japanese sample was changed from an invoice phrase to an appointment-change phrase because the original phrase produced a homophone kanji error on synthetic TTS audio.
- Silero VAD detected one speech segment for each short sample and wrote a segmented WAV file before ASR.
- macOS `say` creates usable demo audio, but the voice quality is not comparable to modern neural TTS.

## Limitations

- The input audio is synthetic macOS-generated speech. Real human recordings should be added before making accuracy claims.
- The demo is offline and file-based. It does not implement streaming endpointing, interruption handling, or turn-taking.
- ASR quality is measured qualitatively on three short samples only.
- The Gemini response is intentionally short and does not call external business systems.
- Local model folders and API keys are ignored by git.

## Next Improvements

- Add real self-recorded English, Japanese, and Chinese samples.
- Record WER or character error rate against the sample `.txt` files.
- Add a small streaming prototype with chunked VAD and endpointing.
- Compare `base`, `small`, and managed ASR APIs on the same sample set.
- Replace macOS `say` with a neural TTS backend for final presentation audio.
