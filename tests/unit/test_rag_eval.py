import numpy as np

from app.rag.chunking import Chunk
from app.rag.evaluate import evaluate
from app.rag.store import VectorStore

STORE = VectorStore(
    [Chunk("a-0", "f.md", "A", "a"), Chunk("b-0", "f.md", "B", "b")],
    np.array([[1, 0], [0, 1]], dtype=np.float32),
)


class FakeEmb:
    def embed(self, texts):
        return np.array([[1, 0]], dtype=np.float32)  # hamesha "a" ke paas


def test_metrics_and_misses():
    golden = [("q1", "a-0"), ("q2", "b-0")]  # b-0 rank 2 par aayega
    r = evaluate(STORE, FakeEmb(), golden, k=2)
    assert r["hit_rate"] == 1.0 and r["mrr"] == 0.75
    r1 = evaluate(STORE, FakeEmb(), golden, k=1)
    assert r1["hit_rate"] == 0.5 and r1["misses"][0][1] == "b-0"