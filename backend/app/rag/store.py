from pathlib import Path
from typing import Sequence

import numpy as np

from .chunking import Chunk

RAG_DIR = Path(__file__).resolve().parent
DOCS_DIR = RAG_DIR / "docs"
INDEX_PATH = RAG_DIR / "index.npz"


class VectorStore:
    def __init__(self, chunks: Sequence[Chunk], vectors: np.ndarray):
        self.chunks: list[Chunk] = list(chunks)
        self.vectors: np.ndarray = np.asarray(vectors, dtype=np.float32)

    def search(self, query_vec: np.ndarray, k: int = 3) -> list[tuple[Chunk, float]]:
        if not self.chunks or self.vectors.size == 0:
            return []

        q = np.asarray(query_vec, dtype=np.float32)
        norm_q = float(np.linalg.norm(q))
        if norm_q <= 1e-12:
            scores = np.zeros(len(self.chunks), dtype=np.float32)
        else:
            norm_v = np.linalg.norm(self.vectors, axis=1)
            denom = np.maximum(norm_v * norm_q, 1e-12)
            scores = np.dot(self.vectors, q) / denom

        top_indices = np.argsort(scores)[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in top_indices]

    def save(self, path: Path | str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        ids = np.array([c.id for c in self.chunks], dtype=object)
        sources = np.array([c.source for c in self.chunks], dtype=object)
        titles = np.array([c.title for c in self.chunks], dtype=object)
        texts = np.array([c.text for c in self.chunks], dtype=object)
        np.savez_compressed(
            p,
            vectors=self.vectors,
            ids=ids,
            sources=sources,
            titles=titles,
            texts=texts,
        )

    @classmethod
    def load(cls, path: Path | str) -> "VectorStore":
        p = Path(path)
        with np.load(p, allow_pickle=True) as data:
            vectors = np.asarray(data["vectors"], dtype=np.float32)
            ids = data["ids"]
            sources = data["sources"]
            titles = data["titles"]
            texts = data["texts"]
            chunks = [
                Chunk(str(i), str(s), str(ti), str(te))
                for i, s, ti, te in zip(ids, sources, titles, texts)
            ]
        return cls(chunks, vectors)
