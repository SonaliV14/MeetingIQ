"""Stage 3 — TTS (the 12 recorded calls).

Reads each audio-flagged meeting transcript, splits it into speaker turns, and
synthesises one WAV file per meeting using pyttsx3 (fully offline, no API key).

Fixes vs the previous version:
  - Bug: engine re-init in a loop caused SAPI5 to only write the last queued
    segment (~3 sec). Fix: one engine instance per meeting, all turns queued
    before a single runAndWait(), then concat the per-turn WAVs.
  - Bug: Windows SAPI5 only has 2 built-in voices. Fix: speaker differentiation
    is done via rate + volume combinations across as many slots as needed, so
    every speaker sounds distinct regardless of how many SAPI5 voices exist.
  - Bug: no terminal output during the (slow) synthesis loop. Fix: per-meeting
    and per-turn progress lines printed to stdout.
"""
from __future__ import annotations

import json
import re
import wave
import time
from pathlib import Path
from . import config


# ---------------------------------------------------------------------------
# encoding-safe file reader (handles cp1252 transcripts written on Windows)
# ---------------------------------------------------------------------------

def _read_text(path: Path) -> str:
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return path.read_bytes().decode("latin-1", errors="replace")


# ---------------------------------------------------------------------------
# transcript parsing
# ---------------------------------------------------------------------------

