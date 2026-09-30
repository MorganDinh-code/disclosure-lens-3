"""Disclosure Lens. Run locally:  python3 -m streamlit run app.py"""
import streamlit as st

import ui

st.set_page_config(page_title="Disclosure Lens", page_icon="🔍", layout="wide")
ui.apply_theme()
ui.header()
pg = st.navigation([
    st.Page("views/analyze.py", title="Analyze", default=True),
    st.Page("views/methodology.py", title="Methodology"),
    st.Page("views/database.py", title="Database"),
], position="top")
pg.run()
