# Disclosure Lens

Analyzes where a company places important information in a disclosure and how it is worded:
information order, hedging, and tone vs. financial facts.

## Run it
```
python analyze.py data/sample_release.txt            # text report
python analyze.py data/sample_release.txt --json     # machine-readable
python -m streamlit run app.py                       # web app
```

## Test it
```
pip install pytest
pytest
```

## Using the web app
- **Analyze page:** paste text, click **Analyze**. **Load sample press release** only fills the box with the
  fictional Acme Corp. release; it never runs the analysis by itself.
- **Methodology page:** every word list, hedge tier, tone source and financial-direction rule, plus a
  "look up a word" box. Edit the source citations in `disclosure_lens/lexicon_info.py`.
- **Database page:** browse analyzed disclosures, filter by sector and document type.

## Adding documents to the Database (owner guide)
1. Save the narrative text of the release as a `.txt` file (no financial tables).
2. Run:
   ```
   python add_to_database.py releases/nvda_q2_fy27.txt --company "NVIDIA" --ticker NVDA \
       --sector "Information Technology" --type "Earnings press release" \
       --period "Q2 FY2027" --date 2026-08-26 --url "https://..."
   ```
3. To add many at once, fill a spreadsheet with the columns
   `file,company,ticker,sector,filing_type,period,date,source_url`, save it as CSV, and run
   `python add_to_database.py --manifest releases/manifest.csv`. Bad rows are skipped with a message.
4. Publish: commit the `database/` folder and push (or redeploy). Records live in `database/records/`.

Handy: `--sectors` lists the allowed sectors and document types, `--list` shows what is stored,
`--remove <id>` deletes a record. Re-adding the same company + period + type replaces the old record.
To add a new sector or document type, edit the lists in `disclosure_lens/taxonomy.py`.

Optional in-app form: set `ADMIN_PASSWORD` (environment variable or `.streamlit/secrets.toml`) and an
owner form appears at the bottom of the Database page. On hosts with a temporary disk (such as Streamlit
Community Cloud) records added that way can vanish on redeploy, so prefer the command line for permanent records.

## Project layout
- `disclosure_lens/preprocess.py`: paragraphs, sentences, positions
- `disclosure_lens/classify.py`: financial direction + materiality (rule-based, needs validation)
- `disclosure_lens/hedges.py`: tiered hedge lexicon, density, modal intensity
- `disclosure_lens/tone.py`: tone score (Loughran-McDonald if the CSV is present, else placeholder list)
- `disclosure_lens/metrics.py`: headline metrics
- `disclosure_lens/checks.py`: input warnings and boilerplate stripping
- `disclosure_lens/pipeline.py`: `run(text)` does everything in one call
- `disclosure_lens/taxonomy.py`: allowed sectors (GICS) and document types
- `disclosure_lens/lexicon_info.py`: descriptions and sources of every word list (Methodology page)
- `disclosure_lens/store.py`: reads and writes `database/records/*.json`
- `analyze.py`: command-line report
- `add_to_database.py`: owner tool for the Database page
- `app.py`, `ui.py`, `views/`: the Streamlit site

## Loughran-McDonald dictionary
Download the master dictionary CSV from Notre Dame's SRAF and either put it in `data/`
(filename starting `Loughran-McDonald`) or set `DISCLOSURE_LENS_LM_CSV=/path/to/file.csv`.

## Still to do
- Hand-label ~200 sentences and measure how accurate `classify.py` really is
- Tune `SCALE` in `tone.py` once the real lexicon is loaded
