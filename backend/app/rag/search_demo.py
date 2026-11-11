import sys

from .embedder import Embedder
from .store import INDEX_PATH, VectorStore

q = " ".join(sys.argv[1:]) or "how long does a refund take"
for chunk, score in VectorStore.load(INDEX_PATH).search(Embedder().embed([q])[0], k=3):
    print(f"{score:.2f}  {chunk.id}")