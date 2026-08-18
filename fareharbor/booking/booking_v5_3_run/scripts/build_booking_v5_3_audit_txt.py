"""
Plain-text audit for the BOOKING V5.3 100-product run.

Same 100 products as the V5 run, so each entry also carries what CHANGED — the
columns V5.3 filled that V5 did not, and vice versa. That comparison is the
point: it is how a new column stealing content from an existing one becomes
visible.

Adds three sections the V5 audit could not have, because the passes did not
exist:

  RECOVERED CONTENT   raw text that reached no column, WITH the heading it sat
                      under. Should be empty.
  REWORDED            text present but not verbatim — a VERBATIM defect that
                      fuzzy retention checks score as "retained". This is how
                      701258 slipped through V5.
  DUPLICATED          the same sentence in 2+ columns. Reported, never removed.

Writes reports/booking_v5_3_hard100_audit.txt, findings first.
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

SCORES = TEST_DIR / "booking_v5_3_100_scores.json"
SELECTION = TEST_DIR / "booking100_products.json"
OUT = ROOT / "reports" / "booking_v5_3_hard100_audit.txt"

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
NEW_COLUMNS = {
    "redo_booking_highlights", "redo_booking_what_excluded",
    "redo_booking_extras", "redo_booking_duration_text",
    "redo_booking_health_safety", "redo_booking_special_requirements",
    "redo_booking_accessibility", "redo_booking_group_size",
    "redo_booking_disclaimers", "redo_booking_pricing",
}

FINDINGS = [
    ("prompt_contamination", "CONTAMINATION -- text copied from the prompt's own examples"),
    ("urls_lost", "URL LOST -- a link in the raw reached no column"),
    ("urls_invented", "URL ALTERED -- a link was changed or invented"),
    ("invented_sentences", "INVENTION -- text in a column that is not in the raw"),
    ("mid_sentence_starts", "MID-SENTENCE START -- a value begins part-way through a sentence"),
    ("item_as_heading", "ITEM AS HEADING -- a packing-list item opened its own column"),
    ("filled_no_heading_at_all", "GATE LEAK -- column filled and the raw has NO heading"),
    ("itinerary_lines_without_signal", "ITINERARY LINE TEST -- no time, step or stop"),
    ("included_that_are_purchasable", "INCLUDED LINE TEST -- line is purchasable"),
    ("markdown_junk_fields", "MARKDOWN JUNK -- * or # survived into a column"),
    ("separators_kept", "SEPARATOR KEPT -- a divider stored as content"),
]

# NOT a defect list. This scorer's heading->column mapper is necessarily
# narrower and blunter than the model's judgement, so "a heading named column X
# but X is empty" mostly means the model routed that content somewhere else --
# often correctly. Measured on this run: of 200 such cases, 161 had the content
# present in another column and only 8 were genuinely absent, several of those
# because the mapper mistook a CONTENT line ("Check in closes 15 minutes prior
# to departure") for a heading. Reported separately so it cannot be read as 200
# defects.
SOFT = [
    ("blank_but_heading_present",
     "review signal -- a heading named this column but the model routed the "
     "content elsewhere (usually correct)"),
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
    v53 = load_outputs("booking_v5_3_100_output.jsonl")
    v5 = load_outputs("booking_v5_100_output.jsonl")

    rows = []
    for pid, s in scores.items():
        f = [(lbl, s[k]) for k, lbl in FINDINGS if s.get(k)]
        soft = [(lbl, s[k]) for k, lbl in SOFT if s.get(k)]
        pp = bool(s.get("recovered_content") or s.get("reworded_content")
                  or s.get("duplicate_content"))
        rows.append((0 if (f or pp) else 1, -len(f), pid, s, f, soft))
    rows.sort()

    n = len(rows)
    n_iss = sum(1 for r in rows if r[0] == 0)
    L = []
    A = L.append

    A("=" * 96)
    A("BOOKING NOTES V5.3 -- 100-PRODUCT AUDIT")
    A("=" * 96)
    A("")
    A("Prompt : SYSTEM_PROMPT_FH_BOOKING_V5_3 (25 columns, heading-gated)")
    A("Model  : gpt-5.6-luna")
    A("Set    : the SAME 100 products the V5 run used, so every difference is")
    A("         caused by the prompt change and nothing else.")
    A("")
    A("A column fills ONLY when the supplier wrote a heading naming it. An EMPTY")
    A("column is a CORRECT answer. Text that names no column goes to `notes` --")
    A("that is the safety net, not a failure.")
    A("")
    A("WHAT CHANGED FROM V5")
    A("  - 15 columns -> 25. inclusions->what_included, location->meeting_point,")
    A("    other->notes, plus 10 new columns derived from a heading census of all")
    A("    8,244 products with booking notes.")
    A("  - Worked examples rewritten with invented names (Sample Wharf, Acme")
    A("    Parking, example.test) after V5 copied one into product 78026.")
    A("  - Stripping a markdown link must KEEP its URL. V5 lost 72 of 238 URLs.")
    A("")
    A(f"products with something to look at : {n_iss} of {n}")
    A(f"products with nothing flagged      : {n - n_iss} of {n}")
    A("")

    A("-" * 96)
    A("FINDING COUNTS")
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
    soft_n = sum(len(s.get("blank_but_heading_present") or []) for _, _, _, s, _, _ in rows)
    A(f"  {soft_n:5d}  review signal only -- a heading named a column but the model")
    A("         routed the content elsewhere. Measured: 161 of 200 had the content")
    A("         present in another column; only 8 were genuinely absent. NOT defects.")
    A("")

    A("-" * 96)
    A("COLUMN FILL RATES  (* = new in V5.3)")
    A("-" * 96)
    for k in FIELDS:
        if k == "redo_booking_flags":
            continue
        c = sum(1 for _, _, pid, _, _, _ in rows if (v53.get(pid, {}).get(k) or "").strip())
        star = " *" if k in NEW_COLUMNS else "  "
        flag = "   <-- NEVER FIRES" if c == 0 else ""
        A(f"  {NICE[k]:24s}{star} {c:4d}/{n}{flag}")
    A("")
    A("=" * 96)
    A("PER-PRODUCT")
    A("=" * 96)

    for _, _, pid, s, f, soft in rows:
        name, raw = load_raw(pid)
        st = strat.get(pid, {})
        a, b = v5.get(pid, {}), v53.get(pid, {})
        A("")
        A("=" * 96)
        A(f"PRODUCT {pid}   {name}")
        A("=" * 96)
        A(f"  stratum   : {st.get('stratum', '?')}   words {s['raw_words']}   "
          f"headings {s['n_headings']}")
        A(f"  retention : {s['retention_pct']}%   columns filled: {s['n_filled']}")
        if s["headings"]:
            A("  headings  : " + "; ".join(s["headings"][:14]))

        gained = [NICE[k] for k in FIELDS if k != "redo_booking_flags"
                  and (b.get(k) or "").strip() and not (a.get(k) or "").strip()]
        lost = [NICE[k] for k in FIELDS if k != "redo_booking_flags"
                and (a.get(k) or "").strip() and not (b.get(k) or "").strip()]
        if gained:
            A("  NOW FILLED (was empty in V5) : " + ", ".join(gained))
        if lost:
            A("  NOW EMPTY  (was filled in V5): " + ", ".join(lost))
        A("")
        A("  VERDICT   : ____________________   (hand review)")
        A("  COMMENT   : ")
        A("")

        if f:
            A("  AUTOMATED FINDINGS")
            for lbl, items in f:
                A(f"    * {lbl}")
                for it in (items if isinstance(items, list) else [str(items)])[:8]:
                    L.extend(wrap(str(it), 88, "        - "))
        else:
            A("  AUTOMATED FINDINGS: none fired")
        A("")
        for lbl, items in soft:
            A(f"  {lbl}")
            A("    " + ", ".join(NICE.get(x, x) for x in items))
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
            star = " *NEW*" if k in NEW_COLUMNS else ""
            A(f"    [{NICE[k]}]{star}")
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
          f"{len(L)} lines, {n} products)")


if __name__ == "__main__":
    main()
