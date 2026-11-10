from .embedder import Embedder

SENTS = [
    "Refunds are issued to the original payment method.",
    "Delivery is free on orders above Rs 299.",
    "Reset your password from the login page.",
    "Cash on delivery is available up to Rs 2000.",
]
QUERIES = [
    "How long until my money comes back?",
    "paisa wapas kab milega",
    "forgot login",
]

e = Embedder()
S = e.embed(SENTS)
print("vector shape:", S.shape)
for q in QUERIES:
    scores = S @ e.embed([q])[0]  # normalized hain, toh dot = cosine
    best = int(scores.argmax())
    print(f"\n{q!r}\n  best: {SENTS[best]} ({scores[best]:.2f})")
    print("  all :", [round(float(s), 2) for s in scores])