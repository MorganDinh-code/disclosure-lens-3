"""Module 3: linguistic tone.

Uses the Loughran-McDonald master dictionary when a CSV is available (set the
DISCLOSURE_LENS_LM_CSV environment variable, or drop the file into data/ with a name
starting "Loughran-McDonald"). Otherwise falls back to a tiny built-in placeholder list.
Positive words preceded by a negation ("not strong") are counted as negative.
"""
import csv
import os
from functools import lru_cache
from pathlib import Path

from .hedges import words

SCALE = 10  # scaling so typical sentences land between -1 and +1 (tune this later)
NEGATORS = {"not", "no", "never", "without", "neither", "nor", "hardly"}
NEGATION_WINDOW = 3

_FALLBACK_POS = {"strong", "record", "excellent", "robust", "pleased", "excited", "confident",
                 "improved", "healthy", "opportunities", "momentum", "resilient", "positive",
                 "growth", "delivered", "meaningfully", "achieved"}
_FALLBACK_NEG = {"weak", "declined", "decline", "impairment", "loss", "losses", "deteriorated",
                 "challenging", "difficult", "decreased", "adverse", "risk", "uncertain",
                 "litigation", "restructuring", "charge"}


def load_lm(path) -> tuple[set, set]:
    """Read the Loughran-McDonald CSV (columns 'Word', 'Negative', 'Positive'; nonzero = member)."""
    pos, neg = set(), set()
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            w = row["Word"].strip().lower()
            if row.get("Positive", "0").strip() not in ("", "0"):
                pos.add(w)
            if row.get("Negative", "0").strip() not in ("", "0"):
                neg.add(w)
    return pos, neg


@lru_cache(maxsize=1)
def lexicon() -> tuple[set, set, str]:
    """(positive, negative, source_label)."""
    path = os.environ.get("DISCLOSURE_LENS_LM_CSV")
    if not path:
        found = sorted((Path(__file__).resolve().parent.parent / "data").glob("Loughran-McDonald*.csv"))
        path = str(found[0]) if found else None
    if path and Path(path).exists():
        pos, neg = load_lm(path)
        return pos, neg, "Loughran-McDonald"
    return _FALLBACK_POS, _FALLBACK_NEG, "built-in placeholder"


def _is_negator(w: str) -> bool:
    return w in NEGATORS or w.endswith("n't")


def tone_matches(text: str) -> list[tuple[str, int]]:
    """Tone-lexicon hits in reading order as (label, +1/-1). A negated positive word
    ("not strong") is returned with -1 and the negator included in the label."""
    pos_set, neg_set, _ = lexicon()
    ws = [w.lower() for w in words(text)]
    hits = []
    for i, w in enumerate(ws):
        if w in pos_set:
            negators = [p for p in ws[max(0, i - NEGATION_WINDOW):i] if _is_negator(p)]
            if negators:
                hits.append((f"{negators[-1]} {w}", -1))
            else:
                hits.append((w, 1))
        elif w in neg_set:
            hits.append((w, -1))
    return hits


def tone_score(text: str) -> float:
    """Linguistic tone in [-1, 1] = (positive words - negative words) / total words, scaled."""
    n = len(words(text))
    if n == 0:
        return 0.0
    net = sum(sign for _, sign in tone_matches(text))
    return max(-1.0, min(1.0, SCALE * net / n))
