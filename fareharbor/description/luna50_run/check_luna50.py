"""
Check luna50_output.jsonl and write a readable summary + spreadsheet.

Answers the only question that matters before results are handed back: did the
run actually work, or did it silently half-fail?

Reports per product:
  fields_filled   how many of the 28 fields the model populated
  word_ratio      words emitted / words in the source. ~1.0 is right.
                  Above 1.1 means the model repeated content; well below 0.9
                  means it dropped some.
  duplicates      sentences placed in two different fields on the same side.
                  Counted per side only -- cancellation and accessibility
                  genuinely appear in both the description and the booking
                  notes, and that is correct, not a fault.

Failures are reported separately from quality. A response that came back as
unparseable JSON is a technical failure, not a model that scored zero, and
conflating the two makes a broken run look like a bad model.

Needs pandas + openpyxl for the spreadsheet; without them it still prints the
summary and writes the CSV.

Usage:
    python check_luna50.py
"""
import sys
import re
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "luna50_output.jsonl"
RAW = HERE / "luna50_raw_text.json"
META = HERE / "luna50_products.json"
SUMMARY_CSV = HERE / "luna50_summary.csv"
REVIEW_XLSX = HERE / "luna50_review.xlsx"

DESC_FIELDS = [
    "redo_desc_about", "redo_desc_highlights", "redo_desc_what_included",
    "redo_desc_what_excluded", "redo_desc_itinerary", "redo_desc_what_to_bring",
    "redo_desc_duration_text", "redo_desc_requirements", "redo_desc_cancellation",
    "redo_desc_check_in", "redo_min_age", "redo_max_age", "redo_group_size",
    "redo_meeting_point", "redo_desc_other",
]
BOOKING_FIELDS = [
    "redo_booking_what_to_bring", "redo_booking_what_not_to_bring",
    "redo_booking_inclusions", "redo_booking_location", "redo_booking_check_in",
    "redo_booking_departure_info", "redo_booking_itinerary",
    "redo_booking_important_info", "redo_booking_cancellation",
    "redo_booking_faqs", "redo_booking_before_arrival", "redo_booking_contact",
    "redo_booking_other",
]
ALL_FIELDS = DESC_FIELDS + BOOKING_FIELDS
MIN_DUP_WORDS = 5


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", str(text))
    return [p.strip() for p in parts if p.strip()]


def norm(s):
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())


def count_dupes(fv):
    """Sentences in 2+ fields, per side. Never across sides -- see docstring."""
    total = 0
    for side in (DESC_FIELDS, BOOKING_FIELDS):
        where = {}
        for f in side:
            for s in split_sentences(str(fv.get(f) or "")):
                if len(s.split()) >= MIN_DUP_WORDS:
                    where.setdefault(norm(s), set()).add(f)
        total += sum(1 for v in where.values() if len(v) > 1)
    return total


