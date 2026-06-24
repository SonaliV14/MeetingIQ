#!/usr/bin/env python3
"""Meeting IQ synthetic-data creator — stage orchestrator.

Usage:
  python run.py skeleton        # Stage 1  (offline, deterministic)
  python run.py expand          # Stage 2  (needs ANTHROPIC_API_KEY)
  python run.py tts             # Stage 3  (needs TTS provider)
  python run.py transcribe      # Stage 4  (local whisper or OPENAI key)
  python run.py assemble        # Stage 5  (offline)
  python run.py validate        # checks   (offline)
  python run.py map             # P7 source archives (offline)
  python run.py load-postgres   # Stage 6a (needs Postgres)
  python run.py load-minio      # Stage 6b (needs MinIO)
  python run.py all             # skeleton -> expand -> tts -> transcribe -> assemble -> validate -> map
"""
import sys
from synthgen import skeleton, validate, assemble, source_map


def main(argv):
    if not argv:
        print(__doc__); return 0
    cmd = argv[0]
    if cmd == "skeleton":
        print(skeleton.build())
    elif cmd == "expand":
        from synthgen import expand_llm
        print("transcripts:", expand_llm.expand_transcripts())
        print("emails:", expand_llm.expand_emails())
        print("documents:", expand_llm.expand_documents())
    elif cmd == "tts":
        from synthgen import tts
        print("audios:", tts.synthesize())
    elif cmd == "transcribe":
        from synthgen import transcribe
        print("transcribed:", transcribe.transcribe())
    elif cmd == "assemble":
        print(assemble.assemble()); assemble.validate_schema()
    elif cmd == "validate":
        return validate.run()
    elif cmd == "map":
        print(source_map.run())
    elif cmd == "load-postgres":
        from synthgen import load_postgres
        print(load_postgres.run())
    elif cmd == "load-minio":
        from synthgen import load_minio
        print(load_minio.run())
    elif cmd == "all":
        skeleton.build()
        from synthgen import expand_llm, tts, transcribe
        expand_llm.expand_transcripts(); expand_llm.expand_emails(); expand_llm.expand_documents()
        tts.synthesize(); transcribe.transcribe()
        assemble.assemble(); assemble.validate_schema()
        validate.run(); source_map.run()
        print("PIPELINE COMPLETE -> out/")
    else:
        print(__doc__); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
