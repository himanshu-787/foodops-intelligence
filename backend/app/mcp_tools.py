from . import models
from .rag.answer import MIN_SCORE


def clamp_limit(limit, default: int = 3, lo: int = 1, hi: int = 5) -> int:
    try:
        n = int(limit)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, n))


def search_restaurants(db, query: str, limit=3) -> list[dict]:
    q = (query or "").strip()[:50]
    if not q:
        return []
    like = f"%{q}%"
    rows = (
        db.query(models.Restaurant)
        .filter(models.Restaurant.name.ilike(like) | models.Restaurant.cuisine.ilike(like))
        .limit(clamp_limit(limit))
        .all()
    )
    return [{"id": r.id, "name": r.name, "cuisine": r.cuisine} for r in rows]


def search_policies(store, embedder, query: str, k=3, min_score: float = MIN_SCORE) -> list[dict]:
    q = (query or "").strip()[:300]
    if not q:
        return []
    hits = store.search(embedder.embed([q])[0], clamp_limit(k))
    return [
        {"chunk_id": c.id, "title": c.title, "text": c.text, "score": round(s, 3)}
        for c, s in hits
        if s >= min_score
    ]