class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


a = Config()
b = Config()
print(a is b)    # True, dono same object

class UpiPayment:
    def pay(self, amount): print(f"UPI se ₹{amount}")

class CardPayment:
    def pay(self, amount): print(f"Card se ₹{amount}")


def payment_factory(method: str):
    if method == "upi":
        return UpiPayment()
    if method == "card":
        return CardPayment()
    raise ValueError(f"Unknown method: {method}")


payment_factory("upi").pay(500)

class OrderEvent:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, fn):
        self.subscribers.append(fn)

    def publish(self, order_id):
        for fn in self.subscribers:
            fn(order_id)


event = OrderEvent()
event.subscribe(lambda oid: print(f"Restaurant ko khabar: order {oid}"))
event.subscribe(lambda oid: print(f"Customer ko SMS: order {oid}"))
event.publish(101)

def festival_discount(total): return total * 0.8
def no_discount(total): return total
def new_user_discount(total): return total - 100


def checkout(total, strategy):
    return strategy(total)


print(checkout(1000, festival_discount))    # 800.0
print(checkout(1000, new_user_discount))    # 900