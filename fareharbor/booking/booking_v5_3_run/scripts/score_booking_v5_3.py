"""
Score the BOOKING_V5_3 run (25 columns).

Separate from score_booking_v5.py rather than replacing it, because the V5
output must stay scoreable for the V5 -> V5.3 diff.

What is new here versus the V5 scorer:

  - 25 columns, with the renames (what_included, meeting_point) and the new
    default destination (booking_notes).
  - CONTAMINATION CHECK. The 100-product V5 run put "We do not operate when
    winds exceed 25 knots" into product 78026, copied verbatim out of the
    prompt's own EXAMPLE 3. V5.3's examples deliberately use invented names --
    Sample Wharf, Acme Parking, example.test -- so any of those strings
    appearing in real output is proof of contamination. This turns an invisible
    failure into a one-line assertion.
  - URL INTEGRITY. Every URL in the raw must appear in the output character for
    character. 257745/582339 had URLs destroyed by markdown stripping; 637073
    had one silently ALTERED (maps.app.goo.gl/... -> goo.gl/...).
  - recovered_content / reworded / duplicate_content from booking_postprocess.

Usage:
    python score_booking_v5_3.py
    python score_booking_v5_3.py --file booking_v5_3_100_output.jsonl
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from booking_common import (headings_in, inline_label_of, lines_of,  # noqa: E402
                            load_raw, is_separator, BULLET,
                            parse_booking_json)
from booking_postprocess import process, norm                        # noqa: E402
from score_booking_v5 import looks_like_item, demark                 # noqa: E402

# V5.3 needs its OWN heading->column mapper. Importing the V5 one returned the
# dead names `redo_booking_location` and `redo_booking_inclusions`, which do not
# exist in this schema -- so vals.get() was always None and every product with a
# Location or Inclusions heading reported a phantom "gate miss". That accounted
# for 86 of 179 on the first pass. It also knew nothing of the 10 new columns.
#
# Ordered: FIRST match wins, so narrow concepts precede broad ones. Patterns use
# \w* for prefixes -- a trailing \b makes "includ" unable to match "included".
COLUMN_PATTERNS = [
    ("redo_booking_what_not_to_bring",
     r"\b(not to bring|do ?n[o']?t bring|don't bring|prohibited|not permitted|banned)"),
    ("redo_booking_what_excluded",
     r"\b(not included|exclu\w*|at your own expense|own cost)"),
    ("redo_booking_extras",
     r"\b(optional|add-?ons?|upgrades?|extras|available for purchase)"),
    ("redo_booking_special_requirements",
     r"\b(special requirement\w*|dietary|allerg\w*|special needs|special assistance)"),
    ("redo_booking_accessibility", r"\b(accessib\w*|wheelchair|mobility|disabled access)"),
    ("redo_booking_health_safety",
     r"\b(safety|safe boarding|emergency|hazard|earthquake|tsunami|landslide|"
     r"first aid|life ?jacket|responsible service|sea ?sickness|travel ?sickness)"),
    ("redo_booking_cancellation",
     r"\b(cancel\w*|refund\w*|no ?-?show|reschedul\w*|change of booking)"),
    ("redo_booking_disclaimers",
     r"\b(terms|conditions of|disclaimer\w*|waiver\w*|liabilit\w*|indemnit\w*|"
     r"fraud|privacy|release|rental agreement)"),
    ("redo_booking_pricing",
     r"\b(tax invoice|invoice|abn|gst|price|pricing|rates?|cost|fees?|payment|"
     r"deposit|surcharge|balance|how to pay)"),
    ("redo_booking_before_arrival",
     r"\b(before you (arrive|join|come|travel)|prior to arrival|in advance|"
     r"pre ?-?arrival|before your (visit|trip|adventure|tour|lesson)|"
     r"participation form|sign your waiver)"),
    ("redo_booking_check_in",
     r"\b(check ?-?in|check ?-?out|arrival|arrive|on the day|registration|sign in)"),
    ("redo_booking_departure_info",
     r"\b(departure|departs?|boarding time|pick ?-?up time|schedule|timetable|"
     r"start time|times?)"),
    ("redo_booking_meeting_point",
     r"\b(location|meeting|meet|where to (meet|go|find)|address|venue|parking|"
     r"directions?|getting (there|here|to)|how to get|boarding location|train station)"),
    ("redo_booking_what_to_bring",
     r"\b(bring|wear|pack|clothing|footwear|dress code|gear|equipment|"
     r"what to take|take with you|don'?t forget|personal items)"),
    ("redo_booking_what_included",
     r"\b(includ\w*|inclusion\w*|inclusive|we provide|we supply|what'?s provided|"
     r"what is provided|provided|comes with)"),
    ("redo_booking_itinerary", r"\b(itinerar\w*|itenerar\w*|run sheet|route|day \d)"),
    ("redo_booking_group_size",
     r"\b(group size|capacity|maximum group|minimum numbers?|max people)"),
    ("redo_booking_duration_text", r"\b(duration|how long|length of)"),
    ("redo_booking_contact",
     r"\b(contact|phone|email|website|office hours|call us|get in touch)"),
    ("redo_booking_highlights", r"\b(highlight\w*|why choose)"),
    ("redo_booking_restrictions",
     r"\b(requirements?|rules|policy|policies|prerequisite\w*|suitab\w*|fitness|"
     r"ability level|restriction\w*|conduct|age)"),
    ("redo_booking_important_info",
     r"\b(important|please note|notes?|reminder|general information|general|"
     r"things to know|good to know|other information|additional information|"
     r"more info|tour information|trip information|what you need to know|"
     r"guidelines|details|weather|rain|wind|tide)"),
    ("redo_booking_faqs", r"\b(faqs?|frequently asked)|\?\s*$"),
]


def heading_column(h):
    """Which V5.3 column a heading names, or None."""
    for col, pat in COLUMN_PATTERNS:
        if re.search(pat, h or "", re.I):
            return col
    return None

DEFAULT_FILE = "booking_v5_3_100_output.jsonl"

PARENT = "redo_booking_notes"
FLAGS = "redo_booking_flags"
FIELDS = [
    "redo_booking_highlights", "redo_booking_what_to_bring",
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
]
ALL_KEYS = [PARENT] + FIELDS + [FLAGS]

# Strings that exist ONLY in the prompt's worked examples. Any of these in real
# output means the model copied from the prompt.
PROMPT_MARKERS = [
    "Sample Wharf", "Testing Island", "Acme Parking", "Example Station",
    "example.test", "Sample Beach", "Sample Street", "Testing Road",
    "Ninety minutes",
]

URL = re.compile(r"https?://[^\s\)\]>,]+", re.I)
PURCHASABLE = re.compile(
    r"available for purchase|can be purchased|at extra cost|additional charge|"
    r"available for hire|optional extra|at your own expense", re.I)
TIME_SIGNAL = re.compile(
    r"\b\d{1,2}[:.]\d{2}\s*(am|pm)?\b|\b\d{1,2}\s*(am|pm)\b|"
    r"\bday\s*\d|\bstop\s*\d|\bstep\s*\d|->|→", re.I)
MONEY = re.compile(r"refund|deposit|no.?show|cancellation fee|charge|forfeit|"
                   r"credit|reschedul", re.I)
MARKDOWN_JUNK = re.compile(r"[*#`]")
CONTINUATION = re.compile(
    r"^\s*(?:and|or|but|which|that|because|so|then|also|however)\b", re.I)


def score_product(pid, fields):
    _, raw = load_raw(pid)
    vals = {k: (fields.get(k) or "").strip() for k in ALL_KEYS}
    content = {k: v for k, v in vals.items() if k != FLAGS}

    raw_lines = lines_of(raw)
    heads = headings_in(raw_lines)
    mapped = {}
    for _, h in heads:
        if (col := heading_column(h)):
            mapped.setdefault(col, []).append(h)
    for l in raw_lines:
        il = inline_label_of(l)
        if il and (col := heading_column(il[0])):
            mapped.setdefault(col, []).append(il[0])

    filled = [k for k in FIELDS if vals[k]]
    r = {
        "product_id": pid,
        "raw_words": len(raw.split()),
        "n_headings": len(heads),
        "headings": [h for _, h in heads],
        "fields_filled": filled,
        "n_filled": len(filled),
        "notes_words": len(vals[PARENT].split()),
        "flags": vals[FLAGS],
    }

    # --- post-processing: the two report-only passes -----------------------
    pp = process(raw, content)
    r["recovered_content"] = pp["recovered_content"]
    r["reworded_content"] = pp["reworded_content"]
    r["duplicate_content"] = pp["duplicate_content"]
    r["pp_stats"] = pp["stats"]

    n_units = max(1, pp["stats"]["units_checked"])
    lost = pp["stats"]["recovered"]
    r["retention_pct"] = round(100 * (n_units - lost) / n_units, 1)

    # --- CONTAMINATION: text lifted from the prompt's own examples ---------
    blob_all = " ".join(content.values())
    r["prompt_contamination"] = [m for m in PROMPT_MARKERS if m.lower() in blob_all.lower()]

    # --- URL integrity ----------------------------------------------------
    raw_urls = set(URL.findall(raw))
    out_urls = set(URL.findall(blob_all))
    r["urls_lost"] = sorted(u for u in raw_urls if u not in out_urls)
    r["urls_invented"] = sorted(u for u in out_urls if u not in raw_urls)

    # --- the gate ---------------------------------------------------------
    unmapped_fill = [k for k in filled if k not in mapped]
    r["filled_no_heading_at_all"] = unmapped_fill if not heads else []
    r["filled_unmapped_heading"] = unmapped_fill if heads else []
    r["blank_but_heading_present"] = [k for k in mapped if not vals.get(k)]

    # --- invention (text not in the raw at all) ---------------------------
    nraw = norm(raw)
    invented = []
    for k in content:
        for s in re.split(r"(?<=[.!?])\s+|\n+", content[k]):
            s = s.strip()
            if len(norm(s).split()) >= 6 and norm(s)[:60] not in nraw:
                from rapidfuzz import fuzz
                if fuzz.partial_ratio(norm(s), nraw) < 85:
                    invented.append(f"{k}: {s[:110]}")
    r["invented_sentences"] = invented

    # --- C1: values beginning mid-sentence --------------------------------
    raw_starts = [norm(l) for l in raw_lines]
    mids = []
    for k in content:
        if not vals[k]:
            continue
        first = demark(vals[k].split("\n")[0]).strip()
        looks_off = CONTINUATION.match(first) or (
            first[:1].islower() and len(first.split()) > 2)
        if looks_off:
            probe = norm(first)[:40]
            if probe and not any(s.startswith(probe) for s in raw_starts):
                mids.append(f"{k}: {first[:90]}")
    r["mid_sentence_starts"] = mids

    # --- packing item that opened its own column --------------------------
    head_lines = {i for i, _ in heads}
    items = {norm(demark(l)) for i, l in enumerate(raw_lines)
             if looks_like_item(l) and (BULLET.match(l) or i not in head_lines)}
    items.discard("")
    r["item_as_heading"] = [
        f"{k}: {vals[k][:60]}" for k in FIELDS
        if k not in ("redo_booking_what_to_bring", "redo_booking_what_included")
        and norm(vals[k]) and norm(vals[k]) in items]

    # --- line tests -------------------------------------------------------
    r["itinerary_lines_without_signal"] = [
        l.strip()[:90] for l in vals["redo_booking_itinerary"].split("\n")
        if l.strip() and not TIME_SIGNAL.search(l)]
    r["included_that_are_purchasable"] = [
        l.strip()[:90] for l in vals["redo_booking_what_included"].split("\n")
        if l.strip() and PURCHASABLE.search(l)]

    # --- definitional guards ---------------------------------------------
    c = vals["redo_booking_cancellation"]
    r["cancellation_without_money"] = bool(c) and not MONEY.search(c)
    p = vals["redo_booking_pricing"]
    r["pricing_without_figure"] = bool(p) and not re.search(r"\d", p)
    r["markdown_junk_fields"] = [k for k in content if MARKDOWN_JUNK.search(vals[k] or "")]
    r["separators_kept"] = [
        k for k in content if any(is_separator(l) for l in (vals[k] or "").split("\n"))]
    return r


def load(path):
    out, bad, repairs = {}, [], {}
    for line in path.open(encoding="utf-8"):
        row = json.loads(line)
        pid = row["custom_id"].split("|")[0]
        fields, note = parse_booking_json(
            row["response"]["body"]["choices"][0]["message"]["content"])
        if fields is None:
            bad.append(pid)
            continue
        out[pid] = fields
        if note:
            repairs[pid] = note
    return out, bad, repairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT_FILE)
    args = ap.parse_args()

    path = TEST_DIR / args.file
    data, bad, repairs = load(path)
    print(f"loaded {len(data)} products from {path.name}"
          + (f"   UNPARSEABLE: {bad}" if bad else ""))
    if repairs:
        print(f"json repaired: {repairs}")

    rows = [score_product(pid, f) for pid, f in sorted(data.items())]
    n = len(rows)
    agg = lambda k: sum(len(r[k]) for r in rows)                    # noqa: E731
    npos = lambda k: sum(1 for r in rows if r[k])                   # noqa: E731

    print(f"\n{'=' * 64}\nBOOKING V5.3 -- {n} products, 25 columns\n{'=' * 64}")
    print(f"mean retention             : {sum(r['retention_pct'] for r in rows) / n:.1f}%")
    print(f"products at 100% retention : {sum(1 for r in rows if not r['recovered_content'])}")
    print()
    print("HARD GATES (must be zero)")
    for label, key in [
        ("TEXT COPIED FROM THE PROMPT", "prompt_contamination"),
        ("URLs lost", "urls_lost"),
        ("URLs invented / altered", "urls_invented"),
        ("invented sentences", "invented_sentences"),
        ("values starting mid-sentence", "mid_sentence_starts"),
        ("packing item opened a column", "item_as_heading"),
        ("filled, raw has no heading at all", "filled_no_heading_at_all"),
        ("itinerary lines without a signal", "itinerary_lines_without_signal"),
        ("what_included that are purchasable", "included_that_are_purchasable"),
        ("markdown junk", "markdown_junk_fields"),
        ("separators kept", "separators_kept"),
    ]:
        print(f"  {label:38s} {agg(key):5d}   ({npos(key)} products)")
    print(f"  {'cancellation without money':38s} "
          f"{sum(1 for r in rows if r['cancellation_without_money']):5d}")
    print(f"  {'pricing without a figure':38s} "
          f"{sum(1 for r in rows if r['pricing_without_figure']):5d}")

    print("\nPOST-PROCESSING (report only, nothing deleted)")
    print(f"  recovered_content entries : {sum(r['pp_stats']['recovered'] for r in rows):5d}"
          f"   ({npos('recovered_content')} products)")
    print(f"  reworded (VERBATIM defect): {sum(r['pp_stats']['reworded'] for r in rows):5d}"
          f"   ({npos('reworded_content')} products)")
    print(f"  duplicate_content entries : {sum(r['pp_stats']['duplicates'] for r in rows):5d}"
          f"   ({npos('duplicate_content')} products)")

    print("\nCOLUMN FILL RATES")
    for k in [PARENT] + FIELDS:
        c = sum(1 for r in rows if k in r["fields_filled"]
                or (k == PARENT and r["notes_words"]))
        mark = "   <-- NEVER FIRES" if c == 0 else ""
        print(f"  {k.replace('redo_booking_', ''):26s} {c:4d}/{n}{mark}")

    tot = sum(r["raw_words"] for r in rows)
    catch = sum(r["notes_words"] for r in rows)
    print(f"\nDEFAULT SHARE: {catch}/{tot} words ({100 * catch / max(1, tot):.1f}%) "
          f"in {PARENT}")

    out = TEST_DIR / path.name.replace("_output.jsonl", "_scores.json")
    out.write_text(json.dumps({r["product_id"]: r for r in rows},
                              indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out.name}")


if __name__ == "__main__":
    main()
