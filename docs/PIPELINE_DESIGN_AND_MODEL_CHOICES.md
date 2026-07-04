# Pipeline Design and Model Choices

This document explains the planned design for the Multilingual Voice Agent Demo: what files the project should contain, how the pipeline works, why each part exists, and which free or limited-free model/API choices make sense for a demo and for a later production plan.

## 1. Target Scope

This should stay a small but serious prototype:

- 1-3 days of implementation.
- About 10-12 files total.
- About 5 core Python modules.
- No custom ASR, VAD, LLM, or TTS model training.
- English, Japanese, and Chinese examples.
- Clear latency and failure-case notes.

The point is to show that I understand the full speech-agent workflow and can make practical engineering decisions quickly.

## 2. Planned File Count and Structure

```text
multilingual-voice-agent-demo/
  README.md
  requirements.txt
  main.py

  vad.py
  asr.py
  agent.py
  tts.py
  metrics.py
  languages.py

  sample_inputs/
    input_en.wav
    input_ja.wav
    input_zh.wav
    input_en.txt
    input_ja.txt
    input_zh.txt

  outputs/
    response_en.wav
    response_ja.wav
    response_zh.wav
    run_log.json

  docs/
    PROJECT_BRIEF.md
    PIPELINE_DESIGN_AND_MODEL_CHOICES.md
    EVALUATION.md

  scripts/
    create_demo_audio.py
```

Expected core file count:

| File | Purpose | Why it exists |
| --- | --- | --- |
| `main.py` | Runs the full pipeline | Makes the demo easy to execute from one command |
| `vad.py` | Speech detection / segmentation | Shows speech-processing awareness before ASR |
| `asr.py` | Speech-to-text | Converts spoken user input into text |
| `agent.py` | Response generation | Connects speech AI with LLM/agent work |
| `tts.py` | Text-to-speech | Completes the speech-to-speech loop |
| `metrics.py` | Latency/result logging | Gives concrete evaluation data |
| `languages.py` | Language profiles | Keeps English, Japanese, and Chinese voice/text behavior consistent |
| `README.md` | Public repo explanation | Makes the project understandable to recruiters/interviewers |
| `docs/EVALUATION.md` | Results and limitations | Shows research maturity and honesty |
| `scripts/create_demo_audio.py` | Sample generation | Creates real local WAV inputs for repeatable demos |

## 3. Pipeline Design

The pipeline is:

```text
Audio input
-> VAD / speech segmentation
-> ASR transcription
-> LLM agent response
-> TTS synthesis
-> output audio + run log
```

### Example Inputs

English:

```text
I want to reschedule my appointment.
```

Japanese:

```text
請求書について確認したいです。
```

Chinese:

```text
我想更改我的预约时间。
```

### Example Outputs

For each input file, the pipeline should produce:

- Clean speech segment: `outputs/speech_segment_en.wav`
- Transcript: `I want to reschedule my appointment.`
- Agent response text: `Sure. What date and time would you prefer?`
- Response audio: `outputs/response_en.wav`
- Result log: `outputs/run_log.json`

## 4. What Is VAD and Why We Need It

VAD means Voice Activity Detection.

Its job is to decide which parts of an audio stream contain speech and which parts are silence, background noise, or non-speech sound.

For this project, VAD is useful because the input audio may contain:

- silence before or after the speaker talks
- long pauses
- background noise
- multiple speech chunks

Without VAD, ASR receives the whole raw audio file. That can increase latency and can make transcription worse, especially when the file has silence or noise.

With VAD, the pipeline becomes more realistic:

```text
raw audio
-> detect speech sections
-> pass only speech to ASR
```

Why this matters for our goal:

- Voice-agent systems need natural conversational behavior, not just clean offline transcription.
- Real voice agents must know when a user starts and stops speaking.
- VAD is a practical first step toward real-time interaction.
- VAD lets us talk about latency and segmentation quality in the README and interview.

### VAD Choice

Recommended for the demo: **Silero VAD**.

Why:

- It is free/open-source and published under MIT license.
- It is lightweight and fast enough for local demo use.
- It is designed for speech detection, voice bots, voice interfaces, call-center style automation, and edge/mobile use cases.
- It is more modern than basic energy-threshold VAD.

