"""Step 1: turn raw text into paragraphs and sentences, with position information."""
import re

# A period after these never ends a sentence (titles, corporate suffixes, "vs.", ...).
_ABBREV = re.compile(r"(?<![A-Za-z])(Inc|Corp|Co|Ltd|approx|vs|No|Mr|Ms|Mrs|Dr|St)\.")
# Dotted initialisms: U.S., U.K., e.g., i.e.
_INITIALISM = re.compile(r"(?<![A-Za-z])(?:[A-Za-z]\.){2,}")
_DOT = "\x00"

# Split after . ! ? (optionally followed by a closing quote/bracket) when the next
# token starts with a capital letter, quote, bracket or $.
# Units such as "bn." / "mn." are deliberately NOT protected, so
# "sales of $1.2 bn. The market ..." splits correctly.
_SPLIT = re.compile(r"(?:(?<=[.!?])|(?<=[.!?][\"”)]))\s+(?=[A-Z\"“($])")


def split_paragraphs(text: str) -> list[str]:
    """Paragraphs are separated by blank lines."""
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def split_sentences(paragraph: str) -> list[str]:
    para = re.sub(r"\s+", " ", paragraph).strip()  # un-wrap hard line breaks
    para = _ABBREV.sub(lambda m: m.group(1) + _DOT, para)
    para = _INITIALISM.sub(lambda m: m.group(0).replace(".", _DOT), para)
    return [p.replace(_DOT, ".").strip() for p in _SPLIT.split(para) if p.strip()]


def parse_document(text: str) -> list[dict]:
    """One record per sentence. Position = sentence number / total sentences (1-indexed)."""
    records = []
    for p_idx, para in enumerate(split_paragraphs(text), start=1):
        sentences = split_sentences(para)
        for s_idx, sent in enumerate(sentences, start=1):
            records.append({"text": sent, "paragraph": p_idx,
                            "sent_in_para": s_idx, "sents_in_para": len(sentences)})
    total = len(records)
    for i, r in enumerate(records, start=1):
        r["index"] = i
        r["pos_doc"] = i / total
        r["pos_para"] = r["sent_in_para"] / r["sents_in_para"]
    return records
