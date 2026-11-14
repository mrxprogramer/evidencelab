"""FastAPI entry point."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.config import settings
from app.evaluation import evaluate_retrieval
from app.schemas import EvaluationRequest, IngestResponse, QueryRequest, QueryResponse
from app.service import EvidenceService
from app.store import SQLiteStore

store = SQLiteStore(settings.db_path)
service = EvidenceService(store, settings.chunk_size, settings.chunk_overlap)
app = FastAPI(title="EvidenceLab API", version="0.1.0", description="Source-grounded document retrieval with measurable retrieval quality.")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "evidencelab"}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><title>EvidenceLab</title>
    <style>body{font:16px system-ui;max-width:760px;margin:4rem auto;padding:0 1rem;color:#18212f}
    input,textarea,button{font:inherit;padding:.65rem;margin:.3rem 0;width:100%;box-sizing:border-box}
    button{background:#172b4d;color:white;border:0;border-radius:6px;cursor:pointer}
    pre{white-space:pre-wrap;background:#f2f4f7;padding:1rem;border-radius:8px}</style></head><body>
    <h1>EvidenceLab</h1><p>Index documents, ask questions, and inspect the retrieved evidence.</p>
    <h2>1. Add a document</h2><input id='file' type='file' accept='.txt,.md,.csv,.json,.log,.pdf'>
    <button onclick='upload()'>Upload and index</button><pre id='uploadResult'>No document uploaded.</pre>
    <h2>2. Ask a question</h2><textarea id='question' rows='3' placeholder='Ask something contained in your documents'></textarea>
    <button onclick='ask()'>Search evidence</button><pre id='answer'>Answers and citations will appear here.</pre>
    <script>
    async function upload(){const f=document.getElementById('file').files[0];if(!f)return;const d=new FormData();d.append('file',f);
    const r=await fetch('/documents', {method:'POST',body:d});document.getElementById('uploadResult').textContent=JSON.stringify(await r.json(),null,2)}
    async function ask(){const question=document.getElementById('question').value;const r=await fetch('/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question})});document.getElementById('answer').textContent=JSON.stringify(await r.json(),null,2)}
    </script></body></html>"""


@app.post("/documents", response_model=IngestResponse)
async def upload_document(file: Annotated[UploadFile, File()]) -> dict:
    content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds configured upload limit")
    try:
        result = service.ingest(file.filename or "upload.txt", content)
    except (ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"document_id": result["id"], "filename": result["filename"], "chunks_created": result["chunks_created"], "status": "already_indexed" if result["duplicate"] else "indexed"}


@app.get("/documents")
def list_documents() -> list[dict]:
    return store.list_documents()


@app.delete("/documents/{document_id}")
def delete_document(document_id: str) -> dict:
    if not store.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True, "document_id": document_id}


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest) -> dict:
    return service.query(request.question, request.top_k)


@app.post("/evaluate")
def evaluate(request: EvaluationRequest) -> dict:
    questions = request.questions
    if questions is None:
        import json
        from pathlib import Path
        path = Path("evals/questions.json")
        if not path.exists():
            raise HTTPException(status_code=404, detail="Evaluation file not found")
        questions = json.loads(path.read_text(encoding="utf-8"))
    try:
        return evaluate_retrieval(questions, store.all_chunks(), request.top_k)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
