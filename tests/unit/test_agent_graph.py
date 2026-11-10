from types import SimpleNamespace

from langgraph.checkpoint.memory import MemorySaver

from app import assistant, models
from app.agent.graph import build_graph, resume, start

U1 = SimpleNamespace(id=1)


def tool_use(name, inp, id="tu_1"):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=inp)


def text(t):
    return SimpleNamespace(type="text", text=t)


def resp(stop, *blocks):
    return SimpleNamespace(stop_reason=stop, content=list(blocks))


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0
        self.last = {}
        self.messages = self

    def create(self, **kwargs):
        self.calls += 1
        self.last = kwargs
        return self.responses.pop(0)


def status_of(db, order_id):
    db.expire_all()
    return assistant._s(db.get(models.Order, order_id).status)


def graph_for(db, client, user=U1, **kw):
    return build_graph(db, user, client, MemorySaver(), **kw)


def test_read_tool_flow_needs_no_approval(db, order_factory):
    o = order_factory(1)
    c = FakeClient([
        resp("tool_use", tool_use("get_order_status", {"order_id": o.id})),
        resp("end_turn", text("Placed hai")),
    ])
    out = start(graph_for(db, c), "t1", "status?")
    assert out == {"status": "done", "reply": "Placed hai"}


def test_cancel_pauses_before_executing(db, order_factory):
    o = order_factory(1)
    c = FakeClient([resp("tool_use", tool_use("cancel_order", {"order_id": o.id}))])
    out = start(graph_for(db, c), "t1", "cancel karo")
    assert out["status"] == "needs_approval"
    assert out["approval"]["order_id"] == o.id
    assert status_of(db, o.id) == "placed"  # abhi kuch nahi badla


def test_approve_executes_cancel(db, order_factory):
    o = order_factory(1)
    c = FakeClient([
        resp("tool_use", tool_use("cancel_order", {"order_id": o.id})),
        resp("end_turn", text("Cancel ho gaya")),
    ])
    g = graph_for(db, c)
    start(g, "t1", "cancel karo")
    out = resume(g, "t1", True)
    assert out == {"status": "done", "reply": "Cancel ho gaya"}
    assert status_of(db, o.id) == "cancelled"


def test_reject_keeps_order(db, order_factory):
    o = order_factory(1)
    c = FakeClient([
        resp("tool_use", tool_use("cancel_order", {"order_id": o.id})),
        resp("end_turn", text("Theek hai, cancel nahi kiya")),
    ])
    g = graph_for(db, c)
    start(g, "t1", "cancel karo")
    out = resume(g, "t1", False)
    assert out["status"] == "done"
    assert status_of(db, o.id) == "placed"


def test_other_users_order_never_asks_approval(db, order_factory):
    o = order_factory(2)  # order user 2 ka, login user 1
    c = FakeClient([
        resp("tool_use", tool_use("cancel_order", {"order_id": o.id})),
        resp("end_turn", text("Order nahi mila")),
    ])
    out = start(graph_for(db, c), "t1", "cancel")
    assert out["status"] == "done"
    assert status_of(db, o.id) == "placed"


def test_max_steps_gives_up(db, order_factory):
    o = order_factory(1)
    looping = [resp("tool_use", tool_use("get_order_status", {"order_id": o.id})) for _ in range(3)]
    c = FakeClient(looping)
    out = start(graph_for(db, c, max_steps=2), "t1", "x")
    assert out["status"] == "done" and "dikkat" in out["reply"]
    assert c.calls == 2