def main():
    if not OUTPUT.exists():
        raise SystemExit(f"{OUTPUT.name} not found -- run  python run_luna50.py  first.")

    raw = json.loads(RAW.read_text(encoding="utf-8"))
    meta = json.loads(META.read_text(encoding="utf-8"))
    expected = meta["n_requests"]

    parsed, bad_json, truncated, http_error = {}, [], [], []
    n_lines = 0
    for line in open(OUTPUT, encoding="utf-8"):
        if not line.strip():
            continue
        n_lines += 1
        rec = json.loads(line)
        cid = rec.get("custom_id", "")
        pid, _, side = (cid.split("|") + ["", "", ""])[:3]
        resp = rec.get("response") or {}
        if rec.get("error") or resp.get("status_code") != 200:
            http_error.append(cid)
            continue
        choice = (resp.get("body", {}).get("choices") or [{}])[0]
        if choice.get("finish_reason") not in (None, "stop"):
            truncated.append(cid)
        content = (choice.get("message") or {}).get("content") or ""
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```[a-z]*\s*|\s*```$", "", content)
        try:
            parsed.setdefault(pid, {})[side] = json.loads(content)
        except json.JSONDecodeError:
            bad_json.append(cid)

    rows = []
    for pid in meta["product_ids"]:
        got = parsed.get(pid, {})
        fv = {}
        for f in DESC_FIELDS:
            fv[f] = (got.get("desc") or {}).get(f, "")
        for f in BOOKING_FIELDS:
            fv[f] = (got.get("booking") or {}).get(f, "")
        src = raw.get(pid, {})
        src_words = len((src.get("raw_desc", "") + " " + src.get("raw_booking", "")).split())
        emitted = sum(len(str(v or "").split()) for v in fv.values())
        rows.append({
            "product_id": pid,
            "source_words": src_words,
            "words_emitted": emitted,
            "word_ratio": round(emitted / src_words, 3) if src_words else 0,
            "fields_filled": sum(1 for v in fv.values() if str(v or "").strip()),
            "duplicates": count_dupes(fv),
            "desc_returned": "yes" if got.get("desc") else "NO",
            "booking_returned": "yes" if got.get("booking")
                                else ("n/a" if not (src.get("raw_booking") or "").strip()
                                      else "NO"),
            **{f: str(fv.get(f) or "") for f in ALL_FIELDS},
            "raw_description": src.get("raw_desc", ""),
            "raw_booking_notes": src.get("raw_booking", ""),
            "pass/fail": "",
            "comment": "",
        })

    n = len(rows)
    tot_src = sum(r["source_words"] for r in rows)
    tot_emit = sum(r["words_emitted"] for r in rows)
    tot_dup = sum(r["duplicates"] for r in rows)

    print("=" * 74)
    print("LUNA 50-PRODUCT RUN -- CHECK")
    print("=" * 74)
    print(f"  responses received   : {n_lines} of {expected} expected")
    print(f"  products with output : {len(parsed)} of {n}")
    print()
    print("  TECHNICAL FAILURES (not model quality):")
    print(f"    HTTP errors        : {len(http_error)}")
    print(f"    unparseable JSON   : {len(bad_json)}")
    print(f"    truncated          : {len(truncated)}")
    for label, items in (("HTTP", http_error), ("BAD JSON", bad_json),
                         ("TRUNCATED", truncated)):
        for cid in items[:5]:
            print(f"      {label}: {cid}")
    print()
    print("  EXTRACTION QUALITY:")
    print(f"    word ratio overall : {tot_emit / tot_src:.3f}   "
          f"(~1.0 good, >1.1 repeating, <0.9 dropping)")
    print(f"    duplicate sentences: {tot_dup}")
    print(f"    avg fields filled  : {sum(r['fields_filled'] for r in rows) / n:.1f} of 28")

    worst = sorted(rows, key=lambda r: -r["duplicates"])[:5]
    if worst and worst[0]["duplicates"]:
        print("\n    most duplicated products:")
        for r in worst:
            if r["duplicates"]:
                print(f"      {r['product_id']}: {r['duplicates']} duplicate sentence(s)")

    ok = not (http_error or bad_json or truncated) and n_lines == expected
    print("\n  " + ("RUN LOOKS CLEAN -- send the results back."
                    if ok else
                    "RUN HAS ISSUES ABOVE -- report them with the results."))

    try:
        import pandas as pd
        df = pd.DataFrame(rows)
        summary_cols = ["product_id", "source_words", "words_emitted", "word_ratio",
                        "fields_filled", "duplicates", "desc_returned",
                        "booking_returned"]
        df[summary_cols].to_csv(SUMMARY_CSV, index=False, encoding="utf-8")
        print(f"\n  wrote {SUMMARY_CSV.name}")
        try:
            with pd.ExcelWriter(REVIEW_XLSX, engine="openpyxl") as w:
                df[summary_cols].to_excel(w, sheet_name="Summary", index=False)
                df.to_excel(w, sheet_name="Full_Output", index=False)
            print(f"  wrote {REVIEW_XLSX.name}")
        except Exception as e:
            print(f"  (no .xlsx: {e} -- the CSV above has the summary)")
    except ImportError:
        print("\n  (pandas not installed -- no CSV/spreadsheet written. "
              "pip install pandas openpyxl)")

    print(f"\n  SEND BACK: luna50_output.jsonl"
          + (f", {REVIEW_XLSX.name}" if REVIEW_XLSX.exists() else ""))


if __name__ == "__main__":
    main()
