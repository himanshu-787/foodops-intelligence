import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ai-engine"))
from tool_calling import chat_with_tools, run_tool  # noqa: E402


def tool_use(name, inp, id="tu_1"):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=inp)


def text(t):
    return SimpleNamespace(type="text", text=t)


def resp(stop, *blocks):
    return SimpleNamespace(stop_reason=stop, content=list(blocks))


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.seen = []
        self.messages = self

    def create(self, **kwargs):
        self.seen.append(list(kwargs["messages"]))  # snapshot
        return self.responses.pop(0)


def test_run_tool_ok():
    out, err = run_tool("get_order_status", {"order_id": 42})
    assert not err and "out_for_delivery" in out


def test_run_tool_unknown():
    _, err = run_tool("delete_database", {})
    assert err


def test_run_tool_invalid_args():
    _, err = run_tool("get_order_status", {"order_id": -5})
    assert err


def test_loop_calls_tool_then_answers():
    c = FakeClient([
        resp("tool_use", tool_use("get_order_status", {"order_id": 42})),
        resp("end_turn", text("25 min mein aa jayega")),
    ])
    assert chat_with_tools("order 42?", client=c) == "25 min mein aa jayega"
    assert len(c.seen) == 2


def test_tool_result_has_matching_id():
    c = FakeClient([
        resp("tool_use", tool_use("get_order_status", {"order_id": 42}, id="abc")),
        resp("end_turn", text("ok")),
    ])
    chat_with_tools("x", client=c)
    last_msg = c.seen[1][-1]
    assert last_msg["content"][0]["tool_use_id"] == "abc"


def test_max_steps_stops_infinite_loop():
    looping = [resp("tool_use", tool_use("get_order_status", {"order_id": 42})) for _ in range(3)]
    with pytest.raises(RuntimeError):
        chat_with_tools("x", client=FakeClient(looping), max_steps=3)