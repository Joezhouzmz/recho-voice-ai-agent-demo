from __future__ import annotations

import shutil
import struct
import wave
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class VADResult:
    input_path: str
    output_path: str
    backend: str
    sample_rate: int
    channels: int
    sample_width: int
    total_seconds: float
    speech_start_seconds: float
    speech_end_seconds: float
    speech_seconds: float
    num_speech_segments: int
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def segment_speech(
    input_path: Path,
    output_path: Path,
) -> VADResult:
    padding_ms = 250
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import torch
        from silero_vad import get_speech_timestamps, load_silero_vad, read_audio
    except ImportError as exc:
        raise RuntimeError(
            "Silero VAD dependencies are not installed. "
            "Run `.venv/bin/python -m pip install -r requirements-optional.txt`."
        ) from exc

    sampling_rate = 16000
    wav = read_audio(str(input_path), sampling_rate=sampling_rate)
    model = load_silero_vad()
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sampling_rate)

    total_seconds = len(wav) / float(sampling_rate) if sampling_rate else 0.0
    if not speech_timestamps:
        shutil.copyfile(input_path, output_path)
        return VADResult(
            input_path=str(input_path),
            output_path=str(output_path),
            backend="silero",
            sample_rate=sampling_rate,
            channels=1,
            sample_width=2,
            total_seconds=round(total_seconds, 3),
            speech_start_seconds=0.0,
            speech_end_seconds=round(total_seconds, 3),
            speech_seconds=round(total_seconds, 3),
            num_speech_segments=0,
            note="Silero detected no speech; copied original audio for downstream ASR.",
        )

    padding_samples = int(sampling_rate * padding_ms / 1000)
    segments = []
    for timestamp in speech_timestamps:
        start = max(0, int(timestamp["start"]) - padding_samples)
        end = min(len(wav), int(timestamp["end"]) + padding_samples)
        segments.append(wav[start:end])
    speech_wav = torch.cat(segments) if len(segments) > 1 else segments[0]
    _write_float_tensor_as_wav(output_path, speech_wav, sampling_rate)

    speech_start = max(0, int(speech_timestamps[0]["start"]) - padding_samples) / float(sampling_rate)
    speech_end = min(len(wav), int(speech_timestamps[-1]["end"]) + padding_samples) / float(sampling_rate)
    speech_seconds = sum(len(segment) for segment in segments) / float(sampling_rate)
    return VADResult(
        input_path=str(input_path),
        output_path=str(output_path),
        backend="silero",
        sample_rate=sampling_rate,
        channels=1,
        sample_width=2,
        total_seconds=round(total_seconds, 3),
        speech_start_seconds=round(speech_start, 3),
        speech_end_seconds=round(speech_end, 3),
        speech_seconds=round(speech_seconds, 3),
        num_speech_segments=len(speech_timestamps),
        note="Segmented speech with Silero VAD.",
    )

def _write_float_tensor_as_wav(path: Path, audio, sample_rate: int) -> None:
    samples = audio.detach().cpu().clamp(-1.0, 1.0).tolist()
    pcm = bytearray()
    for sample in samples:
        pcm.extend(struct.pack("<h", int(sample * 32767)))

    with wave.open(str(path), "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(sample_rate)
        target.writeframes(bytes(pcm))
