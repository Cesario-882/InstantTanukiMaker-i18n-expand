import json
import os

_current = {}
LOCALE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locale")


def load_language(lang="en"):
    global _current
    path = os.path.join(LOCALE_DIR, f"{lang}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            _current = json.load(f)
    else:
        _current = {}


def _(text, **kwargs):
    result = _current.get(text, text)
    if kwargs:
        result = result.format(**kwargs)
    return result


load_language("en")
