import sqlite3

conn = sqlite3.connect(":memory:")   # temporary DB, sirf practice ke liye
cur = conn.cursor()

cur.executescript("""
CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cuisine TEXT,
    rating REAL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    restaurant_id INTEGER,
    customer TEXT,
    total REAL,
    status TEXT,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

INSERT INTO restaurants VALUES
  (1, 'Biryani House', 'Mughlai', 4.5),
  (2, 'Dosa Corner', 'South Indian', 4.2),
  (3, 'Pizza Point', 'Italian', 4.0),
  (4, 'New Cafe', 'Cafe', 3.8);

INSERT INTO orders VALUES
  (1, 1, 'Rahul', 450, 'DELIVERED'),
  (2, 1, 'Anita', 300, 'DELIVERED'),
  (3, 2, 'Rahul', 120, 'PLACED'),
  (4, 3, 'Kiran', 600, 'CANCELLED');
""")


def run(title, sql):
    print(f"\n--- {title} ---")
    for row in cur.execute(sql):
        print(row)


run("1. Filter + sort", """
    SELECT name, rating FROM restaurants
    WHERE rating >= 4.2 ORDER BY rating DESC
""")

run("2. INNER JOIN", """
    SELECT r.name, o.customer, o.total
    FROM orders o JOIN restaurants r ON o.restaurant_id = r.id
""")

run("3. LEFT JOIN + COUNT (jis restaurant ka order nahi, woh bhi dikhega)", """
    SELECT r.name, COUNT(o.id) AS order_count
    FROM restaurants r LEFT JOIN orders o ON o.restaurant_id = r.id
    GROUP BY r.id
""")

run("4. GROUP BY + HAVING (delivered revenue 400 se zyada)", """
    SELECT r.name, SUM(o.total) AS revenue
    FROM orders o JOIN restaurants r ON o.restaurant_id = r.id
    WHERE o.status = 'DELIVERED'
    GROUP BY r.name
    HAVING SUM(o.total) > 400
""")

run("5. Second highest rating (classic interview question)", """
    SELECT MAX(rating) FROM restaurants
    WHERE rating < (SELECT MAX(rating) FROM restaurants)
""")