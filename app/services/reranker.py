from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.core.config import settings


@lru_cache(maxsize=1)
def get_reranker():
    return CrossEncoder(
        settings.reranker_model
    )


def rerank(
    question: str,
    candidates: list,
    top_k: int,
):
    if not candidates:
        return []

    model = get_reranker()

    pairs = [
        (
            question,
            candidate["content"],
        )
        for candidate in candidates
    ]

    scores = model.predict(pairs)

    ranked = []

    for candidate, score in zip(
        candidates,
        scores,
    ):
        candidate = candidate.copy()

        candidate["rerank_score"] = float(
            score
        )

        ranked.append(candidate)

    ranked.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return ranked[:top_k]