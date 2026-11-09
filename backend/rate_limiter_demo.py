import time


class TokenBucket:
    def __init__(self, capacity: int, refill_per_sec: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_per_sec = refill_per_sec
        self.last = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        # Beete time ke hisaab se tokens wapas bharo (capacity se zyada nahi)
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.refill_per_sec)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


bucket = TokenBucket(capacity=3, refill_per_sec=1)

for i in range(1, 7):
    print(f"Request {i}:", "allowed" if bucket.allow() else "429 Too Many Requests")

time.sleep(2)
print("2 second baad:", "allowed" if bucket.allow() else "429")