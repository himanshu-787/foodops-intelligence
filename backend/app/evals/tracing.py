import json
import logging
import math
import time
from collections import deque

log = logging.getLogger("foodops.llm")

# USD per 1M tokens: (input, output). PLACEHOLDER, pricing page se verify karo.
PRICES = {"claude-haiku-4-5": (1.00, 5.00)}


def estimate_cost(model: str, in_tok: int, out_tok: int) -> float | None:
    p = PRICES.get(model)
    if p is None:
        return None  # unknown model: cost guess nahi karte
    return (in_tok * p[0] + out_tok * p[1]) / 1_000_000


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile."""
    if not values:
        return 0.0
    s = sorted(values)
    return s[max(0, math.ceil(p / 100 * len(s)) - 1)]


class TracedClient:
    """client.messages.create(...) wahi interface, saath mein latency/tokens/cost record."""

    def __init__(self, inner, tag: str = "llm", max_records: int = 1000):
        self.inner, self.tag = inner, tag
        self.records: deque = deque(maxlen=max_records)
        self.messages = self

    def create(self, **kw):
        t0 = time.perf_counter()
        try:
            resp = self.inner.messages.create(**kw)
        except Exception as e:
            self._record(kw.get("model", "?"), None, t0, type(e).__name__)
            raise
        self._record(kw.get("model", "?"), resp, t0, None)
        return resp

    def _record(self, model, resp, t0, error):
        usage = getattr(resp, "usage", None)
        in_t = getattr(usage, "input_tokens", 0) or 0
        out_t = getattr(usage, "output_tokens", 0) or 0
        rec = {
            "tag": self.tag,
            "model": model,
            "ms": round((time.perf_counter() - t0) * 1000, 1),
            "input_tokens": in_t,
            "output_tokens": out_t,
            "cost_usd": estimate_cost(model, in_t, out_t),
            "error": error,
        }
        self.records.append(rec)
        log.info(json.dumps(rec))  # content nahi, sirf metadata

    def summary(self) -> dict:
        r = list(self.records)
        ms = [x["ms"] for x in r]
        return {
            "calls": len(r),
            "errors": sum(1 for x in r if x["error"]),
            "input_tokens": sum(x["input_tokens"] for x in r),
            "output_tokens": sum(x["output_tokens"] for x in r),
            "cost_usd": round(sum(x["cost_usd"] or 0 for x in r), 6),
            "p50_ms": percentile(ms, 50),
            "p95_ms": percentile(ms, 95),
        }