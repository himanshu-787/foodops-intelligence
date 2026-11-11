try:
    from langsmith import traceable  # optional dependency
except ImportError:

    def traceable(*args, **kwargs):
        """langsmith installed nahi: no-op decorator. @traceable aur @traceable(name=...) dono."""
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return args[0]
        return lambda f: f