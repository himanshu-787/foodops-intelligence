from types import SimpleNamespace

import pytest

from app.evals.judge import judge_agreement, parse_verdict


class FakeClient:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.messages = self

    def create(self, **kw):
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.outputs.pop(0))])


def test_parse_verdict_with_code_fence():
    v = parse_verdict('```json\n{"verdict":"supported","reason":"ok"}\n```')
    assert v.verdict == "supported"


def test_bad_verdict_raises():
    with pytest.raises(ValueError):
        parse_verdict('{"verdict":"maybe","reason":"?"}')


def test_judge_agreement_counts_matches_and_misses():
    cases = [("ctx a", "ans a", "supported"), ("ctx b", "ans b", "unsupported")]
    c = FakeClient([
        '{"verdict":"supported","reason":""}',
        '{"verdict":"supported","reason":""}',  # galat: unsupported hona chahiye tha
    ])
    r = judge_agreement(c, cases)
    assert r["agreement"] == 0.5
    assert r["misses"] == [("ans b", "unsupported", "supported")]