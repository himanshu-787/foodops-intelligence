import time

cache = {}          # key -> (value, expiry_time)
hits = 0
misses = 0


def slow_db_query():
    time.sleep(0.5)                     # DB ki slowness ka nakli simulation
    return ["Biryani House", "Dosa Corner", "Pizza Point"]


def get_restaurants(ttl_seconds=5):
    global hits, misses
    entry = cache.get("restaurants")
    if entry and entry[1] > time.time():        # cache mein hai aur expire nahi hua
        hits += 1
        return entry[0]

    misses += 1                                  # miss: DB se lo
    data = slow_db_query()
    cache["restaurants"] = (data, time.time() + ttl_seconds)
    return data


def invalidate():
    cache.pop("restaurants", None)               # data badla toh cache hatao


for i in range(1, 6):
    start = time.perf_counter()
    get_restaurants()
    print(f"Request {i}: {(time.perf_counter() - start) * 1000:.1f} ms")

print(f"hits={hits}, misses={misses}, hit ratio={hits / (hits + misses):.0%}")

invalidate()
start = time.perf_counter()
get_restaurants()
print(f"Invalidate ke baad: {(time.perf_counter() - start) * 1000:.1f} ms (phir miss)")