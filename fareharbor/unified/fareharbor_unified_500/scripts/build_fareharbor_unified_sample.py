"""Write 10 random products as a plain-text manual-check file.

Each product shows the RAW supplier text first, then the 48 unified columns built
from it, so every value can be checked back to its source by eye. Random sample,
seed 42, so re-running gives the same 10 products.

Output: reports/fareharbor_unified_sample_10.txt
"""
import json
import random
import sys
import textwrap
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import pandas as pd  # noqa: E402

UNIFIED = ROOT / "data_pipeline" / "fareharbor_unified" / "fareharbor_unified.csv"
INTERNAL = ROOT / "data_pipeline" / "fareharbor_unified" / "fareharbor_internal.csv"
OUT = ROOT / "reports" / "fareharbor_unified_sample_10.txt"

SEED, N = 42, 10
WIDTH = 96
RULE = "=" * WIDTH
THIN = "-" * WIDTH


def wrap(text, indent="    "):
    if not text:
        return indent + "(empty)"
    out = []
    for line in str(text).split("\n"):
        if not line.strip():
            out.append("")
            continue
        out.extend(textwrap.wrap(line, width=WIDTH - len(indent),
                                 initial_indent=indent, subsequent_indent=indent + "  ")
                   or [indent])
    return "\n".join(out)


def main():
    dev = pd.read_csv(UNIFIED, dtype=str).fillna("")
    internal = pd.read_csv(INTERNAL, dtype=str).fillna("")
    merged = dev.merge(internal, on="compound_key", how="left")

    random.seed(SEED)
    picks = random.sample(sorted(dev["product_id"]), N)

    lines = [
        RULE,
        "FAREHARBOR UNIFIED TABLE - 10 RANDOM PRODUCTS FOR MANUAL CHECK",
        RULE,
        "",
        f"Sample     : {N} products drawn at random (seed {SEED}) from the 500-product set.",
        "Sources    : API/ETL fareharbor_etl_v2.csv | description V5.3 | booking notes V5.4",
        "Built by   : scripts/build_fareharbor_unified.py",
        "Design doc : reports/FAREHARBOR_500_COLUMN_INVENTORY.md",
        "",
        "HOW TO CHECK EACH PRODUCT",
        "  1. Read the RAW DESCRIPTION and RAW BOOKING NOTES blocks first.",
        "  2. Then read the 48 unified columns underneath.",
        "  3. For each column ask: is this value actually in the raw text above,",
        "     and is it under the right heading?",
        "  4. An EMPTY column is usually CORRECT - a field only fills when the supplier",
        "     wrote a heading naming it. Empty means 'no heading', not 'we missed it'.",
        "",
        "SOURCE TAGS shown after each value",
        "  [api]      straight from the Fareharbor API",
        "  [desc]     from the description extraction",
        "  [booking]  from the booking-notes extraction",
        "  [desc+booking (DIFFERENT, score NN)]  both sides had content and it differed,",
        "             so BOTH texts were kept, joined by a blank line",
        "  [... (REWORDED-REVIEW, score NN)]     both sides similar but not identical -",
        "             kept both, flagged as worth a human look",
        "  [... (SAME ..., kept longer)]         both sides said the same thing, one kept",
        "",
        "KNOWN ACCEPTED DEFECT",
        "  In list fields (What's Included, Itinerary, What to Bring, Highlights,",
        "  What's Not Included, What Not to Bring) a DIFFERENT/REWORDED merge can repeat",
        "  bullets that appear on both sides. This was reviewed and accepted - no content",
        "  is lost, and de-duplicating can be added later. Flag it if you see it, but it",
        "  is expected, not a new bug.",
        "",
    ]

    groups = [
        ("PRODUCT", ["compound_key", "product_id", "source", "product_name",
                     "product_headline", "product_price", "product_currency",
                     "product_price_options", "product_duration", "product_duration_minutes"]),
        ("MEDIA & CATEGORY", ["product_main_image", "product_images", "product_category"]),
        ("LOCATION", ["location_street", "location_city", "location_state",
                      "location_country", "location_postcode",
                      "location_latitude", "location_longitude"]),
        ("DETAIL PAGE", ["detail_description", "detail_highlights", "detail_what_is_included",
                         "detail_what_is_not_included", "detail_itinerary",
                         "detail_important_info", "detail_booking_notes",
                         "detail_meeting_point", "detail_check_in", "detail_departure_info",
                         "detail_before_arrival", "detail_what_to_bring",
                         "detail_what_not_to_bring", "detail_accessibility",
                         "detail_restrictions", "detail_special_requirements",
                         "detail_health_safety", "detail_group_size", "detail_faqs",
                         "detail_extras", "detail_disclaimers"]),
        ("POLICY & COMMERCIAL", ["detail_cancellation_policy", "detail_cancellation_hours",
                                 "detail_tax_percentage", "detail_pricing_notes",
                                 "detail_pickup_available"]),
        ("SUPPLIER", ["meta_supplier_name", "detail_operator_contact"]),
    ]

    for n, pid in enumerate(picks, 1):
        r = merged[merged["product_id"] == pid].iloc[0]
        meta = json.loads(r["meta_field_sources"]) if r["meta_field_sources"] else {"sources": {}, "notes": []}
        src = meta.get("sources", {})

        lines += ["", RULE,
                  f"PRODUCT {n} of {N}   |   id {pid}   |   {r['product_name'][:52]}",
                  f"supplier: {r['meta_supplier_name']}",
                  RULE, "",
                  THIN,
                  "RAW DESCRIPTION  (the text the description extraction read)",
                  THIN,
                  wrap(r["meta_raw_description"]), "",
                  THIN,
                  "RAW BOOKING NOTES  (the text the booking extraction read)",
                  THIN,
                  wrap(r["meta_raw_booking_notes"]), ""]

        merges = {k: v for k, v in src.items()
                  if v.startswith("desc+booking") or "SAME" in v}
        lines += [THIN,
                  f"MERGES ON THIS PRODUCT  ({len(merges)} field(s) where BOTH sides had content)",
                  THIN]
        lines += [f"    {k:32s} {v}" for k, v in merges.items()] or ["    (none)"]
        if meta.get("notes"):
            lines += ["", "    NOTES:"] + [f"      - {x}" for x in meta["notes"]]
        lines += [""]

        filled = sum(1 for _, cols in groups for c in cols if str(r[c]).strip())
        lines += [THIN, f"UNIFIED ROW - 48 COLUMNS  ({filled} filled, {48-filled} empty)", THIN]
        for title, cols in groups:
            lines += ["", f"  [{title}]"]
            for c in cols:
                v = str(r[c]).strip()
                tag = src.get(c, "")
                head = f"  {c}" + (f"   <{tag}>" if tag else "")
                lines.append(head)
                lines.append(wrap(v, indent="      "))
        lines += [""]

    lines += ["", RULE, "END OF SAMPLE", RULE, ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")
    print("Products:", ", ".join(picks))


if __name__ == "__main__":
    main()
