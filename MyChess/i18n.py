"""Tiny translation layer.  English text is the key; missing entries fall back to English."""

LANGUAGES = {'en': 'English', 'es': 'Español', 'fr': 'Français', 'de': 'Deutsch', 'pt': 'Português', 'it': 'Italiano'}
_current = 'en'
from translations import TRANSLATIONS


def set_language(code):
    global _current
    _current = code if code in LANGUAGES else 'en'


def get_language():
    return _current


def tr(text):
    if _current == 'en':
        return text
    return TRANSLATIONS.get(_current, {}).get(text, text)
