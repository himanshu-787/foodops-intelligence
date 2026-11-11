import numpy as np

from app.mcp_tools import clamp_limit, search_policies
from app.rag.chunking import Chunk
from app.rag.store import VectorStore

STORE = VectorStore(
    [Chunk("a-0", "f.md", "A", "text a"), Chunk("b-0", "f.md", "B", "text b")],
    np.array([[1, 0], [0, 1]], dtype=np.float32),
)


class FakeEmb:
    def embed(self, texts):
        return np.array([[1, 0]], dtype=np.float32)


def test_clamp_limit():
    assert clamp_limit(100) == 5 and clamp_limit(-3) == 1 and clamp_limit("abc") == 3


def test_search_policies_drops_weak_hits_and_empty_query():
    out = search_policies(STORE, FakeEmb(), "refund", k=2)
    assert [h["chunk_id"] for h in out] == ["a-0"]  # b-0 ka score 0 < MIN_SCORE
    assert search_policies(STORE, FakeEmb(), "   ") == []