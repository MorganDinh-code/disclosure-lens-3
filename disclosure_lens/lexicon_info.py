"""Human-readable description of every word list the tool uses (drives the Methodology page).

Edit the source strings below to change what the site tells readers.
"""
from .classify import ADJ, COST, DOWN, UP
from .hedges import HIGH, LOW, MODERATE
from .tone import lexicon

TONE_SOURCE = ("Loughran, T. and McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, "
               "Dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. Dictionary: Notre Dame Software "
               "Repository for Accounting and Finance (sraf.nd.edu).")

# Replace this with the exact citation for the tier list you are using.
HEDGE_SOURCE = ("Three-tier certainty lexicon defined in disclosure_lens/hedges.py (low / moderate / high). "
                "It follows the same idea as the Weak Modal and Strong Modal word categories in the "
                "Loughran-McDonald dictionary: words that signal how firmly a claim is made.")

HEDGE_TIERS = [
    ("low", "Low certainty (strong hedge)", LOW,
     "The writer attaches real uncertainty or a condition to the statement.", True),
    ("moderate", "Moderate certainty (soft hedge)", MODERATE,
     "The statement is framed as a belief, expectation or approximation.", True),
    ("high", "High certainty", HIGH,
     "Firm, definite language. NOT counted as a hedge; only used for the modal-intensity score.", False),
]

# Readable versions of the patterns in classify.py (a test checks each one really is read as bad news).
NEGATIVE_EVENT_TERMS = ["impairment", "loss", "lowered", "lower guidance", "reduced guidance", "cut guidance",
                        "restructuring", "litigation", "restatement", "going concern", "covenant breach",
                        "covenant violation", "covenant waiver", "covenant default", "layoffs", "weak",
                        "weaker", "weakness", "deteriorated", "shortfall", "write-down", "write-off", "missed"]
POSITIVE_EVENT_TERMS = ["exceeded", "outperformed", "beat expectations", "record (as an adjective)"]
SEVERE_TERMS = ["impairment", "going concern", "litigation", "restatement", "covenant breach/violation/waiver/default",
                "restructuring", "layoffs", "lowered", "lower/reduced/cut guidance", "write-down"]


def lookup_word(word: str) -> list[str]:
    """Which lists is this word in? (empty list = in none of them)"""
    w = word.strip().lower()
    out = []
    if not w:
        return out
    for tier, label, terms, _, is_hedge in HEDGE_TIERS:
        if w in terms:
            out.append(f"Hedging: {label}" + ("" if is_hedge else " (not counted as a hedge)"))
    pos, neg, src = lexicon()
    if w in pos:
        out.append(f"Tone: positive word ({src})")
    if w in neg:
        out.append(f"Tone: negative word ({src})")
    if w in DOWN:
        out.append("Financial direction: downward-trend word (bad news, unless it describes a cost)")
    if w in UP:
        out.append("Financial direction: upward-trend word (good news, unless it describes a cost)")
    if w in COST:
        out.append("Financial direction: cost-type word (flips the meaning of a nearby trend word)")
    if w in NEGATIVE_EVENT_TERMS:
        out.append("Financial direction: bad-news term")
    if w in POSITIVE_EVENT_TERMS:
        out.append("Financial direction: good-news term")
    return out
