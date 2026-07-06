from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from agent import generate_response
from asr import ASRUnavailable, transcribe_audio
from languages import SUPPORTED_LANGUAGES, normalize_language
from metrics import append_run_log, timed_stage, write_json
from tts import synthesize_speech
from vad import segment_speech


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the multilingual voice agent demo pipeline."
    )
    parser.add_argument("input_audio", type=Path, help="Path to input .wav audio.")
    parser.add_argument(
        "--language",
        default="auto",
        choices=("auto",) + SUPPORTED_LANGUAGES,
        help="Expected language. Use auto to infer from ASR.",
    )
    parser.add_argument(
        "--gemini-model",
        default=None,
        help="Gemini model name. Defaults to GEMINI_MODEL or gemini-2.5-flash.",
    )
    parser.add_argument(
        "--output-dir",
        default=Path("outputs"),
        type=Path,
        help="Directory for speech segment, response audio, and JSON logs.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Output name suffix. Defaults to the input filename stem.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_audio = args.input_audio
    output_dir = args.output_dir
    run_id = args.run_id or input_audio.stem
    language = normalize_language(args.language)
    asr_model = os.getenv("ASR_MODEL", "small")

    speech_segment_path = output_dir / "speech_segment_{}.wav".format(run_id)
    response_audio_path = output_dir / "response_{}.wav".format(run_id)
    result_path = output_dir / "result_{}.json".format(run_id)
    run_log_path = output_dir / "run_log.json"

    timings = {}
    start = time.perf_counter()

    try:
        with timed_stage("vad", timings):
            vad_result = segment_speech(input_audio, speech_segment_path)

        with timed_stage("asr", timings):
            asr_result = transcribe_audio(
                speech_segment_path,
                language=language,
                model=asr_model,
            )

        with timed_stage("agent", timings):
            agent_result = generate_response(
                asr_result.transcript,
                language=asr_result.language,
                model=args.gemini_model,
            )

        with timed_stage("tts", timings):
            tts_result = synthesize_speech(
                agent_result.response_text,
                response_audio_path,
                language=agent_result.language,
            )
    except ASRUnavailable as exc:
        print("ASR unavailable: {}".format(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        print("Pipeline failed: {}".format(exc), file=sys.stderr)
        return 1

    timings["total_seconds"] = round(time.perf_counter() - start, 4)
    record = {
        "input_audio": str(input_audio),
        "run_id": run_id,
        "language": agent_result.language,
        "transcript": asr_result.transcript,
        "response_text": agent_result.response_text,
        "speech_segment_path": str(speech_segment_path),
        "response_audio_path": str(response_audio_path),
        "timings": timings,
        "vad": vad_result.to_dict(),
        "asr": asr_result.to_dict(),
        "agent": agent_result.to_dict(),
        "tts": tts_result.to_dict(),
    }

    write_json(result_path, record)
    append_run_log(run_log_path, record)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
