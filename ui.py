"""Shared look-and-feel and display helpers for the Streamlit pages."""
import streamlit as st


def apply_theme() -> None:
    st.markdown("""<style>
    .block-container {max-width: 1100px; padding-top: 1.5rem;}
    .dl-tagline {color: #667085; margin-top: -0.8rem; margin-bottom: 0.5rem;}
    </style>""", unsafe_allow_html=True)


def header() -> None:
    st.title("🔍 Disclosure Lens")
    st.markdown('<p class="dl-tagline">Where does a company put important information, and how is it worded?</p>',
                unsafe_allow_html=True)


def pct(x):
    return "n/a" if x is None else f"{x * 100:.0f}%"


def num(x):
    return "n/a" if x is None else f"{x:.2f}"


def render_profile(s: dict) -> None:
    """The three-module summary. Works for a fresh analysis or a stored database record."""
    st.markdown("#### Disclosure profile")
    st.caption(f"{s['n_sentences']} sentences · {s['n_material_neg']} material negatives · {s['n_positive']} positives")
    a, b, c = st.columns(3)
    with a:
        st.markdown("**Information order**")
        st.metric("Avg position, negatives", pct(s.get("mean_pos_negative")), help="0% = start of the document, 100% = end.")
        st.metric("Avg position, positives", pct(s.get("mean_pos_positive")))
        st.metric("Placement asymmetry", pct(s.get("placement_asymmetry")), help="Positive = bad news comes later than good news.")
        d = s.get("distance_from_headline")
        st.metric("Distance from headline", "n/a" if d is None else f"{d} sentences")
    with b:
        st.markdown("**Hedging**")
        st.metric("Hedging near negatives", pct(s.get("hedge_near_negative")), help="Share of words that are hedges in and around the bad-news sentences.")
        st.metric("Hedging near positives", pct(s.get("hedge_near_positive")))
        ha = s.get("hedging_asymmetry")
        if ha is not None:
            shown = f"{ha:.2f}x"
        else:
            shown = "undefined" if s.get("hedge_near_negative") else "n/a"
        st.metric("Hedging asymmetry", shown, help="Hedging near bad news divided by hedging near good news. 'Undefined' = no hedging near good news at all.")
    with c:
        st.markdown("**Tone vs. facts**")
        st.metric("Bad news in positive words", pct(s.get("framing_ratio")), help="Share of negative-fact sentences whose wording is net positive.")
        st.metric("Mean tone gap on bad news", num(s.get("mean_tone_gap_on_negatives")), help="Wording tone minus fact direction. Higher = more spin.")
