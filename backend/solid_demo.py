from abc import ABC, abstractmethod


# =====================================================
# S - Single Responsibility: one class, one job
# =====================================================

# BAD: one class does 3 jobs
class BadOrderService:
    def place_order(self, order):
        print("Order saved")
        print("Payment taken")
        print("Email sent")


# GOOD: one class per job
class OrderRepository:
    def save(self, order):
        print("Order saved in DB")


class PaymentProcessor:
    def charge(self, amount):
        print(f"Charged ₹{amount}")


# =====================================================
# O - Open/Closed: open for extension, closed for change
# =====================================================

# BAD: every new payment type means editing this function
def bad_pay(method, amount):
    if method == "upi":
        print("UPI")
    elif method == "card":
        print("Card")
    # new type = change code here


# GOOD: new type = new class, old code untouched
class Payment(ABC):
    @abstractmethod
    def pay(self, amount):
        ...


class UpiPayment(Payment):
    def pay(self, amount):
        print(f"Paid ₹{amount} via UPI")


class WalletPayment(Payment):
    def pay(self, amount):
        print(f"Paid ₹{amount} via Wallet")


def checkout(payment: Payment, amount):
    payment.pay(amount)         # this function never needs to change


# =====================================================
# L - Liskov Substitution: child must keep parent's promise
# =====================================================

class SimplePayment:
    def pay(self, amount):
        print(f"₹{amount} paid")


# BAD: child breaks what the caller expects
class BrokenPayment(SimplePayment):
    def pay(self, amount):
        raise Exception("Not supported")


# GOOD: child does the same job, in its own way
class CardPayment(SimplePayment):
    def pay(self, amount):
        print(f"Paid ₹{amount} via Card")


# =====================================================
# I - Interface Segregation: small, focused interfaces
# =====================================================

# BAD: a delivery person is forced to implement cook()
class BadWorker(ABC):
    @abstractmethod
    def cook(self):
        ...

    @abstractmethod
    def deliver(self):
        ...


# GOOD: separate small interfaces
class Cook(ABC):
    @abstractmethod
    def cook(self):
        ...


class DeliveryPerson(ABC):
    @abstractmethod
    def deliver(self):
        ...


class Chef(Cook):
    def cook(self):
        print("Cooking food")


class Rider(DeliveryPerson):
    def deliver(self):
        print("Delivering food")


# =====================================================
# D - Dependency Inversion: depend on abstraction, not detail
# =====================================================

class Notifier(ABC):
    @abstractmethod
    def send(self, message):
        ...


class EmailNotifier(Notifier):
    def send(self, message):
        print(f"Email: {message}")


class SmsNotifier(Notifier):
    def send(self, message):
        print(f"SMS: {message}")


class OrderService:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier        # injected from outside

    def place(self, order_id):
        print(f"Order {order_id} placed")
        self.notifier.send(f"Order {order_id} confirmed")


# =====================================================
# Demo
# =====================================================
if __name__ == "__main__":
    checkout(UpiPayment(), 500)
    checkout(WalletPayment(), 200)

    Chef().cook()
    Rider().deliver()

    service = OrderService(SmsNotifier())   # to switch to Email, change only this line
    service.place(101)