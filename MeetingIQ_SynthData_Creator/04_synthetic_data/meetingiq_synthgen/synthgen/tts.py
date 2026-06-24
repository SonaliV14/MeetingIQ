"""Stage 3 — TTS (the 12 recorded calls).

Reads each audio-flagged meeting's transcript, splits it into speaker turns, and
synthesises per-speaker audio, concatenated into one file per meeting. Provider is
pluggable via SYNTHGEN_TTS: openai | azure | elevenlabs | pyttsx3 (offline).

Only the 12 audio meetings are synthesised — that's the whole point of keeping the
call-intelligence path real without paying to voice every meeting.
"""
from __future__ import annotations
import json
import os
import re
from . import config


def _audio_meetings():
    ms = [json.loads(l) for l in (config.SKELETON / "meetings.jsonl").read_text().splitlines() if l.strip()]
    return [m for m in ms if m.get("audio")]


def _turns(transcript: str):
    """Split 'Name: text' lines into (speaker, text) turns."""
    turns = []
    for line in transcript.splitlines():
        mm = re.match(r"^\s*([A-Z][a-zA-Z .'-]{1,40}):\s*(.+)$", line)
        if mm:
            turns.append((mm.group(1).strip(), mm.group(2).strip()))
    return turns


# ---- provider backends ----
def _voice_for(speaker: str, voices: list[str]) -> str:
    return voices[hash(speaker) % len(voices)]


def _openai_tts(turns, out_path):
    from openai import OpenAI
    from pydub import AudioSegment
    client = OpenAI()
    voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    segs = []
    tmp = out_path.with_suffix(".part.mp3")
    for spk, text in turns:
        r = client.audio.speech.create(model="gpt-4o-mini-tts", voice=_voice_for(spk, voices), input=text)
        r.stream_to_file(str(tmp))
        segs.append(AudioSegment.from_file(tmp))
    if segs:
        out = sum(segs[1:], segs[0])
        out.export(out_path, format="mp3")
    tmp.unlink(missing_ok=True)


def _pyttsx3_tts(turns, out_path):
    # offline fallback; one voice, no per-speaker timbre, but produces real audio
    import pyttsx3
    eng = pyttsx3.init()
    text = " ... ".join(f"{s}. {t}" for s, t in turns)
    eng.save_to_file(text, str(out_path.with_suffix(".wav")))
    eng.runAndWait()


BACKENDS = {"openai": _openai_tts, "pyttsx3": _pyttsx3_tts}


def synthesize() -> int:
    backend = BACKENDS.get(config.TTS_PROVIDER)
    if backend is None:
        raise RuntimeError(f"TTS provider '{config.TTS_PROVIDER}' not wired; use openai or pyttsx3, "
                           "or add azure/elevenlabs to BACKENDS")
    n = 0
    for m in _audio_meetings():
        tpath = config.ARTIFACTS / f"transcript_{m['id']}.txt"
        if not tpath.exists():
            continue
        out_path = config.AUDIO / f"{m['id']}.mp3"
        if out_path.exists():
            continue
        backend(_turns(tpath.read_text()), out_path)
        n += 1
    return n


if __name__ == "__main__":
    print("audios synthesised:", synthesize())
