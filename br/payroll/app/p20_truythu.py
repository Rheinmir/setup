"""Stub p20_truythu — /br run sẽ đắp code thật (test-first: xem tests/).
Public API raise NotImplementedError; dunder attrs (__path__…) raise AttributeError
để không phá import machinery."""

def __getattr__(name):
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(name)
    raise NotImplementedError(f"{name} chưa cài — chờ /br run frame p20_truythu")
