"""Methodology page: how it works and the exact word lists, tiers and sources behind every score."""
import streamlit as st

from disclosure_lens import lexicon_info as li
from disclosure_lens.classify import ADJ, COST, DOWN, UP
from disclosure_lens.tone import lexicon

st.subheader("Methodology")
st.markdown("""
Disclosure Lens reads a company disclosure sentence by sentence and measures three things.

1. **Information order.** Where do the important bad-news sentences sit compared with the good news?
   Position = sentence number / total sentences.
2. **Hedging.** How much uncertain language surrounds bad news versus good news (the sentence plus one neighbour each side)?
3. **Tone vs. facts.** Is bad news described in positive words? The *fact* (helps or hurts the company) is judged
   separately from the *wording* (positive or negative language).
""")

st.markdown("### Word lists and where they come from")
tab_hedge, tab_tone, tab_fact, tab_lookup = st.tabs(["Hedging tiers", "Tone words", "Financial direction", "Look up a word"])

with tab_hedge:
    st.markdown(f"**Source.** {li.HEDGE_SOURCE}")
    st.markdown("**Hedge density** = (low + moderate terms) / total words. High-certainty words are not hedges; "
                "they only feed the *modal intensity* score (1 = very uncertain, 3 = very certain).")
    for tier, label, terms, meaning, is_hedge in li.HEDGE_TIERS:
        badge = "counts as a hedge" if is_hedge else "not a hedge"
        st.markdown(f"**{label}** ({badge}). {meaning}")
        st.code(", ".join(terms), language=None)
    st.caption('"may" followed by a number (for example "May 5") is treated as a month, not a hedge.')

with tab_tone:
    pos, neg, src = lexicon()
    st.markdown(f"**Source.** {li.TONE_SOURCE}")
    st.markdown(f"**In use right now:** {src} ({len(pos):,} positive words, {len(neg):,} negative words).")
    if src != "Loughran-McDonald":
        st.warning("The built-in placeholder list is active. Add the Loughran-McDonald CSV (see the README) "
                   "for the full financial dictionary.")
    st.markdown("**Tone score** = (positive words - negative words) / total words, scaled to between -1 and +1. "
                "A positive word right after a negation (not, no, never, without...) counts as negative.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("Positive words" + (" (first 80)" if len(pos) > 80 else ""))
        st.code(", ".join(sorted(pos)[:80]), language=None)
    with c2:
        st.markdown("Negative words" + (" (first 80)" if len(neg) > 80 else ""))
        st.code(", ".join(sorted(neg)[:80]), language=None)

with tab_fact:
    st.markdown("Financial direction asks whether the **event** helps or hurts the company, whatever the wording. "
                "A sentence is a **material negative** if it is bad news *and* has a quantified figure "
                "(%, $, million...) or a severe term.")
    st.markdown("**Bad-news terms**")
    st.code(", ".join(li.NEGATIVE_EVENT_TERMS), language=None)
    st.markdown("**Good-news terms**")
    st.code(", ".join(li.POSITIVE_EVENT_TERMS), language=None)
    st.markdown("**Trend words.** Downward: " + ", ".join(sorted(DOWN)) + ". Upward: " + ", ".join(sorted(UP)) + ".")
    st.markdown("**Cost-type words** flip a trend word, so \"expenses declined\" is good news and \"debt increased\" is bad news: "
                + ", ".join(sorted(COST)) + ".")
    st.markdown("**Severe terms** (make a negative material even without a number): " + ", ".join(li.SEVERE_TERMS) + ".")

with tab_lookup:
    w = st.text_input("Type a word to see which lists it belongs to", key="lookup_word")
    if w.strip():
        found = li.lookup_word(w)
        if found:
            for line in found:
                st.write("• " + line)
        else:
            st.write("That word is not in any list.")

st.markdown("### Limitations")
st.markdown("""
- The rules are word-list based, so they miss sarcasm, context and unusual phrasing.
- The financial-direction rules have not yet been checked against a hand-labeled sample.
- Works best on short narrative documents such as earnings press releases, not full 10-Ks or tables.
- These are descriptive measures of *how* something is disclosed, not evidence of intent or wrongdoing.
""")
