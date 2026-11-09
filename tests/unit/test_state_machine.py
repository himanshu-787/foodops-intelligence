import pytest

from app.order_status import OrderStatus as S
from app.order_status import can_transition


@pytest.mark.parametrize(
    "current,new",
    [
        (S.PLACED, S.ACCEPTED),
        (S.PLACED, S.CANCELLED),
        (S.ACCEPTED, S.PREPARING),
        (S.PREPARING, S.OUT_FOR_DELIVERY),
        (S.OUT_FOR_DELIVERY, S.DELIVERED),
    ],
)
def test_valid_transitions(current, new):
    assert can_transition(current, new) is True


@pytest.mark.parametrize(
    "current,new",
    [
        (S.PLACED, S.DELIVERED),            # beech skip
        (S.OUT_FOR_DELIVERY, S.CANCELLED),  # nikal chuka, cancel nahi
        (S.DELIVERED, S.PREPARING),         # terminal state
        (S.CANCELLED, S.DELIVERED),         # terminal state
    ],
)
def test_invalid_transitions(current, new):
    assert can_transition(current, new) is False