"""Financial direction: does the FACT help or hurt the company? (separate from tone)

Rule-based. Compared with the first version this handles:
  * whole-word matching ("loss" no longer fires inside "gloss", "up " inside "backup")
  * cost-type subjects: "expenses declined" is GOOD news, "debt increased" is BAD news
  * "record" as a verb ("may record a charge") vs. as a good-news adjective ("record revenue")
  * materiality needs a real quantified figure (%, $, million...), not any digit like "Q3"
Still unvalidated until you compare it with a hand-labeled sample.
"""
import re

_TOKEN = re.compile(r"[a-z']+|\d[\d,.]*%?")

DOWN = {"declined", "decline", "declining", "decreased", "decrease", "decreasing", "fell",
        "dropped", "lower", "reduced", "reduction", "down"}
UP = {"increased", "increase", "increasing", "grew", "rose", "higher", "up", "expanded", "improved"}
COST = {"expense", "expenses", "cost", "costs", "spending", "debt", "liabilities", "liability", "churn"}
ADJ = {"lower", "higher", "reduced"}          # modifiers that come BEFORE their noun ("lower costs")
NEEDS_NUMBER = {"up", "down"}                 # "up 5%" is a trend; "set up a team" is not
NOT_A_NOUN_BEFORE_RECORD = {"to", "may", "might", "could", "will", "would", "should",
                            "potentially", "also", "we", "not"}

# Facts that are bad news regardless of direction words.
_NEG_EVENTS = re.compile(
    r"\b(impairments?|loss(?:es)?|lowered|(?:lower|reduced|cut) guidance|restructuring|litigation|"
    r"restatements?|going concern|covenant (?:breach|violation|waiver|default)|layoffs|"
    r"weak(?:er|ness)?|deteriorat\w*|shortfalls?|write-?downs?|write-?offs?|missed)\b")
_POS_EVENTS = re.compile(r"\b(exceeded|outperform\w*|beat expectations)\b")
_SEVERE = re.compile(
    r"\b(impairments?|going concern|litigation|restatements?|covenant (?:breach|violation|waiver|default)|"
    r"restructuring|layoffs|lowered|(?:lower|reduced|cut) guidance|write-?downs?)\b")
_QUANTIFIED = re.compile(
    r"\$\s?\d|\d[\d,.]*\s?(?:%|percent\b|million\b|billion\b|bn\b|mn\b|bps\b|basis points\b)", re.I)


def _trend_counts(tokens: list[str]) -> tuple[int, int]:
    neg = pos = 0
    for i, tok in enumerate(tokens):
        if tok in DOWN:
            sign = -1
        elif tok in UP:
            sign = 1
        else:
            continue
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        if tok in NEEDS_NUMBER and not nxt[:1].isdigit():
            continue
        window = tokens[max(0, i - 5):i] + (tokens[i + 1:i + 3] if tok in ADJ else [])
        if any(t in COST for t in window):
            sign = -sign                      # falling costs are good, rising costs are bad
        neg, pos = (neg + 1, pos) if sign < 0 else (neg, pos + 1)
    return neg, pos


def _record_adjective(tokens: list[str]) -> int:
    n = 0
    for i, tok in enumerate(tokens):
        if tok == "record" and (i == 0 or tokens[i - 1] not in NOT_A_NOUN_BEFORE_RECORD):
            n += 1
    return n


def _scores(text: str) -> tuple[int, int]:
    t = text.lower()
    tokens = _TOKEN.findall(t)
    neg, pos = _trend_counts(tokens)
    neg += len(_NEG_EVENTS.findall(t))
    pos += len(_POS_EVENTS.findall(t)) + _record_adjective(tokens)
    return neg, pos


def direction(text: str) -> int:
    """+1 positive fact, -1 negative fact, 0 neutral. Negative wins ties (conservative)."""
    neg, pos = _scores(text)
    if neg and neg >= pos:
        return -1
    return 1 if pos else 0


def is_material_negative(text: str) -> bool:
    """Material = negative AND (contains a quantified figure OR a severe term)."""
    if direction(text) != -1:
        return False
    t = text.lower()
    return bool(_QUANTIFIED.search(t) or _SEVERE.search(t))
