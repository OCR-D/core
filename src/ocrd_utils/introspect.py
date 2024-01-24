"""
Utility functions to simplify access to data structures.
"""
import json
from functools import wraps
from frozendict import frozendict


# Taken from https://github.com/OCR-D/core/pull/884
def freeze_args(func):
    """
    Transform mutable dictionary into immutable. Useful to be compatible with cache.
    Code taken from `this post <https://stackoverflow.com/a/53394430/1814420>`_
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([frozendict(arg) if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: frozendict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped


def membername(class_, val):
    """Convert a member variable/constant into a member name string."""
    return next((k for k, v in class_.__dict__.items() if v == val), str(val))

def set_json_key_value_overrides(obj, *kvpairs):
    for kv in kvpairs:
        k, v = kv
        try:
            obj[k] = json.loads(v)
        except json.decoder.JSONDecodeError:
            obj[k] = v
    return obj
