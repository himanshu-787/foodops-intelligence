from app.evals.gate import check_gate

GOOD = {
    "tool_accuracy": 0.9,
    "args_accuracy": 1.0,
    "dangerous_calls": 0,
    "hit_rate": 1.0,
    "avg_faithfulness": 0.9,
    "p95_ms": 2000,
}


def test_gate_passes_good_metrics():
    assert check_gate(GOOD) == []


def test_gate_fails_below_threshold():
    fails = check_gate({**GOOD, "tool_accuracy": 0.5})
    assert len(fails) == 1 and "tool_accuracy" in fails[0]


def test_gate_fails_closed_on_dangerous_missing_and_none():
    assert any("dangerous_calls" in f for f in check_gate({**GOOD, "dangerous_calls": 1}))
    no_hit = {k: v for k, v in GOOD.items() if k != "hit_rate"}
    assert any("hit_rate" in f for f in check_gate(no_hit))
    assert any("avg_faithfulness" in f for f in check_gate({**GOOD, "avg_faithfulness": None}))