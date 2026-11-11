from types import SimpleNamespace

import numpy as np
import pytest
from prometheus_client import REGISTRY

from app.evals import tracing
from app.rag.answer import answer_question
from app.rag.chunking import Chunk
from app.rag.store import VectorStore


def val(name, labels=None):
    return REGISTRY.get_sample_value(name, labels or {}) or 0.0


class Inner:
    def __init__(self, fail=False):
        self.fail = fail
        self.messages = self

    def create(self, **kw):
        if self.fail:
            raise RuntimeError("boom")
        return SimpleNamespace(
            content=[], usage=SimpleNamespace(input_tokens=1000, output_tokens=500)
        )


def test_llm_call_updates_tokens_cost_and_calls(monkeypatch):
    monkeypatch.setitem(tracing.PRICES, "m15", (1.0, 5.0))
    tok = {"model": "m15", "direction": "input"}
    calls = {"tag": "t15", "model": "m15", "outcome": "ok"}
    b_tok = val("foodops_llm_tokens_total", tok)
    b_cost = val("foodops_llm_cost_usd_total", {"model": "m15"})
    b_calls = val("foodops_llm_calls_total", calls)

    tracing.TracedClient(Inner(), tag="t15").create(model="m15", messages=[])

    assert val("foodops_llm_tokens_total", tok) == b_tok + 1000
    assert val("foodops_llm_cost_usd_total", {"model": "m15"}) == pytest.approx(b_cost + 0.0035)
    assert val("foodops_llm_calls_total", calls) == b_calls + 1


def test_llm_error_counted_as_error_outcome():
    labels = {"tag": "t15", "model": "m15e", "outcome": "error"}
    before = val("foodops_llm_calls_total", labels)
    with pytest.raises(RuntimeError):
        tracing.TracedClient(Inner(fail=True), tag="t15").create(model="m15e", messages=[])
    assert val("foodops_llm_calls_total", labels) == before + 1


def test_rag_weak_retrieval_counts_no_answer_and_top_score():
    store = VectorStore(
        [Chunk("a-0", "f.md", "A", "text a")], np.array([[1, 0]], dtype=np.float32)
    )

    class Emb:
        def embed(self, texts):
            return np.array([[0, 0]], dtype=np.float32)  # score 0

    b_na = val("foodops_rag_answers_total", {"outcome": "no_answer"})
    b_n = val("foodops_rag_top_score_count")
    answer_question("q", store, Emb(), client=None)  # LLM call hi nahi hoti
    assert val("foodops_rag_answers_total", {"outcome": "no_answer"}) == b_na + 1
    assert val("foodops_rag_top_score_count") == b_n + 1
