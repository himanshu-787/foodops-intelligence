from app.evals.observe import traceable


def test_traceable_works_bare_and_with_args():
    @traceable
    def a(x):
        return x + 1

    @traceable(name="b")
    def b(x):
        return x * 2

    assert a(1) == 2 and b(3) == 6