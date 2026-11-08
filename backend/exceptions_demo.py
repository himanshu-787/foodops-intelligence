# =====================================================
# 1. Without handling vs with handling
# =====================================================

def average_price(items):
    # average_price([]) -> ZeroDivisionError, app crashes
    return sum(items) / len(items)


def safe_average(items):
    try:
        return sum(items) / len(items)
    except ZeroDivisionError:
        print("Cart is empty")
        return 0
    finally:
        print("Always runs (cleanup goes here)")


# =====================================================
# 2. Custom exceptions
# =====================================================

class OrderError(Exception):
    """Base class for all order-related errors."""


class EmptyCartError(OrderError):
    pass


class PaymentFailedError(OrderError):
    def __init__(self, needed, available):
        self.needed = needed
        self.available = available
        super().__init__(f"Insufficient balance: need ₹{needed}, have ₹{available}")


def place_order(cart, balance):
    if not cart:
        raise EmptyCartError("Cart is empty")

    total = sum(cart)
    if total > balance:
        raise PaymentFailedError(total, balance)

    return "Order placed"


# =====================================================
# Demo
# =====================================================

def try_order(cart, balance):
    try:
        print(place_order(cart, balance))
    except EmptyCartError as e:
        print("Error:", e)
    except PaymentFailedError as e:
        print("Payment error:", e)


if __name__ == "__main__":
    print(safe_average([100, 200]))   # 150.0
    print(safe_average([]))           # 0

    try_order([250, 180], 300)        # payment error
    try_order([], 300)                # empty cart
    try_order([100, 50], 300)         # order placed