import logging
from types import SimpleNamespace

from app.agent import actions

U1 = SimpleNamespace(id=1)


def test_check_cancel_ok(db, order_factory):
    o = order_factory(1)
    order, err = actions.check_cancel(db, U1, o.id)
    assert err is None and order.id == o.id


def test_check_cancel_hides_other_users_order(db, order_factory):
    o = order_factory(2)
    order, err = actions.check_cancel(db, U1, o.id)
    assert order is None and "not found" in err


def test_check_cancel_refuses_after_preparing(db, order_factory):
    o = order_factory(1, "preparing")
    _, err = actions.check_cancel(db, U1, o.id)
    assert err and "preparing" in err


def test_execute_cancel_changes_status_and_audits(db, order_factory, caplog):
    o = order_factory(1)
    with caplog.at_level(logging.INFO, logger="foodops.audit"):
        out = actions.execute_cancel(db, U1, o.id)
    assert out["status"] == "cancelled"
    assert "cancel_order" in caplog.text