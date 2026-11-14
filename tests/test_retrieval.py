import pytest

from app.retrieval import rank_chunks


def test_retriever_ranks_relevant_chunk_first():
    chunks = [
        {"chunk_id": "a", "text": "The mitochondrion produces cellular energy through respiration."},
        {"chunk_id": "b", "text": "A bicycle has two wheels and a chain."},
    ]
    result = rank_chunks("How does mitochondrion produce energy?", chunks, 2)
    assert result[0]["chunk_id"] == "a"
    assert result[0]["score"] > 0


def test_retriever_returns_empty_for_no_match():
    assert rank_chunks("quantum telescope", [{"chunk_id": "x", "text": "bread and butter"}]) == []


def test_retriever_rejects_non_positive_top_k():
    with pytest.raises(ValueError, match="top_k"):
        rank_chunks("test query", [{"chunk_id": "x", "text": "test query"}], 0)
