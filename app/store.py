"""SQLite persistence with explicit transactions and parameterized SQL."""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any


class SQLiteStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    sha256 TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    text TEXT NOT NULL,
                    page INTEGER,
                    ordinal INTEGER NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id);
                """
            )

    def add_document(self, filename: str, sha256: str, chunks: list[dict]) -> dict[str, Any]:
        with self.connect() as db:
            existing = db.execute("SELECT id, filename FROM documents WHERE sha256 = ?", (sha256,)).fetchone()
            if existing:
                count = db.execute("SELECT COUNT(*) AS n FROM chunks WHERE document_id = ?", (existing["id"],)).fetchone()["n"]
                return {"id": existing["id"], "filename": existing["filename"], "chunks_created": count, "duplicate": True}

            document_id = str(uuid.uuid4())
            db.execute("INSERT INTO documents (id, filename, sha256) VALUES (?, ?, ?)", (document_id, filename, sha256))
            for ordinal, chunk in enumerate(chunks):
                db.execute(
                    "INSERT INTO chunks (id, document_id, text, page, ordinal, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                    (str(uuid.uuid4()), document_id, chunk["text"], chunk.get("page"), ordinal,
                     json.dumps({"start": chunk.get("start"), "end": chunk.get("end") })),
                )
            return {"id": document_id, "filename": filename, "chunks_created": len(chunks), "duplicate": False}

    def all_chunks(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT c.id AS chunk_id, c.document_id, d.filename, c.text, c.page, c.ordinal "
                "FROM chunks c JOIN documents d ON d.id = c.document_id ORDER BY d.created_at, c.ordinal"
            ).fetchall()
        return [dict(row) for row in rows]

    def list_documents(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT d.id, d.filename, d.created_at, COUNT(c.id) AS chunks "
                "FROM documents d LEFT JOIN chunks c ON c.document_id=d.id "
                "GROUP BY d.id ORDER BY d.created_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def delete_document(self, document_id: str) -> bool:
        with self.connect() as db:
            cursor = db.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            return cursor.rowcount > 0
