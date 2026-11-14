"""Runtime configuration loaded from environment variables."""

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Settings:
    db_path: str = os.getenv("EVIDENCELAB_DB_PATH", "./data/evidencelab.sqlite3")
    max_upload_mb: int = int(os.getenv("EVIDENCELAB_MAX_UPLOAD_MB", "15"))
    chunk_size: int = int(os.getenv("EVIDENCELAB_CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("EVIDENCELAB_CHUNK_OVERLAP", "120"))


settings = Settings()
