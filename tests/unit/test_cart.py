from cart import calculate_total


def test_no_discount_below_threshold():
    assert calculate_total([200, 100]) == 300


def test_discount_above_threshold():
    assert calculate_total([300, 300]) == 540   # 600 ka 10% off


def test_empty_cart_is_zero():
    assert calculate_total([]) == 0