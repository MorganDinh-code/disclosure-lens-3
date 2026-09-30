"""Analyze page: paste text -> click Analyze. A separate button loads the fictional sample."""
from pathlib import Path

import streamlit as st

import ui
from disclosure_lens import run
from disclosure_lens.hedges import hedge_matches
from disclosure_lens.tone import tone_matches

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_release.txt"
FACT = {1: "🟢", -1: "🔴", 0: "⚪"}

st.session_state.setdefault("doc_text", "")


def _load_sample() -> None:
    st.session_state["doc_text"] = SAMPLE.read_text(encoding="utf-8")
    st.session_state.pop("result", None)


def _clear() -> None:
    st.session_state["doc_text"] = ""
    st.session_state.pop("result", None)


st.subheader("Analyze a disclosure")
st.text_area("Paste the text of an earnings press release (narrative only, no financial tables)",
             key="doc_text", height=260)
st.checkbox("Remove legal 'forward-looking statements' boilerplate", value=True, key="strip_bp")

c1, c2, c3, _ = st.columns([1, 2, 1, 4])
analyze_clicked = c1.button("Analyze", type="primary")
c2.button("Load sample press release", on_click=_load_sample, help="Fills the box with a fictional Acme Corp. release.")
c3.button("Clear", on_click=_clear)

if analyze_clicked:
    text = st.session_state["doc_text"].strip()
    if not text:
        st.warning("Paste some text first (or click 'Load sample press release').")
        st.session_state.pop("result", None)
    else:
        st.session_state["result"] = run(text, strip=st.session_state["strip_bp"])

result = st.session_state.get("result")
if result:
    records = result["records"]
    for w in result["warnings"]:
        st.warning(w)
    if result["n_boilerplate_removed"]:
        st.info(f"Removed {result['n_boilerplate_removed']} legal 'forward-looking statements' block(s) before analysis.")

    ui.render_profile(result["summary"])

    st.markdown("#### Disclosure map")
    st.caption("Fact: does the event help 🟢 or hurt 🔴 the company? Tone: how positive or negative the wording is.")
    rows = []
    for r in records:
        tone = "🟢" if r["tone"] > 0.05 else "🔴" if r["tone"] < -0.05 else "⚪"
        rows.append({
            "#": r["index"],
            "Sentence": r["text"],
            "Fact": FACT[r["direction"]] + (" material" if r["material_neg"] else ""),
            "Tone": tone,
            "Hedge %": round(r["hedge_density"] * 100, 1),
            "Flag": "Spin?" if r["direction"] == -1 and r["tone"] > 0 else "",
        })
    st.dataframe(rows, hide_index=True)

    with st.expander("Which words drove these scores? (lexicon matches)"):
        st.caption(f"Hedge terms are shown with their tier. Tone words come from the {result['tone_lexicon']} list. "
                   "The full lists and sources are on the Methodology page.")
        try:
            st.page_link("views/methodology.py", label="Open the Methodology page")
        except Exception:  # page not registered (e.g. this file run on its own)
            pass
        word_rows = []
        for r in records:
            hedges = ", ".join(f"{t} ({tier})" for t, tier in hedge_matches(r["text"]))
            hits = tone_matches(r["text"])
            pos = ", ".join(w for w, s in hits if s > 0)
            neg = ", ".join(w for w, s in hits if s < 0)
            if hedges or pos or neg:
                word_rows.append({"#": r["index"], "Hedge terms (tier)": hedges,
                                  "Positive tone words": pos, "Negative tone words": neg})
        st.dataframe(word_rows, hide_index=True) if word_rows else st.write("No lexicon matches found.")
else:
    st.caption("Tip: click **Load sample press release** to see what a result looks like, then paste your own text and click **Analyze**.")
