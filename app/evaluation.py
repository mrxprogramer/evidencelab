"""Offline retrieval evaluation using a small, inspectable JSONL dataset."""

from __future__ import annotations

from app.retrieval import rank_chunks


def evaluate_retrieval(questions: list[dict], chunks: list[dict], top_k: int = 5) -> dict:
    if top_k < 1:
        raise ValueError("top_k must be at least 1")
    if not questions:
        raise ValueError("Evaluation set is empty")

    recalls, reciprocal_ranks = [], []
    for index, item in enumerate(questions):
        question = item.get("question")
        if not isinstance(question, str) or len(question.strip()) < 3:
            raise ValueError(f"Evaluation question at index {index} is missing or too short")
        relevant_ids = item.get("relevant_chunk_ids", [])
        if not isinstance(relevant_ids, list) or any(
            not isinstance(chunk_id, str) or not chunk_id.strip() for chunk_id in relevant_ids
        ):
            raise ValueError(f"relevant_chunk_ids at index {index} must be a list of non-empty strings")
        expected = set(relevant_ids)
        if not expected:
            continue

        ranked = rank_chunks(question, chunks, top_k)
        found = [row["chunk_id"] for row in ranked]
        recalls.append(len(expected.intersection(found)) / len(expected))
        reciprocal_ranks.append(
            next((1 / (rank + 1) for rank, chunk_id in enumerate(found) if chunk_id in expected), 0.0)
        )

    if not recalls:
        raise ValueError("No evaluation questions contain relevant_chunk_ids")
    evaluated = len(recalls)
    return {
        "evaluated_questions": evaluated,
        "recall_at_k": round(sum(recalls) / evaluated, 4),
        "mrr_at_k": round(sum(reciprocal_ranks) / evaluated, 4),
        "k": top_k,
        "note": "Metrics evaluate retrieval only, not answer correctness or clinical validity.",
    }
