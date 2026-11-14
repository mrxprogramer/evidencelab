"""Offline retrieval evaluation using a small, inspectable JSONL dataset."""

from __future__ import annotations

from app.retrieval import rank_chunks


def evaluate_retrieval(questions: list[dict], chunks: list[dict], top_k: int = 5) -> dict:
    if not questions:
        raise ValueError("Evaluation set is empty")

    recalls, reciprocal_ranks = [], []
    evaluated = 0
    for item in questions:
        expected = set(item.get("relevant_chunk_ids", []))
        if not expected:
            continue
        ranked = rank_chunks(item["question"], chunks, top_k)
        found = [row["chunk_id"] for row in ranked]
        recalls.append(len(expected.intersection(found)) / len(expected))
        reciprocal_ranks.append(next((1 / (i + 1) for i, chunk_id in enumerate(found) if chunk_id in expected), 0.0))
        evaluated += 1

    if not evaluated:
        raise ValueError("No evaluation questions contain relevant_chunk_ids")
    return {
        "evaluated_questions": evaluated,
        "recall_at_k": round(sum(recalls) / evaluated, 4),
        "mrr_at_k": round(sum(reciprocal_ranks) / evaluated, 4),
        "k": top_k,
        "note": "Metrics evaluate retrieval only, not answer correctness or clinical validity.",
    }
