from types import SimpleNamespace

import numpy as np

from app.rag.answer import NO_ANSWER, answer_question
from app.rag.chunking import Chunk
from app.rag.store import VectorStore

STORE = VectorStore(
    [Chunk("a-0", "f.md", "A", "text a"), Chunk("b-0", "f.md", "B", "text b")],
    np.array([[1, 0], [0, 1]], dtype=np.float32),
)


class FakeEmb:
    def __init__(self, vec):
        self.vec = np.array([vec], dtype=np.float32)

    def embed(self, texts):
        return self.vec


class FakeClient:
    def __init__(self, text):
        self.text, self.calls, self.messages = text, 0, self

    def create(self, **kwargs):
        self.calls += 1
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.text)])


def test_only_valid_citations_kept():
    c = FakeClient("Refund 5-7 din mein [1]. Aur ye bhi [9].")
    r = answer_question("q", STORE, FakeEmb([1, 0]), c)
    assert [s["n"] for s in r.sources] == [1] and r.grounded


def test_uncited_answer_is_not_grounded():
    r = answer_question("q", STORE, FakeEmb([1, 0]), FakeClient("Pata nahi"))
    assert not r.grounded and r.sources == []


def test_weak_retrieval_skips_llm():
    c = FakeClient("should never be used")
    r = answer_question("q", STORE, FakeEmb([0, 0]), c)  # score 0 < MIN_SCORE
    assert r.reply == NO_ANSWER and c.calls == 0