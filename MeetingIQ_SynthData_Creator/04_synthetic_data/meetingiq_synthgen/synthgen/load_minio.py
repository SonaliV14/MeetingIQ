"""Stage 6b — load blobs into MinIO (object storage).

Uploads the call audio (Stage 3) and document files (Stage 2) to MinIO so blobs
live where they will in production (S3-compatible). Requires the MinIO service from
docker-compose.

  pip install minio
"""
from __future__ import annotations
import os
from . import config

BUCKET = os.getenv("MINIO_BUCKET", "meetingiq")


def _client():
    from minio import Minio
    return Minio(os.getenv("MINIO_ENDPOINT", "localhost:9000"),
                 access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                 secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"), secure=False)


def run() -> dict:
    client = _client()
    if not client.bucket_exists(BUCKET):
        client.make_bucket(BUCKET)
    n_audio = n_doc = 0
    for f in list(config.AUDIO.glob("*.mp3")) + list(config.AUDIO.glob("*.wav")):
        client.fput_object(BUCKET, f"audio/{f.name}", str(f)); n_audio += 1
    for f in config.ARTIFACTS.glob("doc_*.md"):
        client.fput_object(BUCKET, f"documents/{f.name}", str(f)); n_doc += 1
    return {"audio": n_audio, "documents": n_doc}


if __name__ == "__main__":
    print("uploaded to minio:", run())
