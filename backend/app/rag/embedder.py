import numpy as np


def normalize(v: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    return v / np.clip(norms, 1e-12, None)


class Embedder:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None  # lazy: pehli embed() par load hoga

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return: (len(texts), dim) array, har row unit length."""
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(self.model_name)
        vecs = np.array(list(self._model.embed(texts)), dtype=np.float32)
        return normalize(vecs)