import sqlite3
import time
import random

conn = sqlite3.connect(":memory:")
cur = conn.cursor()

cur.execute("CREATE TABLE restaurants (id INTEGER PRIMARY KEY, name TEXT, cuisine TEXT)")

cuisines = ["Mughlai", "South Indian", "Italian", "Chinese", "Cafe"]
rows = [(i, f"Restaurant {i}", random.choice(cuisines)) for i in range(1, 200_001)]
cur.executemany("INSERT INTO restaurants VALUES (?, ?, ?)", rows)
conn.commit()


def timed_search():
    start = time.perf_counter()
    for _ in range(200):
        cur.execute("SELECT * FROM restaurants WHERE name = ?", ("Restaurant 150000",)).fetchall()
    return (time.perf_counter() - start) * 1000


print("Bina index :", round(timed_search(), 1), "ms")

cur.execute("CREATE INDEX idx_name ON restaurants(name)")

print("Index ke saath:", round(timed_search(), 1), "ms")

print("\nQuery plan:")
for row in cur.execute("EXPLAIN QUERY PLAN SELECT * FROM restaurants WHERE name = 'Restaurant 150000'"):
    print(row)