GOLDEN = [
    ("How long does a refund take?", "refund-policy-0"),
    ("My food is 40 minutes late, can I get compensation?", "late-delivery-0"),
    ("Can I cancel after the restaurant starts preparing?", "order-cancellation-0"),
    ("Is delivery free?", "delivery-fee-0"),
    ("Can I pay with cash?", "payment-methods-0"),
    ("They forgot my fries", "wrong-or-missing-items-0"),
    ("I forgot my password", "account-and-password-0"),
    ("Is the food nut free?", "allergies-and-dietary-info-0"),
]


def evaluate(store, embedder, golden=GOLDEN, k: int = 3) -> dict:
    hits, rr, misses = 0, 0.0, []
    for question, expected in golden:
        ids = [c.id for c, _ in store.search(embedder.embed([question])[0], k)]
        if expected in ids:
            hits += 1
            rr += 1 / (ids.index(expected) + 1)
        else:
            misses.append((question, expected, ids))
    n = len(golden)
    return {"hit_rate": hits / n, "mrr": rr / n, "misses": misses}


if __name__ == "__main__":
    from .embedder import Embedder
    from .store import INDEX_PATH, VectorStore

    for k in (1, 3):
        r = evaluate(VectorStore.load(INDEX_PATH), Embedder(), k=k)
        print(f"k={k}  hit_rate={r['hit_rate']:.2f}  mrr={r['mrr']:.2f}")
        for q, exp, got in r["misses"]:
            print(f"   MISS: {q!r} expected {exp}, got {got}")