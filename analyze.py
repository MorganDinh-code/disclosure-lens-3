"""Run Disclosure Lens on a text file.

    python analyze.py data/sample_release.txt
    python analyze.py data/sample_release.txt --json > result.json
    python analyze.py data/sample_release.txt --keep-boilerplate
"""
import argparse
import json
import sys

from disclosure_lens import run

ICON = {1: "🟢", -1: "🔴", 0: "⚪"}


def fmt(x, pct=False):
    if x is None:
        return "n/a"
    return f"{x * 100:.0f}%" if pct else f"{x:.2f}"


def print_report(result: dict) -> None:
    records, s = result["records"], result["summary"]
    for w in result["warnings"]:
        print(f"WARNING: {w}\n")
    if result["n_boilerplate_removed"]:
        print(f"(Removed {result['n_boilerplate_removed']} legal 'forward-looking statements' block(s).)")
    print(f"(Tone lexicon: {result['tone_lexicon']})")

    print("\n=== DISCLOSURE MAP (text version) ===\n")
    for r in records:
        tone_icon = "🟢" if r["tone"] > 0.05 else "🔴" if r["tone"] < -0.05 else "⚪"
        flag = "  <-- SPIN?" if r["direction"] == -1 and r["tone"] > 0 else ""
        mat = " [MATERIAL]" if r["material_neg"] else ""
        print(f"{r['index']:>2}. fact {ICON[r['direction']]}  tone {tone_icon}  "
              f"hedge {r['hedge_density'] * 100:4.1f}%{mat}{flag}")
        print(f"    {r['text'][:90]}")

    print("\n=== DISCLOSURE PROFILE ===\n")
    print(f"Sentences: {s['n_sentences']}  (material negatives: {s['n_material_neg']}, positives: {s['n_positive']})")
    print("\nINFORMATION ORDER")
    print(f"  Avg position, negatives : {fmt(s.get('mean_pos_negative'), True)}")
    print(f"  Avg position, positives : {fmt(s.get('mean_pos_positive'), True)}")
    print(f"  Placement asymmetry     : {fmt(s.get('placement_asymmetry'), True)} (positive = bad news later)")
    print(f"  Distance from headline  : {s.get('distance_from_headline', 'n/a')} sentences")
    print("\nHEDGING")
    print(f"  Near negatives          : {fmt(s.get('hedge_near_negative'), True)}")
    print(f"  Near positives          : {fmt(s.get('hedge_near_positive'), True)}")
    ha = s.get("hedging_asymmetry")
    if ha is not None:
        print(f"  Hedging asymmetry       : {fmt(ha)}x")
    elif s.get("hedge_near_negative"):
        print("  Hedging asymmetry       : undefined (no hedging near positives at all)")
    else:
        print("  Hedging asymmetry       : n/a")
    print("\nTONE VS. FACTS")
    print(f"  Negative facts framed in positive language: {fmt(s.get('framing_ratio'), True)}")
    print(f"  Mean tone gap on negative facts           : {fmt(s.get('mean_tone_gap_on_negatives'))}")
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze where a disclosure puts information and how it is worded.")
    ap.add_argument("path", nargs="?", default="data/sample_release.txt")
    ap.add_argument("--json", action="store_true", help="print summary + per-sentence flags as JSON")
    ap.add_argument("--keep-boilerplate", action="store_true", help="do not strip forward-looking-statement blocks")
    args = ap.parse_args()

    with open(args.path, encoding="utf-8") as f:
        result = run(f.read(), strip=not args.keep_boilerplate)

    if args.json:
        payload = {"summary": result["summary"],
                   "sentences": [{"d": r["direction"], "m": r["material_neg"]} for r in result["records"]]}
        json.dump(payload, sys.stdout, indent=1)
        print()
    else:
        print_report(result)


if __name__ == "__main__":
    main()
