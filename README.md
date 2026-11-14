# EvidenceLab

**Evaluation-first, source-grounded document retrieval.** EvidenceLab indexes documents, retrieves relevant passages, returns inspectable citations, and exposes retrieval metrics. The baseline is CPU-friendly and runs without a hosted LLM or GPU.

> Status: early-stage reference implementation (v0.1.0). It is not a production security boundary and must not be used as a clinical decision-support system.

## Why this project exists

A typical document chatbot demonstrates a happy path but makes it difficult to inspect why a passage was retrieved or whether retrieval quality regressed. EvidenceLab keeps the baseline intentionally transparent: deterministic chunking, a small BM25-style lexical ranker, explicit citations, and offline Recall@K / MRR@K evaluation.

## Features

- Upload `.txt`, `.md`, `.csv`, `.json`, and `.log` documents.
- Optional PDF text extraction (`pip install -e '.[pdf]'`). Scanned PDFs are not OCR'd.
- Deterministic overlapping chunking with page metadata where available.
- Lexical BM25-style retrieval with matched-term explanations available internally.
- Extractive responses with document and chunk citations; no fabricated generative answer.
- SQLite persistence, duplicate-content detection, list and delete endpoints.
- Offline retrieval evaluation (Recall@K and MRR@K).
- FastAPI OpenAPI docs, minimal browser UI, Docker, pytest, Ruff, and GitHub Actions.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e '.[dev,pdf]'
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` for the minimal UI or `http://127.0.0.1:8000/docs` for the API.

### Docker

```bash
docker compose up --build
```

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/documents` | Upload and index a document (`multipart/form-data`, field `file`) |
| `GET` | `/documents` | List indexed documents |
| `DELETE` | `/documents/{document_id}` | Delete a document and its chunks |
| `POST` | `/query` | Retrieve evidence for a question |
| `POST` | `/evaluate` | Evaluate retrieval against labeled questions |

Example query:

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"How does EvidenceLab retrieve evidence?","top_k":5}'
```

A query response includes `answer`, `citations`, `retrieval_method`, and `grounded`. If no indexed passage matches, `grounded` is false and citations are empty.

## Evaluation

The evaluation endpoint accepts an explicit JSON body:

```json
{
  "top_k": 5,
  "questions": [
    { "question": "Which framework serves HTTP?", "relevant_chunk_ids": ["chunk-id"] }
  ]
}
```

To build a meaningful benchmark:

1. Ingest a fixed document corpus.
2. Create questions representative of actual user information needs.
3. Label relevant chunk IDs using a documented annotation protocol.
4. Run the same benchmark before and after retrieval changes.
5. Report corpus version, K, number of questions, Recall@K, and MRR@K.

Do not use placeholder IDs from `evals/questions.json` as real labels. The included JSON is a template; replace its ID after indexing the sample document or pass labeled questions directly to `/evaluate`.

## Architecture

```text
Browser / API client
        |
     FastAPI
        |
  EvidenceService
   /          \
Parser       Retriever (BM25-style lexical scoring)
   |                 |
Chunker          Ranked chunks
   \                 /
       SQLite store
             |
       Citations + metrics
```

### Design decisions

- **No model required in the baseline:** makes the first run reproducible and cheap. It also avoids pretending that a generated answer is grounded merely because a prompt requests citations.
- **Lexical retrieval first:** offers a debuggable baseline against which future embedding or hybrid retrieval can be measured.
- **Extractive answer composition:** answer text is derived from retrieved excerpts. It is less fluent than a generative model but easier to audit.
- **SQLite:** keeps local setup simple. A multi-user deployment should move to a managed database and add tenant isolation.

## Limitations and next engineering steps

This is a portfolio-grade foundation, not a finished enterprise platform. Before production use, add authentication and authorization, tenant isolation, malware scanning, rate limiting, robust PDF/OCR handling, background ingestion, database migrations, structured observability, and load tests. Retrieval quality should be evaluated on a real domain corpus. Embedding/hybrid retrieval and optional LLM answer synthesis should be added behind interfaces and compared against this baseline, not substituted without measurement.

## Development

```bash
python -m pip install -e '.[dev,pdf]'
ruff check app tests
pytest
```

## Repository hygiene

Commit source, tests, benchmark definitions, and documentation. Do not commit `.env`, API keys, private documents, local SQLite databases, or generated caches. Replace this README's example claims with your own measured results after running the benchmark.

## License

MIT. See [LICENSE](LICENSE).
