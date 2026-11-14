import pytest

from app.evaluation import evaluate_retrieval


def test_retrieval_metrics():
    chunks = [
        {"chunk_id": "one", "text": "FastAPI provides a web API."},
        {"chunk_id": "two", "text": "SQLite stores relational data."},
    ]
    result = evaluate_retrieval(
        [{"question": "What provides the web API?", "relevant_chunk_ids": ["one"]}],
        chunks,
        2,
    )
    assert result["recall_at_k"] == 1.0
    assert result["mrr_at_k"] == 1.0


def test_evaluation_rejects_missing_question():
    with pytest.raises(ValueError, match="question"):
        evaluate_retrieval([{"relevant_chunk_ids": ["one"]}], [], 5)


def test_evaluation_rejects_invalid_relevant_ids():
    with pytest.raises(ValueError, match="relevant_chunk_ids"):
        evaluate_retrieval(
            [{"question": "A valid question", "relevant_chunk_ids": ["one", 3]}],
            [],
            5,
        )


def test_evaluation_rejects_empty_labels():
    with pytest.raises(ValueError, match="No evaluation questions"):
        evaluate_retrieval([{"question": "A valid question"}], [], 5)
