"""The Database: one JSON file per analyzed document in database/records/.

Owner workflow: python add_to_database.py --help   (or the optional owner form on the Database page)
"""
import json
import re
from datetime import date, datetime
from pathlib import Path

from .pipeline import run
from .taxonomy import FILING_TYPES, SECTORS

DB_DIR = Path(__file__).resolve().parent.parent / "database"
REQUIRED = ["company", "sector", "filing_type", "period", "date"]


def records_dir() -> Path:
    return DB_DIR / "records"


def validate_meta(meta: dict, demo: bool = False) -> dict:
    """Return a cleaned copy of meta or raise ValueError with a plain-English message."""
    m = {k: (str(v).strip() if v is not None else "") for k, v in meta.items()}
    for k in REQUIRED:
        if not m.get(k):
            raise ValueError(f"Missing required field: {k}")
    if not demo and m["sector"] not in SECTORS:
        raise ValueError(f"Unknown sector '{m['sector']}'. Choose one of: {', '.join(SECTORS)}")
    if not demo and m["filing_type"] not in FILING_TYPES:
        raise ValueError(f"Unknown filing type '{m['filing_type']}'. Choose one of: {', '.join(FILING_TYPES)}")
    try:
        datetime.strptime(m["date"], "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Date must look like 2026-08-26 (got '{m['date']}')") from None
    m.setdefault("ticker", "")
    m.setdefault("source_url", "")
    m["ticker"] = m["ticker"].upper()
    return m


def record_id(meta: dict) -> str:
    base = f"{meta.get('ticker') or meta['company']}-{meta['period']}-{meta['filing_type']}"
    return re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")


def make_record(text: str, meta: dict, strip: bool = True, demo: bool = False) -> dict:
    m = validate_meta(meta, demo=demo)
    result = run(text, strip=strip)
    return {
        "id": record_id(m),
        "company": m["company"], "ticker": m["ticker"], "sector": m["sector"],
        "filing_type": m["filing_type"], "period": m["period"], "date": m["date"],
        "source_url": m["source_url"], "demo": demo,
        "summary": result["summary"],
        "sentences": [{"d": r["direction"], "m": r["material_neg"],
                       "t": round(r["tone"], 2), "h": round(r["hedge_density"], 3)}
                      for r in result["records"]],
        "boilerplate_removed": result["n_boilerplate_removed"],
        "tone_lexicon": result["tone_lexicon"],
        "added": date.today().isoformat(),
    }


def save_record(record: dict) -> Path:
    """Write the record; adding the same company/period/type again replaces the old one."""
    d = records_dir()
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{record['id']}.json"
    path.write_text(json.dumps(record, indent=1), encoding="utf-8")
    return path


def load_all() -> list[dict]:
    out = []
    for p in sorted(records_dir().glob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rec.setdefault("id", p.stem)
        out.append(rec)
    return out


def remove_record(rec_id: str) -> bool:
    p = records_dir() / f"{rec_id}.json"
    if p.exists():
        p.unlink()
        return True
    return False
