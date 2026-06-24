"""Stage 4 — Whisper STT.

Transcribes the synthesised call audio back to text, closing the call-intelligence
loop end-to-end (audio in -> transcript out). Mode via SYNTHGEN_WHISPER:
  local : faster-whisper (no API key; downloads a model once)
  api   : OpenAI Whisper API (needs OPENAI_API_KEY)
"""
from __future__ import annotations
from . import config


def _local(model_size: str = "base"):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def fn(path):
        segments, _ = model.transcribe(str(path))
        return " ".join(s.text.strip() for s in segments)
    return fn


def _api():
    from openai import OpenAI
    client = OpenAI()

    def fn(path):
        with open(path, "rb") as f:
            return client.audio.transcriptions.create(model="whisper-1", file=f).text
    return fn


def transcribe() -> int:
    fn = _local() if config.WHISPER_MODE == "local" else _api()
    n = 0
    for audio in sorted(list(config.AUDIO.glob("*.mp3")) + list(config.AUDIO.glob("*.wav"))):
        out_path = config.TRANSCRIBED / f"{audio.stem}.txt"
        if out_path.exists():
            continue
        out_path.write_text(fn(audio))
        n += 1
    return n


if __name__ == "__main__":
    print("audios transcribed:", transcribe())
