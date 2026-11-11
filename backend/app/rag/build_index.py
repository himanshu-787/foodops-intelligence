from .chunking import chunk_markdown
from .embedder import Embedder
from .store import DOCS_DIR, INDEX_PATH, VectorStore


def build() -> VectorStore:
    chunks = []
    for f in sorted(DOCS_DIR.glob("*.md")):
        chunks += chunk_markdown(f.read_text(encoding="utf-8"), f.name)
    # title saath embed karo: contextual header
    vecs = Embedder().embed([f"{c.title}\n{c.text}" for c in chunks])
    store = VectorStore(chunks, vecs)
    store.save(INDEX_PATH)
    return store


if __name__ == "__main__":
    s = build()
    print(f"{len(s.chunks)} chunks indexed, vectors shape {s.vectors.shape}")