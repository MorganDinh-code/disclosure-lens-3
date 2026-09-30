from pathlib import Path

import pytest

from disclosure_lens import store
from disclosure_lens.taxonomy import FILING_TYPES, SECTORS

SAMPLE = (Path(__file__).resolve().parent.parent / "data" / "sample_release.txt").read_text(encoding="utf-8")
META = {"company": "Acme Corp.", "ticker": "acme", "sector": "Industrials",
        "filing_type": "Earnings press release", "period": "Q3 FY2026", "date": "2026-09-30"}


def test_make_record_has_expected_shape():
    rec = store.make_record(SAMPLE, META)
    assert rec["id"] == "acme-q3-fy2026-earnings-press-release"
    assert rec["ticker"] == "ACME"
    assert rec["summary"]["n_sentences"] == len(rec["sentences"])
    assert set(rec["sentences"][0]) == {"d", "m", "t", "h"}


def test_save_load_replace_remove(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB_DIR", tmp_path)
    rec = store.make_record(SAMPLE, META)
    store.save_record(rec)
    store.save_record(rec)                      # same id again -> replaces, no duplicate
    assert len(store.load_all()) == 1
    assert store.remove_record(rec["id"]) and store.load_all() == []


@pytest.mark.parametrize("bad, msg", [
    ({"sector": "Tech"}, "Unknown sector"),
    ({"filing_type": "Tweet"}, "Unknown filing type"),
    ({"date": "26/08/2026"}, "Date must look like"),
    ({"company": ""}, "Missing required field: company"),
])
def test_validation_messages(bad, msg):
    with pytest.raises(ValueError, match=msg):
        store.make_record(SAMPLE, {**META, **bad})


def test_taxonomy_is_sane():
    assert "Industrials" in SECTORS and "Financials" in SECTORS and "Information Technology" in SECTORS
    assert "Earnings press release" in FILING_TYPES
