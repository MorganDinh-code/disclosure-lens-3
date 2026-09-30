"""One call that runs the whole analysis (used by the CLI and the Streamlit app)."""
from .checks import check_document, strip_boilerplate
from .metrics import annotate, summarize
from .preprocess import parse_document
from .tone import lexicon


def run(text: str, strip: bool = True) -> dict:
    """Return {'records', 'summary', 'warnings', 'n_boilerplate_removed', 'tone_lexicon'}."""
    n_removed = 0
    if strip:
        text, n_removed = strip_boilerplate(text)
    records = annotate(parse_document(text))
    return {
        "records": records,
        "summary": summarize(records),
        "warnings": check_document(text),
        "n_boilerplate_removed": n_removed,
        "tone_lexicon": lexicon()[2],
    }
