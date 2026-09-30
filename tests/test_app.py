"""Drive the real Streamlit pages: paste text + Analyze must work without touching the sample button."""
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PASTED = (ROOT / "data" / "sample_release.txt").read_text(encoding="utf-8")


def _analyze_app():
    return AppTest.from_file(str(ROOT / "views" / "analyze.py"), default_timeout=30)


def _button(at, label):
    return next(b for b in at.button if b.label == label)


def test_paste_then_analyze_without_sample_button():
    at = _analyze_app().run()
    at.text_area(key="doc_text").set_value(PASTED)
    _button(at, "Analyze").click().run()
    assert not at.exception
    assert at.session_state["result"]["summary"]["n_sentences"] > 5


def test_analyze_with_empty_box_warns():
    at = _analyze_app().run()
    _button(at, "Analyze").click().run()
    assert any("Paste some text" in w.value for w in at.warning)


def test_sample_button_only_fills_the_box():
    at = _analyze_app().run()
    _button(at, "Load sample press release").click().run()
    assert "Acme Corp." in at.session_state["doc_text"]
    assert "result" not in at.session_state


def test_database_and_methodology_pages_render():
    for page in ["database.py", "methodology.py"]:
        at = AppTest.from_file(str(ROOT / "views" / page), default_timeout=30).run()
        assert not at.exception, page


def test_full_app_with_navigation_paste_then_analyze():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not at.exception
    at.text_area(key="doc_text").set_value(PASTED)
    _button(at, "Analyze").click().run()
    assert not at.exception
    assert at.session_state["result"]["summary"]["n_material_neg"] >= 1
