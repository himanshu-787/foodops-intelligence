import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ai-engine"))
from triage import parse_triage, triage_message  # noqa: E402

GOOD = '{"intent":"refund","sentiment":"negative","urgency":3,"order_id":5,"summary":"Wants refund"}'


class FakeClient:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = 0
        self.messages = self

    def create(self, **kwargs):
        self.calls += 1
        return SimpleNamespace(content=[SimpleNamespace(text=self.outputs.pop(0))])


def test_parse_clean_json():
    assert parse_triage(GOOD).order_id == 5


def test_parse_with_code_fence():
    assert parse_triage(f"```json\n{GOOD}\n```").intent == "refund"


def test_parse_rejects_bad_enum():
    with pytest.raises(ValueError):
        parse_triage(GOOD.replace("refund", "angry"))


def test_parse_rejects_urgency_out_of_range():
    with pytest.raises(ValueError):
        parse_triage(GOOD.replace('"urgency":3', '"urgency":9'))


def test_retry_recovers():
    c = FakeClient(["sorry, here you go: nothing", GOOD])
    assert triage_message("x", client=c).intent == "refund"
    assert c.calls == 2


def test_retry_gives_up():
    c = FakeClient(["bad", "bad"])
    with pytest.raises(ValueError):
        triage_message("x", client=c)