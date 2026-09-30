"""Module 2: hedge detection (published, tiered lexicon)."""
import re

LOW = ["may", "might", "could", "potentially", "possibly", "uncertain", "cannot guarantee",
       "subject to", "depending on"]
MODERATE = ["expects", "expect", "anticipates", "anticipate", "believes", "likely",
            "approximately", "generally", "typically"]
HIGH = ["will", "delivered", "achieved", "has", "is"]


def _compile(terms: list[str]) -> re.Pattern:
    parts = []
    for t in sorted(terms, key=len, reverse=True):
        p = re.escape(t).replace(r"\ ", r"\s+")
        if t == "may":
            p += r"(?!\s+\d)"        # "May 5" is a month, not a hedge
        parts.append(p)
    return re.compile(r"\b(?:" + "|".join(parts) + r")\b", re.I)


_PATTERNS = {"low": _compile(LOW), "moderate": _compile(MODERATE), "high": _compile(HIGH)}


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text)


def hedge_matches(text: str) -> list[tuple[str, str]]:
    """Every hedge-lexicon hit in reading order, as (term, tier). Used to show WHY a score is what it is."""
    hits = []
    for tier, p in _PATTERNS.items():
        for m in p.finditer(text):
            hits.append((m.start(), re.sub(r"\s+", " ", m.group(0).lower()), tier))
    return [(term, tier) for _, term, tier in sorted(hits)]


def hedge_counts(text: str) -> dict:
    return {tier: len(p.findall(text)) for tier, p in _PATTERNS.items()}


def hedge_density(text: str) -> float:
    """Hedge density = (low + moderate terms) / total words.

    High-certainty words are NOT hedges; they are only used for modal intensity.
    """
    n = len(words(text))
    if n == 0:
        return 0.0
    c = hedge_counts(text)
    return (c["low"] + c["moderate"]) / n


def modal_intensity(text: str):
    """Average certainty: 1 = very uncertain, 3 = very certain. None if no modal words."""
    c = hedge_counts(text)
    total = c["low"] + c["moderate"] + c["high"]
    if total == 0:
        return None
    return (c["low"] * 1 + c["moderate"] * 2 + c["high"] * 3) / total