def _audio_meetings() -> list[dict]:
    ms = [
        json.loads(l)
        for l in (config.SKELETON / "meetings.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    return [m for m in ms if m.get("audio")]


def _turns(transcript: str) -> list[tuple[str, str]]:
    """Parse 'Speaker Name: dialogue text' lines.

    Also strips optional [persona:role] prefixes:
      [salesperson:AE] Priya Menon: Hi there ...
    → ('Priya Menon', 'Hi there ...')
    """
    turns = []
    for line in transcript.splitlines():
        line = re.sub(r"^\s*\[[^\]]+\]\s*", "", line)
        mm = re.match(r"^\s*([A-Z][a-zA-Z .'\-]{1,40}):\s*(.+)$", line)
        if mm:
            turns.append((mm.group(1).strip(), mm.group(2).strip()))
    return turns


# ---------------------------------------------------------------------------
# voice differentiation via rate + volume combos
#
# Windows SAPI5 typically ships with only 2 voices (David ♂ and Zira ♀).
# We cannot rely on having more. Instead we assign each unique speaker a
# (voice_index, rate, volume) slot so they sound distinct from each other.
# With 2 voices × 3 rates × 2 volumes = 12 distinguishable combinations —
# more than enough for the 3-4 speakers in any one call.
# ---------------------------------------------------------------------------

_SLOTS = [
    # (voice_idx, rate_delta, volume)  — voice_idx wraps to available count
    (0,   0,  1.00),   # slot 0: voice-A, normal
    (1,   0,  1.00),   # slot 1: voice-B, normal
    (0,  40,  0.92),   # slot 2: voice-A, faster
    (1, -30,  1.00),   # slot 3: voice-B, slower
    (0, -30,  0.95),   # slot 4: voice-A, slower
    (1,  40,  0.90),   # slot 5: voice-B, faster
    (0,  70,  0.88),   # slot 6: voice-A, fast
    (1,  70,  0.88),   # slot 7: voice-B, fast
    (0, -50,  1.00),   # slot 8: voice-A, slow
    (1, -50,  0.95),   # slot 9: voice-B, slow
    (0,  20,  0.85),   # slot 10
    (1, -15,  0.90),   # slot 11
]


# ---------------------------------------------------------------------------
# WAV concatenation (no ffmpeg needed)
# ---------------------------------------------------------------------------

def _concat_wavs(parts: list[Path], out_path: Path) -> None:
    """Concatenate WAV segments that share the same audio params."""
    valid = [p for p in parts if p.exists() and p.stat().st_size > 44]
    if not valid:
        print("    [tts] warning: no valid WAV segments to concatenate")
        return
    all_frames = b""
    params = None
    for p in valid:
        try:
            with wave.open(str(p), "rb") as wf:
                if params is None:
                    params = wf.getparams()
                all_frames += wf.readframes(wf.getnframes())
        except wave.Error as exc:
            print(f"    [tts] warning: skipping corrupt segment {p.name}: {exc}")
    if params and all_frames:
        with wave.open(str(out_path), "wb") as out:
            out.setparams(params)
            out.writeframes(all_frames)


# ---------------------------------------------------------------------------
# pyttsx3 backend  — one engine instance per meeting, all turns pre-queued
# ---------------------------------------------------------------------------

def _pyttsx3_tts(
    meeting_id: str,
    turns: list[tuple[str, str]],
    out_path: Path,
) -> None:
    """
    Synthesise every turn for one meeting into a single WAV.

    KEY FIX: pyttsx3 on Windows (SAPI5) only writes audio for the LAST
    save_to_file() call when you call runAndWait() repeatedly in a loop.
    The correct pattern is:
      1. Queue ALL save_to_file() calls on one engine instance.
      2. Call runAndWait() ONCE — SAPI5 processes the whole queue.
      3. Concat the per-segment WAVs into the final file.
      4. Destroy the engine (del eng) — do NOT re-use it across meetings
         or SAPI5 can deadlock on the second call.
    """
    try:
        import pyttsx3
    except ImportError as exc:
        raise RuntimeError("pip install pyttsx3>=2.90") from exc

    eng = pyttsx3.init()
    all_voices = eng.getProperty("voices") or []
    n_voices = max(len(all_voices), 1)
    base_rate = eng.getProperty("rate")

    print(f"  [tts] {meeting_id}: {len(turns)} turns, {n_voices} SAPI5 voice(s) available")

    # Assign a stable slot to each unique speaker in this meeting
    speaker_slot: dict[str, int] = {}
    for speaker, _ in turns:
        if speaker not in speaker_slot:
            speaker_slot[speaker] = len(speaker_slot) % len(_SLOTS)

    tmp_dir = out_path.parent / f"_tmp_{meeting_id}"
    tmp_dir.mkdir(exist_ok=True)
    seg_paths: list[Path] = []

    try:
        # --- queue all segments BEFORE calling runAndWait() ---
        for i, (speaker, text) in enumerate(turns):
            slot = _SLOTS[speaker_slot[speaker]]
            voice_idx, rate_delta, volume = slot

            # pick voice (wraps if fewer voices than slots reference)
            if all_voices:
                eng.setProperty("voice", all_voices[voice_idx % n_voices].id)
            eng.setProperty("rate", max(80, base_rate + rate_delta))
            eng.setProperty("volume", volume)

            seg = tmp_dir / f"{i:04d}.wav"
            eng.save_to_file(text, str(seg))
            seg_paths.append(seg)
            print(f"    [{i+1:02d}/{len(turns):02d}] queued: {speaker[:20]:<20} → {seg.name}")

        # --- single runAndWait() processes the whole queue ---
        print(f"  [tts] {meeting_id}: running SAPI5 engine (may take a moment)...")
        t0 = time.time()
        eng.runAndWait()
        print(f"  [tts] {meeting_id}: engine done in {time.time()-t0:.1f}s")

        # --- verify segments were actually written ---
        for i, seg in enumerate(seg_paths):
            size = seg.stat().st_size if seg.exists() else 0
            status = f"{size} bytes" if size > 44 else "EMPTY/MISSING"
            print(f"    seg {i:04d}.wav: {status}")

        # --- concat into the final WAV ---
        wav_out = out_path.with_suffix(".wav")
        _concat_wavs(seg_paths, wav_out)
        if wav_out.exists():
            duration_s = wav_out.stat().st_size / (2 * 16000)  # rough estimate (16-bit, 16kHz)
            print(f"  [tts] {meeting_id}: wrote {wav_out.name} (~{duration_s:.0f}s estimated)")
        else:
            print(f"  [tts] {meeting_id}: WARNING — output WAV not created")

    finally:
        del eng   # must destroy — do NOT call eng.stop() then reuse on Windows
        for seg in seg_paths:
            seg.unlink(missing_ok=True)
        try:
            tmp_dir.rmdir()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# public entry point
# ---------------------------------------------------------------------------

BACKENDS = {"pyttsx3": _pyttsx3_tts}


def synthesize() -> int:
    """Synthesise audio for every audio-flagged meeting that has a transcript.

    Returns the number of new WAV files written.
    Idempotent: skips any meeting whose .wav or .mp3 already exists in AUDIO.
    """
    provider = config.TTS_PROVIDER
    if provider not in BACKENDS:
        raise RuntimeError(
            f"TTS provider '{provider}' not wired. "
            f"Set SYNTHGEN_TTS=pyttsx3 in .env (available: {list(BACKENDS)})"
        )
    backend = BACKENDS[provider]

    meetings = _audio_meetings()
    print(f"[tts] {len(meetings)} audio-flagged meetings found")

    n = 0
    for m in meetings:
        mid = m["id"]
        tpath = config.ARTIFACTS / f"transcript_{mid}.txt"
        if not tpath.exists():
            print(f"  [tts] {mid}: no transcript yet (run expand first) — skipping")
            continue

        wav_out = config.AUDIO / f"{mid}.wav"
        mp3_out = config.AUDIO / f"{mid}.mp3"
        if wav_out.exists() or mp3_out.exists():
            print(f"  [tts] {mid}: already done — skipping")
            continue

        turns = _turns(_read_text(tpath))
        if not turns:
            print(f"  [tts] {mid}: WARNING — no parseable turns in transcript — skipping")
            print(f"         first 200 chars: {_read_text(tpath)[:200]!r}")
            continue

        print(f"\n[tts] === starting {mid} ({m.get('title', '')}) ===")
        backend(mid, turns, mp3_out)
        n += 1

    print(f"\n[tts] done — {n} new audio file(s) written to {config.AUDIO}")
    return n


if __name__ == "__main__":
    print("audios synthesised:", synthesize())