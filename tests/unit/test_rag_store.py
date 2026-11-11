import numpy as np

from app.rag.chunking import Chunk
from app.rag.store import VectorStore

CHUNKS = [Chunk("a-0", "f.md", "A", "text a"), Chunk("b-0", "f.md", "B", "text b")]
VECS = np.array([[1, 0], [0, 1]], dtype=np.float32)


def test_search_ranks_closest_first():
    hits = VectorStore(CHUNKS, VECS).search(np.array([0.9, 0.1], dtype=np.float32), k=2)
    assert [c.id for c, _ in hits] == ["a-0", "b-0"]
    assert hits[0][1] > hits[1][1]


def test_save_load_roundtrip(tmp_path):
    p = tmp_path / "i.npz"
    VectorStore(CHUNKS, VECS).save(p)
    loaded = VectorStore.load(p)
    assert [c.id for c in loaded.chunks] == ["a-0", "b-0"]
    assert loaded.vectors.shape == (2, 2)