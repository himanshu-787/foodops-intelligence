from types import SimpleNamespace

from app.evals.toolcalls import ToolCase, evaluate_tools


def tu(name, inp):
    return SimpleNamespace(type="tool_use", id="t", name=name, input=inp)


def tx(t):
    return SimpleNamespace(type="text", text=t)


class ScriptClient:
    """Message ke hisaab se pehle se tay jawab deta hai."""

    def __init__(self, script):
        self.script = script
        self.messages = self

    def create(self, **kw):
        return SimpleNamespace(content=[self.script[kw["messages"][0]["content"]]])


def test_perfect_run():
    cases = [ToolCase("a", "get_order_status", {"order_id": 1}), ToolCase("b", None)]
    c = ScriptClient({"a": tu("get_order_status", {"order_id": 1}), "b": tx("hi")})
    r = evaluate_tools(c, cases)
    assert r["tool_accuracy"] == 1.0 and r["args_accuracy"] == 1.0 and r["dangerous_calls"] == 0


def test_wrong_tool_goes_to_misses():
    cases = [ToolCase("a", "get_order_status", {"order_id": 1})]
    c = ScriptClient({"a": tu("search_restaurants", {"query": "x"})})
    r = evaluate_tools(c, cases)
    assert r["tool_accuracy"] == 0.0 and r["args_accuracy"] == 0.0
    assert r["misses"] == [("a", "get_order_status", "search_restaurants")]


def test_unwanted_cancel_counts_as_dangerous():
    cases = [ToolCase("a", "get_order_status", {"order_id": 1})]
    c = ScriptClient({"a": tu("cancel_order", {"order_id": 1})})
    assert evaluate_tools(c, cases)["dangerous_calls"] == 1