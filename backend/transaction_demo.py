import sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.cursor()

cur.executescript("""
CREATE TABLE wallets (user TEXT PRIMARY KEY, balance REAL CHECK (balance >= 0));
CREATE TABLE orders (id INTEGER PRIMARY KEY, user TEXT, amount REAL);
INSERT INTO wallets VALUES ('Rahul', 600);
""")
conn.commit()


def place_order(user, amount, crash=False):
    try:
        cur.execute("UPDATE wallets SET balance = balance - ? WHERE user = ?", (amount, user))
        if crash:
            raise RuntimeError("Server crash!")     # beech mein failure
        cur.execute("INSERT INTO orders (user, amount) VALUES (?, ?)", (user, amount))
        conn.commit()                                # dono kaam successful
        print("Order placed")
    except Exception as e:
        conn.rollback()                              # dono undo
        print("Rolled back:", e)


def show():
    print("Wallet:", cur.execute("SELECT * FROM wallets").fetchall(),
          "| Orders:", cur.execute("SELECT * FROM orders").fetchall())


place_order("Rahul", 500, crash=True)   # fail
show()                                   # balance abhi bhi 600, order nahi

place_order("Rahul", 500)                # success
show()                                   # balance 100, 1 order

place_order("Rahul", 500)                # balance 100 hai, CHECK constraint fail
show()                                   # kuch nahi badla