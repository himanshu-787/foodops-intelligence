from abc import ABC, abstractmethod


# ---------- 1. Class, object, attribute, method ----------
class Order:
    def __init__(self, order_id, items):
        self.order_id = order_id    # attribute
        self.items = items          # e.g. {"dosa": 80, "idli": 40}
        self.status = "PLACED"

    def total(self):                # method
        return sum(self.items.values())

    def cancel(self):
        if self.status == "DELIVERED":
            print("A delivered order cannot be cancelled")
            return
        self.status = "CANCELLED"


# ---------- 2. Encapsulation ----------
class Wallet:
    def __init__(self, balance=0):
        self._balance = balance     # "_" means: internal, do not touch directly

    @property
    def balance(self):              # read-only access from outside
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient balance")
        self._balance -= amount


# ---------- 3. Inheritance + Polymorphism ----------
class Payment(ABC):
    def __init__(self, amount):
        self.amount = amount

    @abstractmethod
    def pay(self):
        """Every child class must implement this."""


class UpiPayment(Payment):
    def pay(self):
        print(f"Paid ₹{self.amount} via UPI")


class CardPayment(Payment):
    def pay(self):
        print(f"Paid ₹{self.amount} via Card")


# ---------- Demo ----------
if __name__ == "__main__":
    order1 = Order(1, {"dosa": 80, "idli": 40})
    order2 = Order(2, {"biryani": 250})

    print(order1.total())       # 120
    order2.cancel()
    print(order2.status)        # CANCELLED
    print(order1.status)        # PLACED (separate object, separate data)

    wallet = Wallet(100)
    wallet.deposit(50)
    print(wallet.balance)       # 150

    payments = [UpiPayment(500), CardPayment(300)]
    for p in payments:
        p.pay()                 # same call, different behaviour