import json
import os
import sys

_strings: dict = {}
_lang: str = "ko"

LANG_OPTIONS = {
    "English":          "en",
    "한국어":            "ko",
    "Bahasa Indonesia": "id",
    "Español":          "es",
}
LANG_CODES = {v: k for k, v in LANG_OPTIONS.items()}

LANG_NAMES = {
    "en": "English",
    "ko": "Korean",
    "id": "Indonesian",
    "es": "Spanish",
}


def _locales_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "locales")


def load(lang: str = "ko"):
    global _strings, _lang
    _lang = lang
    path = os.path.join(_locales_dir(), f"{lang}.json")
    try:
        with open(path, encoding="utf-8") as f:
            _strings = json.load(f)
    except Exception:
        _strings = {}


def t(key: str, **kwargs) -> str:
    text = _strings.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text


def current() -> str:
    return _lang
