"""Runtime configuration loaded from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    db_path: str = os.getenv("EVIDENCELAB_DB_PATH", "./data/evidencelab.sqlite3")
    max_upload_mb: int = int(os.getenv("EVIDENCELAB_MAX_UPLOAD_MB", "15"))
    chunk_size: int = int(os.getenv("EVIDENCELAB_CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("EVIDENCELAB_CHUNK_OVERLAP", "120"))

    def __post_init__(self) -> None:
        if not self.db_path.strip():
            raise ValueError("EVIDENCELAB_DB_PATH must not be empty")
        if self.max_upload_mb < 1:
            raise ValueError("EVIDENCELAB_MAX_UPLOAD_MB must be at least 1")
        if self.chunk_size < 100:
            raise ValueError("EVIDENCELAB_CHUNK_SIZE must be at least 100")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError(
                "EVIDENCELAB_CHUNK_OVERLAP must be non-negative and smaller than chunk size"
            )


settings = Settings()