Official reference: [Silero VAD GitHub](https://github.com/snakers4/silero-vad)

Production plan idea:

- Start with Silero VAD as the baseline.
- Measure false starts, missed speech, and pause-handling on English/Japanese/Chinese examples.
- If production requires streaming, tune chunk size, silence thresholds, and endpointing rules.
- If cloud/vendor ASR provides built-in endpointing, compare it against Silero and keep the simpler option only if quality is acceptable.

## 5. ASR: Free or Limited-Free Choices

ASR means Automatic Speech Recognition. It converts speech audio into text.

For this prototype, ASR must support English, Japanese, and Chinese.

### Recommended Demo Choice: Whisper / faster-whisper

Use Whisper or faster-whisper locally first.

Why:

- OpenAI Whisper is an open-source multilingual speech recognition model.
- It supports multilingual speech recognition, translation, and language identification.
- It avoids cloud quota problems during development.
- It is good enough for a demo with short English/Japanese/Chinese audio.
- It gives us a strong baseline before comparing cloud APIs.

Official reference: [OpenAI Whisper GitHub](https://github.com/openai/whisper)

Production plan idea:

- Use Whisper/faster-whisper as the local baseline.
- If production needs privacy or offline processing, self-host a faster-whisper service.
- If production needs lower operational burden, compare against managed ASR APIs.
- Track word error rate, language detection quality, latency, and cost per audio minute.

### Option: Google Cloud Speech-to-Text

Google Cloud Speech-to-Text has a limited free monthly allowance for Speech-to-Text V1 in the official pricing table.

Official reference: [Google Cloud Speech-to-Text pricing](https://cloud.google.com/speech-to-text/pricing)

Why use it for demo:

- Useful if we want a managed ASR comparison against Whisper.
- Good fit if we already use Google Cloud or Gemini in the agent layer.

Production plan idea:

- Good managed-cloud candidate for scalable transcription.
- Evaluate English/Japanese/Chinese accuracy and latency.
- Watch pricing, request rounding, data logging settings, and region/compliance requirements.

### Option: Azure Speech

Azure Speech has a Free F0 tier listed for speech-to-text and text-to-speech.

Official reference: [Azure Speech pricing](https://azure.microsoft.com/en-us/pricing/details/speech/)

Why use it for demo:

- One vendor can cover both ASR and TTS.
- The free tier is enough for a small application demo.

Production plan idea:

- Strong candidate for enterprise customer-support use cases.
- Evaluate language support, diarization/translation needs, deployment region, and compliance requirements.
- Useful if the future product needs both managed ASR and managed neural TTS under one vendor.

## 6. Agent: Is Gemini Flash Fine?

Yes. Gemini Flash is fine for the agent part.

For this prototype, the agent does not need deep reasoning. It needs to:

- read the ASR transcript
- identify the user intent
- respond in the same language
- keep the reply short and customer-support-like
- avoid hallucinating unavailable business facts

Gemini Flash-family models are appropriate because the agent step is latency-sensitive and usually short-context. Google's current pricing page also positions Flash/Lite family models as cost-efficient options for agentic tasks and simple data processing.

Official references:

- [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)

Recommended demo approach:

- Use Gemini Flash-family models as the real agent backend.
- Keep only an explicit development `mock` backend for VAD/TTS/logging checks without API usage.
- Force concise responses with a simple system instruction.
- Ask the model to respond in `en`, `ja`, or `zh` based on detected language.

Example agent instruction:

```text
You are a concise enterprise customer-support voice assistant.
Reply in the same language as the user.
Keep the answer under two sentences.
Do not invent account-specific facts.
If information is missing, ask one clear follow-up question.
```

Production plan idea:

- Gemini Flash is a good first production candidate for low-latency support-agent replies.
- Add strict prompts, output length limits, safety checks, and logging.
- Add tool/function calling only after the base voice loop works.
- Evaluate against alternatives for latency, cost, response consistency, and Japanese/Chinese quality.
- If customer data is involved, review data retention, privacy, and enterprise terms before production use.

## 7. TTS: Free or Limited-Free Choices

TTS means Text-to-Speech. It converts the agent's response text into spoken audio.

For this prototype, TTS should support English, Japanese, and Chinese.

### Recommended Demo Choice: macOS `say` or Piper First

For fastest implementation, start with macOS `say` if voice quality is acceptable.

Why:

- Already available on macOS.
- No API key or billing setup.
- Good enough to prove the pipeline shape.
- Very fast to implement.

Downside:

- Voice quality and language support may be less impressive than modern neural TTS.
- Not a production plan.

For a stronger local open-source TTS path, use Piper.

Official reference: [Piper GitHub](https://github.com/rhasspy/piper)

Why:

- Local neural TTS.
- No cloud quota.
- Useful for privacy/offline demos.

Production plan idea:

- Use local TTS only if privacy/offline operation is important.
- Check voice availability and licensing for English, Japanese, and Chinese voices before public release.
- For production quality, compare against cloud neural TTS.

### Option: Google Cloud Text-to-Speech

Google Cloud Text-to-Speech has free monthly character allowances for several voice families, while newer Gemini-TTS rows may not have a free usage limit.

Official reference: [Google Cloud Text-to-Speech pricing](https://cloud.google.com/text-to-speech/pricing)

Why use it for demo:

- Better voice quality than basic local system TTS.
- Good if we are already using Google Cloud or Gemini.
- Supports many languages and voices.

Production plan idea:

- Good managed TTS candidate if voice quality matters.
- Evaluate Japanese and Chinese voice naturalness.
- Track per-character cost and caching opportunities.
- Cache repeated support responses to reduce cost and latency.

### Option: Azure Speech TTS

Azure Speech Free F0 includes a monthly neural TTS character allowance in the official pricing page.

Official reference: [Azure Speech pricing](https://azure.microsoft.com/en-us/pricing/details/speech/)

Why use it for demo:

- Same vendor can handle both ASR and TTS.
- Neural TTS quality is usually strong enough for a polished demo.

Production plan idea:

- Strong candidate for enterprise voice agents.
- Useful when ASR, TTS, translation, and enterprise controls should live in one cloud stack.
- Evaluate quota, latency, voice availability, and compliance.

### Option: Amazon Polly

Amazon Polly has a published free tier for several voice categories, with limits depending on voice type and account age.

Official reference: [Amazon Polly pricing](https://aws.amazon.com/polly/pricing/)

Why use it for demo:

- Mature managed TTS service.
- Good free-tier capacity for short demo scripts.
- Many production deployment teams already know AWS.

Production plan idea:

- Good if the production stack is on AWS.
- Compare Standard, Neural, Long-Form, and Generative voices for cost and quality.
- Cache stable responses and monitor character usage.

## 8. Language Design: English, Japanese, Chinese

The prototype should include all three languages:

- English: shows international customer-support workflow.
- Japanese: relevant to multilingual enterprise support and Japan-market voice workflows.
- Chinese: shows multilingual ability and personal language advantage.

The agent should respond in the same language as the transcript by default.

Expected behavior:

| Input language | ASR transcript | Agent response language | TTS voice |
| --- | --- | --- | --- |
| English | English text | English | English voice |
| Japanese | Japanese text | Japanese | Japanese voice |
| Chinese | Chinese text | Chinese | Chinese voice |

Optional later behavior:

- English input -> Japanese output for bilingual support.
- Japanese input -> English summary for operator handoff.
- Chinese input -> Japanese or English translation for support teams.

## 9. Why This Design Is Specific to Our Goal

This project is a speech AI portfolio demo, not a generic chatbot project.

That is why the design includes:

- VAD: shows speech-processing awareness.
- ASR: maps to speech recognition.
- Agent: maps to LLM/generative AI and enterprise workflow.
- TTS: maps to speech synthesis.
- Metrics: shows engineering evaluation and research thinking.
- English/Japanese/Chinese: makes the demo relevant to multilingual enterprise use cases.

The strongest signal is:

```text
I can assemble, evaluate, and explain an end-to-end voice AI agent pipeline.
```

The weaker signal would be:

```text
I tried to train a model from scratch but did not finish a working demo.
```

So the design choice is deliberate: use existing models, own the pipeline, measure the system, and explain tradeoffs clearly.

## 10. Recommended Version 1 Stack

Fastest good version:

| Stage | Version 1 choice | Reason |
| --- | --- | --- |
| VAD | Silero VAD | Free, fast, strong local baseline |
| ASR | Whisper / faster-whisper | Multilingual and local |
| Agent | Gemini Flash-family model | Low-latency, free/limited-free API path, good enough for short replies |
| TTS | macOS `say` first, then Google/Azure/Polly or Piper | Fastest path first, better voice quality later |
| Metrics | Local JSON timing log | Simple, interview-useful evidence |

Production comparison candidates:

| Stage | Candidate | Why compare |
| --- | --- | --- |
| ASR | Whisper self-hosted | Privacy/offline/control |
| ASR | Google Cloud Speech-to-Text | Managed cloud scaling |
| ASR | Azure Speech | Enterprise ASR/TTS bundle |
| Agent | Gemini Flash | Low latency and cost |
| TTS | Google Cloud TTS | Voice quality and Google stack fit |
| TTS | Azure Speech TTS | Enterprise voice stack |
| TTS | Amazon Polly | AWS stack fit and mature managed TTS |
| TTS | Piper | Local/offline/privacy path |

## 11. Version 1 Definition of Done

Version 1 is done when:

- `python main.py sample_inputs/input_en.wav` runs end to end.
- English, Japanese, and Chinese examples are documented.
- At least one response audio file is generated.
- `outputs/run_log.json` records transcript, response, latency, and output path.
- `docs/EVALUATION.md` lists what worked, what failed, and what should improve next.
- The README explains the system without exaggerating it.
