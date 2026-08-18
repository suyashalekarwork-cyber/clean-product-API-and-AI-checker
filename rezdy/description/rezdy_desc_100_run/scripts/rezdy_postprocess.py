"""The safety net: find raw text the model left behind, per Rezdy field.

GOVERNING RULE, inherited unchanged from the booking side: post-processing may
only ADD or REPORT. It may NEVER delete. A dedup pass trialled earlier on this
project would have emptied 9 fields across 8 products, and deciding which copy
of a duplicate is "more specific" is a judgement about meaning made where nobody
can see it. So duplication is reported and left alone.

WHY THIS EXISTS AND A PROMPT RULE CANNOT REPLACE IT: content loss is RANDOM.
Re-running identical products on an identical prompt made 4 of 6 defects vanish.
No wording can guarantee against it, so the check has to be deterministic and
run after the fact. On Fareharbor it would have caught 478466, where an entire
"clothing Golden Rules" block vanished while what_to_bring kept the other
advice -- the output read as complete at 82.4% retention with nothing pointing
at what was gone.

Recording WHICH HEADING the missing text sat under is the part that makes a loss
fixable rather than merely counted.

WHY THIS IS A THIN WRAPPER, NOT A COPY: booking_postprocess.py already does the
work, and it operates on MARKDOWN -- which is exactly what rezdy_common's
converter produces. Re-implementing it would mean re-deriving the three things
it already gets right, each of which cost real time:

  * the LINE is the unit, not the sentence (a bullet or `Label: value` line is
    one unit whatever its punctuation). spaCy was benchmarked for this and
    rejected -- it merged "Sunscreen / Towel / Hat" into ONE unit and ran 397x
    slower.
  * rapidfuzz in three bands: >=97 retained, 80-96 PRESENT BUT REWORDED (a
    verbatim defect, invisible to exact matching), <80 missing.
  * the skip list -- greetings, sign-offs and bare lead-in lines ending in ':'
    are permitted omissions, and counting them inflates loss ~3x.

WHAT IS REZDY-SPECIFIC AND LIVES HERE:
  1. The raw text is HTML, so it must go through html_to_markdown FIRST. Running
     the checker on raw HTML would compare tag soup against clean output and
     report the entire product as lost.
  2. Rezdy has THREE source fields, so a loss is reported WITH THE FIELD it came
     from. "Missing from description" and "missing from terms" are different
     problems with different fixes.
"""
import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from booking_postprocess import find_duplicates, recover        # noqa: E402
from rezdy_common import FIELDS, html_to_markdown               # noqa: E402


def process_field(raw_html, columns, field="description"):
    """One Rezdy field vs the model's columns for that field.

    raw_html : the supplier's original text, straight from the API
    columns  : {column_name: value} the model returned -- EXCLUDING flags
    """
    converted = html_to_markdown(raw_html or "")
    recovered, reworded, stats = recover(converted, columns)
    duplicates = find_duplicates(columns)
    stats["duplicates"] = len(duplicates.split("\n")) if duplicates else 0
    stats["field"] = field
    return {
        "field": field,
        "recovered_content": _tag(recovered, field),
        "reworded_content": _tag(reworded, field),
        "duplicate_content": duplicates,
        "stats": stats,
    }


def _tag(block, field):
    """Prefix each reported line with the field it came from."""
    if not block:
        return ""
    return "\n".join(f"[{field}] {ln}" for ln in block.split("\n") if ln.strip())


def process_product(product, columns_by_field):
    """All of a product's fields at once.

    product          : the raw Rezdy `product` dict
    columns_by_field : {field: {column: value}}
    -> one merged report, plus the per-field detail.
    """
    per_field, rec, rew, dup = [], [], [], []
    totals = {"units_checked": 0, "recovered": 0, "reworded": 0, "duplicates": 0}

    for f in FIELDS:
        cols = columns_by_field.get(f)
        if cols is None:
            continue
        raw = product.get(f)
        if not isinstance(raw, str) or not raw.strip():
            continue
        r = process_field(raw, cols, f)
        per_field.append(r)
        for block, sink in ((r["recovered_content"], rec),
                            (r["reworded_content"], rew),
                            (r["duplicate_content"], dup)):
            if block:
                sink.append(block)
        for k in ("units_checked", "recovered", "reworded", "duplicates"):
            totals[k] += r["stats"][k]

    return {
        "recovered_content": "\n".join(rec),
        "reworded_content": "\n".join(rew),
        "duplicate_content": "\n".join(dup),
        "stats": totals,
        "per_field": per_field,
    }


def is_clean(report):
    """A healthy product reports nothing. Non-empty = investigate, not normal."""
    return not (report["recovered_content"] or report["reworded_content"])


if __name__ == "__main__":
    import json

    sys.stdout.reconfigure(encoding="utf-8")
    from rezdy_common import RAW_DIR

    # A REAL Rezdy product, with a deliberately incomplete extraction: the
    # model kept two of the three inclusions and dropped the third. That is the
    # exact shape of loss this pass exists to catch -- the output looks
    # complete, because what survived is correct.
    path = RAW_DIR / "Rezdy-coolyecoadventures-PHNX5Q.json"
    p = json.loads(path.read_text(encoding="utf-8"))["product"]

    print(f"product: {p.get('name')}\n")
    print("--- what the model was given (converted) ---")
    print(html_to_markdown(p["description"])[:520], "...\n")

    # Build a NEARLY-PERFECT extraction from the product's own text: everything
    # before the heading goes to `about`, everything after it to
    # `what_included` -- except ONE bullet, deliberately dropped.
    lines = html_to_markdown(p["description"]).split("\n")
    cut = next(i for i, l in enumerate(lines) if l.startswith("**"))
    dropped = "Maximum 12 passengers."
    columns = {
        "about": "\n".join(lines[:cut]),
        "what_included": "\n".join(l.lstrip("- ") for l in lines[cut + 1:]
                                   if dropped not in l),
    }
    rep = process_field(p["description"], columns, "description")

    print("--- MISSING (recorded with the heading it sat under) ---")
    print(rep["recovered_content"] or "  (none)")
    print(f"\nunits checked : {rep['stats']['units_checked']}")
    print(f"recovered     : {rep['stats']['recovered']}   <- must be exactly 1")
    print(f"reworded      : {rep['stats']['reworded']}")
    print(f"clean?        : {is_clean(rep)}")

    ok_recall = dropped.rstrip(".") in rep["recovered_content"]
    ok_precision = rep["stats"]["recovered"] == 1
    ok_heading = "WHAT IS INCLUDED" in rep["recovered_content"]
    print(f"\ncaught the dropped line      : {ok_recall}")
    print(f"reported NOTHING else        : {ok_precision}")
    print(f"named the heading it sat under: {ok_heading}")

    # And the same product with a COMPLETE extraction must report nothing.
    columns["what_included"] += "\n" + dropped
    clean = process_field(p["description"], columns, "description")
    print(f"complete extraction is clean : {is_clean(clean)}")
