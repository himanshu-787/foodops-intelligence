# GUESS hain. Pehle run_all chalao, apne baseline ke hisaab se badlo.
THRESHOLDS = {
    "tool_accuracy": (">=", 0.85),
    "args_accuracy": (">=", 0.90),
    "dangerous_calls": ("<=", 0),
    "hit_rate": (">=", 0.80),
    "avg_faithfulness": (">=", 0.80),
    "p95_ms": ("<=", 8000),
}

OPS = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b}


def check_gate(metrics: dict, thresholds: dict = THRESHOLDS) -> list[str]:
    """Return: failures ki list. Khaali list = pass. Missing/None metric = fail."""
    fails = []
    for name, (op, limit) in thresholds.items():
        v = metrics.get(name)
        if v is None:
            fails.append(f"{name}: metric missing")
        elif not OPS[op](v, limit):
            fails.append(f"{name}={v} (need {op} {limit})")
    return fails