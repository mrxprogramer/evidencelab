"""Text extraction and deterministic chunking utilities."""

from __future__ import annotations

import re
from pathlib import Path

SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log"}


def extract_text(filename: str, content: bytes) -> tuple[str, list[tuple[int | None, str]]]:
    """Return full text and page-aware sections; PDF support is an optional extra."""
    suffix = Path(filename).suffix.lower()
    if suffix in SUPPORTED_TEXT_EXTENSIONS:
        text = content.decode("utf-8-sig", errors="replace")
        return text, [(None, text)]
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("PDF support is optional. Install with: pip install -e '.[pdf]'" ) from exc
        import io

        reader = PdfReader(io.BytesIO(content))
        pages = [(index + 1, page.extract_text() or "") for index, page in enumerate(reader.pages)]
        return "\n\n".join(text for _, text in pages), pages
    raise ValueError(f"Unsupported file type: {suffix or '(no extension)'}")


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_sections(
    sections: list[tuple[int | None, str]], size: int = 900, overlap: int = 120
) -> list[dict]:
    """Split sections into overlapping character windows, preferring sentence boundaries."""
    if size < 100 or overlap < 0 or overlap >= size:
        raise ValueError("Require size >= 100 and 0 <= overlap < size")

    chunks: list[dict] = []
    for page, raw in sections:
        text = normalize_text(raw)
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            if end < len(text):
                boundary = max(text.rfind(". ", start + size // 2, end), text.rfind("\n", start + size // 2, end))
                if boundary > start:
                    end = boundary + 1
            piece = text[start:end].strip()
            if piece:
                chunks.append({"text": piece, "page": page, "start": start, "end": end})
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
    return chunks
