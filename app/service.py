"""Application use-cases: ingestion, retrieval, grounded answer composition."""

from __future__ import annotations

import hashlib
from pathlib import PurePosixPath

from app.retrieval import rank_chunks
from app.store import SQLiteStore
from app.text_processing import chunk_sections, extract_text


class EvidenceService:
    def __init__(self, store: SQLiteStore, chunk_size: int = 900, chunk_overlap: int = 120):
        self.store = store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def ingest(self, filename: str, content: bytes) -> dict:
        if not content:
            raise ValueError("The uploaded file is empty")
        full_text, sections = extract_text(filename, content)
        if not full_text.strip():
            raise ValueError("No extractable text was found in the document")
        chunks = chunk_sections(sections, self.chunk_size, self.chunk_overlap)
        if not chunks:
            raise ValueError("Document did not produce any searchable chunks")
        digest = hashlib.sha256(content).hexdigest()
        safe_name = PurePosixPath(filename.replace("\\", "/")).name or "upload.txt"
        return self.store.add_document(safe_name, digest, chunks)

    def query(self, question: str, top_k: int = 5) -> dict:
        ranked = rank_chunks(question, self.store.all_chunks(), top_k)
        if not ranked:
            return {
                "answer": "I could not find evidence for this question in the indexed documents.",
                "citations": [], "retrieval_method": "bm25_lite", "grounded": False,
            }

        citations = []
        answer_lines = []
        for item in ranked:
            excerpt = item["text"][:500].strip()
            citations.append({
                "document_id": item["document_id"], "document_name": item["filename"],
                "chunk_id": item["chunk_id"], "page": item["page"],
                "score": round(float(item["score"]), 4), "excerpt": excerpt,
            })
            answer_lines.append(f"- {excerpt} [{len(citations)}]")

        answer = "Relevant evidence found in the indexed documents:\n" + "\n".join(answer_lines)
        return {"answer": answer, "citations": citations, "retrieval_method": "bm25_lite", "grounded": True}
