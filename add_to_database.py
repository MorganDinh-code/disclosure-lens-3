"""Owner tool: add documents to the Database page.

ONE document:
  python add_to_database.py releases/nvda_q2_fy27.txt --company "NVIDIA" --ticker NVDA \\
      --sector "Information Technology" --type "Earnings press release" \\
      --period "Q2 FY2027" --date 2026-08-26 --url "https://..."

MANY documents at once (a spreadsheet saved as CSV):
  python add_to_database.py --manifest releases/manifest.csv
  Columns: file,company,ticker,sector,filing_type,period,date,source_url
  ("file" is relative to the CSV's folder)

Other:
  python add_to_database.py --list            show what is in the database
  python add_to_database.py --remove <id>     delete one record
  python add_to_database.py --sectors         show the allowed sectors and document types
"""
import argparse
import csv
import sys
from pathlib import Path

from disclosure_lens import store
from disclosure_lens.taxonomy import FILING_TYPES, SECTORS


def add_one(path: Path, meta: dict, strip: bool, demo: bool = False) -> None:
    text = path.read_text(encoding="utf-8")
    rec = store.make_record(text, meta, strip=strip, demo=demo)
    out = store.save_record(rec)
    s = rec["summary"]
    print(f"  saved {out.name}: {rec['company']} | {rec['sector']} | {rec['filing_type']} | {rec['period']} "
          f"({s['n_sentences']} sentences, {s['n_material_neg']} material negatives)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Add documents to the Disclosure Lens database.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("file", nargs="?", help="text file of the document")
    ap.add_argument("--manifest", help="CSV listing many documents")
    ap.add_argument("--company"); ap.add_argument("--ticker", default="")
    ap.add_argument("--sector"); ap.add_argument("--type", dest="filing_type")
    ap.add_argument("--period"); ap.add_argument("--date"); ap.add_argument("--url", default="")
    ap.add_argument("--keep-boilerplate", action="store_true")
    ap.add_argument("--demo", action="store_true", help="mark as illustrative/fictional (skips sector check)")
    ap.add_argument("--list", action="store_true"); ap.add_argument("--remove"); ap.add_argument("--sectors", action="store_true")
    a = ap.parse_args()

    if a.sectors:
        print("Sectors:\n  " + "\n  ".join(SECTORS) + "\n\nDocument types:\n  " + "\n  ".join(FILING_TYPES))
        return 0
    if a.list:
        for r in store.load_all():
            print(f"{r['id']:<45} {r['company']:<20} {r['sector']:<24} {r['filing_type']:<24} {r['period']}")
        return 0
    if a.remove:
        print("removed" if store.remove_record(a.remove) else "no such id (use --list)")
        return 0

    strip = not a.keep_boilerplate
    failures = 0
    try:
        if a.manifest:
            base = Path(a.manifest).parent
            with open(a.manifest, encoding="utf-8-sig", newline="") as f:
                for n, row in enumerate(csv.DictReader(f), start=2):
                    try:
                        add_one(base / row["file"].strip(), row, strip)
                    except (ValueError, OSError, KeyError) as e:
                        failures += 1
                        print(f"  row {n} skipped: {e}")
        elif a.file:
            meta = {"company": a.company, "ticker": a.ticker, "sector": a.sector,
                    "filing_type": a.filing_type, "period": a.period, "date": a.date, "source_url": a.url}
            add_one(Path(a.file), meta, strip, demo=a.demo)
        else:
            ap.print_help()
            return 1
    except (ValueError, OSError) as e:
        print(f"Error: {e}")
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
