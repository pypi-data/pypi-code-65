#!/usr/bin/env python3
import json
from types import SimpleNamespace


def DotNotation(dict):
    """Return dict as json object with dot notation"""
    dot_notated_dict = json.loads(json.dumps(dict),
                   object_hook=lambda item: SimpleNamespace(**item))
    return dot_notated_dict