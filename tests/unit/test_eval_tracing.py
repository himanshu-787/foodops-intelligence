from types import SimpleNamespace

import pytest

from app.evals import tracing


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


def test_records_tokens_and_cost(monkeypatch):
    monkeypatch.setitem(tracing.PRICES, "m", (1.0, 5.0))
    c = tracing.TracedClient(Inner())
    c.create(model="m", messages=[])
    s = c.summary()
    assert s["calls"] == 1 and s["input_tokens"] == 1000 and s["output_tokens"] == 500
    assert s["cost_usd"] == pytest.approx(0.0035)  # 1000*1 + 500*5 per million


def test_error_is_recorded_and_reraised():
    c = tracing.TracedClient(Inner(fail=True))
    with pytest.raises(RuntimeError):
        c.create(model="m", messages=[])
    assert c.summary()["errors"] == 1


def test_percentile_nearest_rank():
    assert tracing.percentile([10, 20, 30, 40], 50) == 20
    assert tracing.percentile([10, 20, 30, 40], 95) == 40
    assert tracing.percentile([], 95) == 0.0