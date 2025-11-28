import re
import unicodedata
from difflib import SequenceMatcher

_ws_re = re.compile(r"\s+", re.MULTILINE)
_nonword_re = re.compile(r"[^\w\s-]", re.UNICODE)


def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("—", "-").replace("–", "-")
    s = _ws_re.sub(" ", s).strip()
    return s


def normalize_key(s: str) -> str:
    s = normalize_text(s).lower()
    s = _nonword_re.sub("", s)
    s = _ws_re.sub(" ", s).strip()
    return s


def fuzzy_ratio(a: str, b: str) -> float:
    a = normalize_key(a)
    b = normalize_key(b)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def looks_like_heading(s: str) -> bool:
    if not s:
        return False
    # short and title-like, or ALL CAPS
    return (len(s) <= 140 and (s.isupper() or any(ch.isalpha() for ch in s))) and not s.endswith(":")


def extract_number_prefix(s: str) -> int | None:
    # 1) Title, 1. Title, Variation 1: Title etc.
    m = re.match(r"^(?:variation|pattern)?\s*(\d+)[\).:\-\s]+", s, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except:
            return None
    return None
