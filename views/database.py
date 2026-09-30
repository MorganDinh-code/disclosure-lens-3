"""Database page: browse analyzed disclosures by sector and document type."""
import os
from datetime import date

import pandas as pd
import streamlit as st

import ui
from disclosure_lens import store
from disclosure_lens.taxonomy import FILING_TYPES, SECTORS

st.subheader("Database")
records = store.load_all()

# ---------------- filters ----------------
show_demo = st.checkbox("Include the fictional demo (Acme Corp.)", value=True)
rows = [r for r in records if show_demo or not r.get("demo")]

f1, f2, f3 = st.columns([2, 2, 2])
sector_opts = [s for s in SECTORS if any(r["sector"] == s for r in rows)]
sector_opts += sorted({r["sector"] for r in rows} - set(sector_opts))          # e.g. "Illustrative"
type_opts = [t for t in FILING_TYPES if any(r["filing_type"] == t for r in rows)]
type_opts += sorted({r["filing_type"] for r in rows} - set(type_opts))
sel_sectors = f1.multiselect("Sector", sector_opts, placeholder="All sectors")
sel_types = f2.multiselect("Document type", type_opts, placeholder="All document types")
query = f3.text_input("Search company or ticker").strip().lower()

view = [r for r in rows
        if (not sel_sectors or r["sector"] in sel_sectors)
        and (not sel_types or r["filing_type"] in sel_types)
        and (not query or query in r["company"].lower() or query in r.get("ticker", "").lower())]

# ---------------- table ----------------
if not records:
    st.info("The database is empty. The site owner can add documents (see the README, 'Adding documents').")
elif not view:
    st.info("No documents match these filters.")
else:
    table = pd.DataFrame([{
        "Company": r["company"], "Ticker": r.get("ticker", ""), "Sector": r["sector"],
        "Document type": r["filing_type"], "Period": r["period"], "Date": r["date"],
        "Sentences": r["summary"]["n_sentences"],
        "Material negatives": r["summary"]["n_material_neg"],
        "Placement asymmetry": r["summary"].get("placement_asymmetry"),
        "Bad news in positive words": r["summary"].get("framing_ratio"),
    } for r in view])
    st.caption(f"{len(view)} document(s). Click a row to see its full profile.")
    event = st.dataframe(
        table, hide_index=True, on_select="rerun", selection_mode="single-row",
        column_config={
            "Placement asymmetry": st.column_config.NumberColumn(format="percent",
                help="Positive = bad news placed later than good news."),
            "Bad news in positive words": st.column_config.NumberColumn(format="percent"),
        })

    picked = event.selection.rows
    if picked:
        rec = view[picked[0]]
        st.markdown(f"### {rec['company']}" + (f" ({rec['ticker']})" if rec.get("ticker") else ""))
        st.caption(f"{rec['sector']} · {rec['filing_type']} · {rec['period']} · {rec['date']}"
                   + (" · fictional demo" if rec.get("demo") else ""))
        if rec.get("source_url"):
            st.link_button("Open original document", rec["source_url"])
        ui.render_profile(rec["summary"])
        strip = "".join(("🔴" if s["m"] else {1: "🟢", -1: "🟠", 0: "⚪"}[s["d"]]) for s in rec["sentences"])
        st.markdown("**Disclosure map, start to end of document**")
        st.write(strip)
        st.caption("🟢 good-news fact · 🔴 material bad news · 🟠 other bad news · ⚪ neutral")

    # sector comparison
    by_sector = pd.DataFrame([{"Sector": r["sector"], "asym": r["summary"].get("placement_asymmetry")}
                              for r in view if r["summary"].get("placement_asymmetry") is not None])
    if not by_sector.empty and by_sector["Sector"].nunique() > 1:
        st.markdown("#### Average placement asymmetry by sector")
        st.bar_chart(by_sector.groupby("Sector")["asym"].mean())

# ---------------- owner tools ----------------
def _admin_password() -> str:
    try:
        return st.secrets.get("ADMIN_PASSWORD", "") or os.environ.get("ADMIN_PASSWORD", "")
    except Exception:
        return os.environ.get("ADMIN_PASSWORD", "")


st.divider()
pw = _admin_password()
with st.expander("Site owner: add a document"):
    if not pw:
        st.write("Owner form is off. Set an `ADMIN_PASSWORD` (environment variable or `.streamlit/secrets.toml`) "
                 "to turn it on, or use `python add_to_database.py` from the command line (see the README).")
    elif st.text_input("Owner password", type="password", key="admin_pw") != pw:
        st.caption("Enter the owner password to add documents.")
    else:
        with st.form("add_doc", clear_on_submit=False):
            up = st.file_uploader("Document text file (.txt)", type=["txt"])
            pasted = st.text_area("...or paste the text", height=140)
            a, b = st.columns(2)
            company = a.text_input("Company")
            ticker = b.text_input("Ticker")
            sector = a.selectbox("Sector", SECTORS)
            ftype = b.selectbox("Document type", FILING_TYPES)
            period = a.text_input("Period (e.g. Q2 FY2027)")
            d = b.date_input("Document date", value=date.today())
            url = st.text_input("Link to the original (optional)")
            go = st.form_submit_button("Analyze and add", type="primary")
        if go:
            text = up.getvalue().decode("utf-8", errors="replace") if up else pasted
            if not text.strip():
                st.error("Upload a .txt file or paste the text.")
            else:
                try:
                    rec = store.make_record(text, {"company": company, "ticker": ticker, "sector": sector,
                                                   "filing_type": ftype, "period": period,
                                                   "date": d.isoformat(), "source_url": url})
                    store.save_record(rec)
                    st.success(f"Added {rec['company']} · {rec['period']}. Reload the page to see it in the table.")
                    st.caption("Note: on hosts with a temporary disk (such as Streamlit Community Cloud) records added "
                               "here can disappear on redeploy. For permanent records use add_to_database.py "
                               "and commit the database/ folder.")
                except ValueError as e:
                    st.error(str(e))
