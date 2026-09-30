from pathlib import Path

from disclosure_lens import run
from disclosure_lens.checks import strip_boilerplate

SAMPLE = (Path(__file__).resolve().parent.parent / "data" / "sample_release.txt").read_text(encoding="utf-8")


def test_sample_runs_and_finds_material_negatives():
    result = run(SAMPLE)
    s = result["summary"]
    assert s["n_sentences"] > 5
    assert s["n_material_neg"] >= 1
    assert s["distance_from_headline"] >= 0
    assert 0 <= s["first_negative_pos"] <= 1


def test_strip_boilerplate_keeps_normal_paragraphs():
    legal = ("This release contains forward-looking statements within the meaning of the Private "
             "Securities Litigation Reform Act, and actual results may differ materially from those "
             "expressed or implied by such statements.")
    text = "Revenue grew.\n\n" + legal + "\n\nMargins improved."
    clean, n = strip_boilerplate(text)
    assert n == 1 and "forward-looking" not in clean and "Margins improved." in clean
