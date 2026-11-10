import numpy as np

from app.rag.embedder import normalize


def test_normalize_gives_unit_length():
    v = normalize(np.array([[3.0, 4.0]]))
    assert abs(float(np.linalg.norm(v[0])) - 1.0) < 1e-6


def test_dot_of_normalized_is_cosine():
    a = normalize(np.array([[1.0, 0.0]]))[0]
    b = normalize(np.array([[0.0, 5.0]]))[0]
    assert abs(float(a @ a) - 1.0) < 1e-6  # same direction
    assert abs(float(a @ b)) < 1e-6  # perpendicular
    