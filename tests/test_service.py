from app.service import EvidenceService
from app.store import SQLiteStore


def test_ingest_query_and_duplicate_detection(tmp_path):
    store = SQLiteStore(str(tmp_path / "test.sqlite3"))
    service = EvidenceService(store, chunk_size=300, chunk_overlap=30)
    content = b"The project uses FastAPI for its HTTP interface and SQLite for persistence."
    first = service.ingest("architecture.txt", content)
    second = service.ingest("renamed.txt", content)
    assert first["id"] == second["id"]
    assert second["duplicate"] is True
    response = service.query("What is used for the HTTP interface?")
    assert response["grounded"] is True
    assert response["citations"][0]["document_name"] == "architecture.txt"


def test_query_without_documents_is_not_grounded(tmp_path):
    service = EvidenceService(SQLiteStore(str(tmp_path / "empty.sqlite3")))
    response = service.query("What is the answer?")
    assert response["grounded"] is False
    assert response["citations"] == []
