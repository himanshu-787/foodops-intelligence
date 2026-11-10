import logging
import os

from .. import assistant, models

audit = logging.getLogger("foodops.audit")
CANCELLABLE = {"placed", "confirmed"}


def writes_enabled() -> bool:
    """Kill switch. 12.5 mein use hoga."""
    return os.getenv("AGENT_WRITES_ENABLED", "true").lower() == "true"


def check_cancel(db, user, order_id: int):
    """Return (order, error). Ownership + status check. Kuch badalta nahi."""
    order = (
        db.query(models.Order)
        .filter(models.Order.id == order_id, models.Order.user_id == user.id)
        .first()
    )
    if order is None:  # dusre ka order bhi yahi jawab dega
        return None, f"Order {order_id} not found"
    status = assistant._s(order.status)
    if status not in CANCELLABLE:
        return None, f"Order {order_id} cancel nahi ho sakta (status: {status})"
    return order, None


def execute_cancel(db, user, order_id: int) -> dict:
    """Asli write. Approval ke BAAD hi call hota hai. Dobara check karta hai."""
    order, err = check_cancel(db, user, order_id)
    if err:
        audit.info("action=cancel_order user_id=%s order_id=%s result=refused", user.id, order_id)
        return {"error": err}

    # TODO: yahan apni order_status.py ka cancel function call karo
    # (wo stock wapas karta hai). Ye simplified version stock wapas NAHI karta.
    order.status = "cancelled"
    db.commit()
    audit.info("action=cancel_order user_id=%s order_id=%s result=cancelled", user.id, order_id)
    return {"order_id": order.id, "status": "cancelled"}