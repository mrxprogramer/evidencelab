"""A transparent lexical retriever; deliberately dependency-free and inspectable."""

from __future__ import annotations

import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[\w'-]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [token.casefold() for token in TOKEN_RE.findall(text) if len(token) > 1]


def rank_chunks(question: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
    """Rank chunks with a small BM25-style scorer and return score explanations."""
    if top_k < 1:
        raise ValueError("top_k must be at least 1")
    query_terms = tokenize(question)
    if not query_terms or not chunks:
        return []

    tokenized = [tokenize(item["text"]) for item in chunks]
    doc_freq = Counter(term for term in set(query_terms) for doc in tokenized if term in doc)
    avg_len = sum(map(len, tokenized)) / max(len(tokenized), 1)
    k1, b = 1.5, 0.75
    scored = []
    total_docs = len(chunks)

    for item, terms in zip(chunks, tokenized, strict=True):
        frequencies = Counter(terms)
        length_norm = 1 - b + b * (len(terms) / max(avg_len, 1))
        score = 0.0
        matched = []
        for term in set(query_terms):
            frequency = frequencies[term]
            if not frequency:
                continue
            matched.append(term)
            idf = math.log(1 + (total_docs - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            score += idf * (frequency * (k1 + 1)) / (frequency + k1 * length_norm)
        if score > 0:
            scored.append({**item, "score": score, "matched_terms": sorted(matched)})

    return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]
