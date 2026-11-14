from app.evaluation import evaluate_retrieval


def test_retrieval_metrics():
    chunks = [
        {"chunk_id": "one", "text": "FastAPI provides a web API."},
        {"chunk_id": "two", "text": "SQLite stores relational data."},
    ]
    result = evaluate_retrieval([{"question": "What provides the web API?", "relevant_chunk_ids": ["one"]}], chunks, 2)
    assert result["recall_at_k"] == 1.0
    assert result["mrr_at_k"] == 1.0
