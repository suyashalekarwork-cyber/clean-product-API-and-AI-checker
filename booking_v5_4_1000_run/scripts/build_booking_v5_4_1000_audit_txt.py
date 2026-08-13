"""
Plain-text audit for the BOOKING V5.3 500-product run.

Adapted from build_booking_v5_3_audit_txt.py, with three differences forced by
what this run is:

  - NO V5-vs-V5.3 diff. These 500 products were never run on V5, so there is
    nothing to compare against. The 100-run audit's "NOW FILLED / NOW EMPTY"
    section is dropped rather than faked.
  - COLLAPSE is reported per product (how much of it landed in one column).
    That is the measurement this run existed to produce.
  - FLAGGED PRODUCTS ONLY by default. 500 full products is a ~5 MB file; the
    clean majority belongs in the workbook, where it can be filtered.

NOBODY HAS HAND-READ THESE 500. Every finding is detector output. The
"VERDICT/COMMENT" lines are left blank for exactly that reason -- this file is
the input to a hand review, not the result of one.

Writes reports/booking_v5_4_1000_audit.txt, findings first.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = ROOT / "data_pipeline" / "batch_api_test"
sys.path.insert(0, str(TEST_DIR))

from booking_common import load_raw, parse_booking_json  # noqa: E402

SCORES = TEST_DIR / "booking_v5_4_1000_scores.json"
SELECTION = TEST_DIR / "booking1000_products.json"
OUTPUT = "booking_v5_4_1000_output.jsonl"
OUT = ROOT / "reports" / "booking_v5_4_1000_audit.txt"

PARENT = "redo_booking_notes"
FIELDS = [
    PARENT, "redo_booking_highlights", "redo_booking_what_to_bring",
    "redo_booking_what_not_to_bring", "redo_booking_what_included",
    "redo_booking_what_excluded", "redo_booking_extras",
    "redo_booking_meeting_point", "redo_booking_check_in",
    "redo_booking_before_arrival", "redo_booking_departure_info",
    "redo_booking_itinerary", "redo_booking_duration_text",
    "redo_booking_important_info", "redo_booking_health_safety",
    "redo_booking_restrictions", "redo_booking_special_requirements",
    "redo_booking_accessibility", "redo_booking_group_size",
    "redo_booking_cancellation", "redo_booking_disclaimers",
    "redo_booking_pricing", "redo_booking_faqs", "redo_booking_contact",
    "redo_booking_flags",
]
NICE = {f: f.replace("redo_booking_", "") for f in FIELDS}

FINDINGS = [
    ("prompt_contamination", "CONTAMINATION -- text copied from the prompt's own examples"),
    ("urls_lost", "URL LOST -- a link in the raw reached no column"),
    ("urls_invented", "URL ALTERED -- a link was changed or invented"),
    ("invented_sentences", "INVENTION -- text in a column that is not in the raw"),
    ("mid_sentence_starts", "MID-SENTENCE START -- a value begins part-way through a sentence"),
    ("item_as_heading", "ITEM AS HEADING -- a packing-list item opened its own column"),
    ("filled_no_heading_at_all", "GATE LEAK -- column filled and the raw offers NO licence"),
    ("itinerary_lines_without_signal", "ITINERARY LINE TEST -- no time, step or stop"),
    ("included_that_are_purchasable", "INCLUDED LINE TEST -- line is purchasable"),
    ("markdown_junk_fields", "MARKDOWN JUNK -- * or # survived into a column"),
    ("separators_kept", "SEPARATOR KEPT -- a divider stored as content"),
]

# NOT a defect list -- see the 100-run audit for the measurement behind this.
SOFT = [
    ("blank_but_heading_present",
     "review signal -- a heading named this column but the model routed the "
     "content elsewhere (usually correct)"),
    ("itinerary_lines_not_checkable",
     "not checkable -- itinerary lines in a non-Latin script; the line test "
     "reads English time and ordering words only"),
]


def wrap(text, width=94, indent=""):
    out, line = [], indent
    for word in (text or "").split():
        if len(line) + len(word) + 1 > width and line.strip():
            out.append(line.rstrip())
            line = indent + word + " "
        else:
            line += word + " "
    if line.strip():
        out.append(line.rstrip())
    return out


def block(text, indent="    "):
    out = []
    for raw_line in (text or "").split("\n"):
        if raw_line.strip():
            out.extend(wrap(raw_line, 94, indent) or [indent])
    return out


def load_outputs(fn):
    out = {}
    for line in (TEST_DIR / fn).open(encoding="utf-8"):
        d = json.loads(line)
        f, _ = parse_booking_json(
            d["response"]["body"]["choices"][0]["message"]["content"])
        out[d["custom_id"].split("|")[0]] = f or {}
    return out


def main():
    scores = json.loads(SCORES.read_text(encoding="utf-8"))
    strat = {r["product_id"]: r
             for r in json.loads(SELECTION.read_text(encoding="utf-8"))["products"]}
    v53 = load_outputs(OUTPUT)

    rows = []
    for pid, s in scores.items():
        f = [(lbl, s[k]) for k, lbl in FINDINGS if s.get(k)]
        soft = [(lbl, s[k]) for k, lbl in SOFT if s.get(k)]
        pp = bool(s.get("recovered_content") or s.get("reworded_content")
                  or s.get("duplicate_content"))
        rows.append((0 if (f or pp) else 1, -len(f), pid, s, f, soft))
    rows.sort()

    n = len(rows)
    flagged = [r for r in rows if r[0] == 0]
    L = []
    A = L.append

    A("=" * 96)
    A("BOOKING NOTES V5.3 -- 1000-PRODUCT AUDIT")
    A("=" * 96)
    A("")
    A("Prompt : SYSTEM_PROMPT_FH_BOOKING_V5_4 (25 columns, heading-gated)")
    A("         UNCHANGED from the 100-product run, deliberately -- the sample")
    A("         changed, so the prompt did not, or no difference could be")
    A("         attributed to either.")
    A("Model  : gpt-5.6-luna")
    A("Set    : 1000 products, UNIFORM RANDOM (seed 42), none of them from the")
    A("         600 already run. NOT stratified and NOT hardest-first -- every")
    A("         earlier booking set was chosen for difficulty, so this is the")
    A("         first booking run whose rate can be quoted for the catalogue.")
    A("")
    A("A column fills ONLY when the supplier wrote a heading naming it. An EMPTY")
    A("column is a CORRECT answer. Text that names no column goes to `notes` --")
    A("that is the safety net, not a failure.")
    A("")
    A("*** NOBODY HAS HAND-READ THESE 500. ***")
    A("Everything below is DETECTOR OUTPUT and is an UPPER BOUND. On the")
    A("100-product run, once each finding was read against the raw, 24 of 43")
    A("flagged products turned out to be the detector rather than the model.")
    A("The VERDICT and COMMENT lines are blank because this file is the INPUT")
    A("to a hand review, not the result of one.")
    A("")
    A("One scorer bug was found and fixed DURING this run: the gate leak count")
    A("was 93 across 36 products before the fix and 49 across 18 after. The gate")
    A("split on markdown headings while the column mapping already honoured")
    A("inline labels, so products correctly routing off `Refund Policy - ...`")
    A("were accused of filling from nothing. On the 100 run that flag read 0")
    A("both before and after -- it was invisible until the sample changed.")
    A("")
    A(f"products with something to look at : {len(flagged)} of {n}")
    A(f"products with nothing flagged      : {n - len(flagged)} of {n}")
    A("")
    A("This file contains the FLAGGED products only. All 500 are in")
    A("exports/booking_v5_3_500_scores.xlsx, where they can be sorted and")
    A("filtered.")
    A("")

    A("-" * 96)
    A("FINDING COUNTS  (upper bounds -- unverified)")
    A("-" * 96)
    tally = Counter()
    for _, _, _, s, f, _sf in rows:
        for lbl, items in f:
            tally[lbl] += len(items)
    for lbl, c in tally.most_common():
        A(f"  {c:5d}  {lbl}")
    A("")
    A(f"  {sum(s['pp_stats']['recovered'] for _, _, _, s, _, _ in rows):5d}  "
      "RECOVERED CONTENT -- raw text that reached no column")
    A(f"  {sum(s['pp_stats']['reworded'] for _, _, _, s, _, _ in rows):5d}  "
      "REWORDED -- present but not verbatim (a VERBATIM defect)")
    A(f"  {sum(s['pp_stats']['duplicates'] for _, _, _, s, _, _ in rows):5d}  "
      "DUPLICATED -- same sentence in 2+ columns (reported, not removed)")
    A("")

    A("-" * 96)
    A("COLLAPSE -- how often one heading swallowed a whole product")
    A("-" * 96)
    A("")
    A("The measurement this run existed to produce. Reported BY STRATUM because")
    A("the overall figure is meaningless: 125 of the 500 were selected for")
    A("having no headings at all, and those collapse into the catch-all")
    A("CORRECTLY.")
    A("")
    by = {}
    for pid, s in scores.items():
        st = strat.get(pid, {}).get("regime", "?")
        d = by.setdefault(st, {"n": 0, "full": 0})
        d["n"] += 1
        d["full"] += s["top_column_share"] == 100
    for st in ["heading_rich", "bullet_heavy", "long_no_heading", "inline_label_only"]:
        d = by.get(st)
        if not d:
            continue
        note = ("  <-- THE REAL MEASURE" if st == "heading_rich" else
                "  (correct by design -- no headings exist)"
                if st in ("long_no_heading", "inline_label_only") else "")
        A(f"  {st:20s} {d['full']:4d} of {d['n']:4d} at 100% in one column"
          f"  ({100*d['full']/d['n']:4.1f}%){note}")
    A("")
    real = [pid for pid, s in scores.items()
            if strat.get(pid, {}).get("regime") in ("heading_rich", "bullet_heavy")
            and s["top_column_share"] == 100 and s["n_headings"] >= 3]
    A(f"  {len(real)} products have THREE OR MORE headings and still filled exactly")
    A("  one column. Those are the outer-heading rule's real cost:")
    for pid in sorted(real, key=lambda p: -scores[p]["raw_words"])[:12]:
        s = scores[pid]
        A(f"      {pid:>8s}  {s['n_headings']:3d} headings, {s['raw_words']:5d} words"
          f"  -> ALL in {NICE.get(s['top_column'], s['top_column'])}")
    A("")

    A("-" * 96)
    A("COLUMN FILL RATES")
    A("-" * 96)
    for k in FIELDS:
        if k == "redo_booking_flags":
            continue
        c = sum(1 for _, _, pid, _, _, _ in rows if (v53.get(pid, {}).get(k) or "").strip())
        flag = "   <-- NEVER FIRES" if c == 0 else ""
        A(f"  {NICE[k]:24s} {c:4d}/{n}{flag}")
    A("")

    A("=" * 96)
    A("PER-PRODUCT  (flagged only)")
    A("=" * 96)

    for _, _, pid, s, f, soft in flagged:
        name, raw = load_raw(pid)
        st = strat.get(pid, {})
        b = v53.get(pid, {})
        A("")
        A("=" * 96)
        A(f"PRODUCT {pid}   {name}")
        A("=" * 96)
        A(f"  stratum   : {st.get('regime', '?')}   words {s['raw_words']}   "
          f"headings {s['n_headings']}")
        A(f"  retention : {s['retention_pct']}%   columns filled: {s['n_filled']}")
        A(f"  collapse  : {s['top_column_share']}% of the words in "
          f"{NICE.get(s['top_column'], s['top_column'])}"
          f"   ({s['n_content_cols']} content columns used)")
        if s["headings"]:
            A("  headings  : " + "; ".join(s["headings"][:14]))
        A("")
        A("  VERDICT   : ____________________   (hand review)")
        A("  COMMENT   : ")
        A("")

        if f:
            A("  AUTOMATED FINDINGS  (unverified)")
            for lbl, items in f:
                A(f"    * {lbl}")
                for it in (items if isinstance(items, list) else [str(items)])[:8]:
                    L.extend(wrap(str(it), 88, "        - "))
        else:
            A("  AUTOMATED FINDINGS: none fired")
        A("")
        for lbl, items in soft:
            A(f"  {lbl}")
            A("    " + ", ".join(NICE.get(x, x) for x in items)[:400])
            A("")

        for key, title in [
            ("recovered_content", "RECOVERED CONTENT -- reached no column (heading: text)"),
            ("reworded_content", "REWORDED -- present but not verbatim"),
            ("duplicate_content", "DUPLICATED -- same sentence in 2+ columns"),
        ]:
            if s.get(key):
                A(f"  {title}")
                L.extend(block(s[key], "        "))
                A("")

        A("  " + "-" * 92)
        A("  RAW BOOKING NOTES")
        A("  " + "-" * 92)
        L.extend(block(raw, "    "))
        A("")
        A("  " + "-" * 92)
        A("  EXTRACTED COLUMNS")
        A("  " + "-" * 92)
        any_filled = False
        for k in FIELDS:
            v = (b.get(k) or "").strip()
            if not v:
                continue
            any_filled = True
            A(f"    [{NICE[k]}]")
            L.extend(block(v, "        "))
            A("")
        if not any_filled:
            A("    (nothing extracted)")
        blanks = [NICE[k] for k in FIELDS if not (b.get(k) or "").strip()]
        A("    EMPTY: " + ", ".join(blanks))
        A("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size / 1024:.0f} KB, "
          f"{len(L)} lines, {len(flagged)} flagged of {n})")


if __name__ == "__main__":
    main()
