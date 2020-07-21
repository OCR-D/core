"""
Utility functions to simplify access to data structures.
"""
import json

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
