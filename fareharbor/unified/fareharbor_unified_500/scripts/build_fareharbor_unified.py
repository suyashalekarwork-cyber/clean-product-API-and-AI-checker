"""Build the Fareharbor unified table from three inputs.

Inputs (all READ-ONLY, checksummed before and after):
  1. exports/fareharbor_etl_v2.csv                  - API/ETL, 69 cols
  2. data_pipeline/batch_api_test/v5_3_full_output.jsonl    - description V5.3, 22 cols
  3. data_pipeline/batch_api_test/booking_v5_4_500_output.jsonl - booking V5.4, 25 cols

Outputs (data_pipeline/fareharbor_unified/):
  fareharbor_unified.csv/.xlsx   - 48 columns, for the web dev team
  fareharbor_internal.csv        -  8 columns, data team only (QA/audit/provenance)

Design settled in reports/FAREHARBOR_500_COLUMN_INVENTORY.md. Read that first; every
mapping and merge decision below traces to a numbered section there.

Universe = the products present in the booking run. Description and API rows are
looked up for those same ids.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
BT = ROOT / "data_pipeline" / "batch_api_test"
sys.path.insert(0, str(BT))

from booking_common import parse_booking_json  # noqa: E402
from rapidfuzz import fuzz  # noqa: E402
import pandas as pd  # noqa: E402

ETL_CSV = ROOT / "exports" / "fareharbor_etl_v2.csv"
DESC_JSONL = BT / "v5_3_full_output.jsonl"
BOOK_JSONL = BT / "booking_v5_4_500_output.jsonl"
OUT_DIR = ROOT / "data_pipeline" / "fareharbor_unified"

# Empty-equivalents seen in this data. Fareharbor returns the literal "<p>None</p>".
EMPTY = {"", "[]", "{}", "nan", "none", "null", "<p>none</p>", "n/a", "-"}
# openpyxl raises IllegalCharacterError on these; present in some supplier raw text.
CONTROL = re.compile(r"[\000-\010\013\014\016-\037]")
# gpt-5.6-luna intermittently closes JSON with a stray comma before the brace.
STRAY_COMMA = re.compile(r',\s*"\s*\}\s*$')

SAME_BAND = 97   # >= this: the two texts are the same content, keep the longer
DIFF_BAND = 80   # <  this: genuinely different, keep both. Between: keep both + flag


# --------------------------------------------------------------------------- utils
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean(v):
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s.lower() in EMPTY else s


def for_excel(v):
    return CONTROL.sub("", v) if isinstance(v, str) else v


def body(rec):
    return rec["response"]["body"]["choices"][0]["message"]["content"]


def product_id(rec):
    return rec["custom_id"].split("|")[0]


# ----------------------------------------------------------------------- the merge
def merge(desc_val, book_val, booking_first):
    """Section 5 three-band rule. -> (value, provenance_note).

    Whole-text comparison only. The bullet-level pass was considered and declined
    (Section 8) - duplicated list items are an accepted cosmetic defect. Nothing is
    ever dropped, so adding that pass later is purely additive.
    """
    d, b = clean(desc_val), clean(book_val)
    if not d and not b:
        return "", ""
    if not b:
        return d, "desc"
    if not d:
        return b, "booking"

    score = max(fuzz.token_set_ratio(d.lower(), b.lower()),
                fuzz.partial_ratio(d.lower(), b.lower()))
    if score >= SAME_BAND:
        if len(b) >= len(d):
            return b, f"booking (SAME as desc, score {score:.0f}, kept longer)"
        return d, f"desc (SAME as booking, score {score:.0f}, kept longer)"

    band = "DIFFERENT" if score < DIFF_BAND else "REWORDED-REVIEW"
    parts = [b, d] if booking_first else [d, b]
    return "\n\n".join(parts), f"desc+booking ({band}, score {score:.0f})"


# MERGED FIELDS: unified name -> (desc key, booking key, booking_first)
# booking_first reflects which side is the stronger source, measured over the 500.
MERGED = {
    "detail_highlights":           ("redo_desc_highlights", "redo_booking_highlights", False),
    "detail_what_is_included":     ("redo_desc_what_included", "redo_booking_what_included", False),
    "detail_what_is_not_included": ("redo_desc_what_excluded", "redo_booking_what_excluded", False),
    "detail_itinerary":            ("redo_desc_itinerary", "redo_booking_itinerary", False),
    "detail_important_info":       ("redo_desc_important_info", "redo_booking_important_info", True),
    "detail_meeting_point":        ("redo_meeting_point", "redo_booking_meeting_point", True),
    "detail_check_in":             ("redo_desc_check_in", "redo_booking_check_in", True),
    "detail_what_to_bring":        ("redo_desc_what_to_bring", "redo_booking_what_to_bring", True),
    "detail_accessibility":        ("redo_desc_accessibility", "redo_booking_accessibility", True),
    "detail_restrictions":         ("redo_desc_restrictions", "redo_booking_restrictions", True),
    "detail_faqs":                 ("redo_desc_faqs", "redo_booking_faqs", True),
    "detail_extras":               ("redo_desc_extras", "redo_booking_extras", True),
    "detail_disclaimers":          ("redo_desc_disclaimers", "redo_booking_disclaimers", True),
    "detail_pricing_notes":        ("redo_desc_pricing", "redo_booking_pricing", True),
}

# STRAIGHT FROM THE API: unified name -> etl column
API_DIRECT = {
    "compound_key": "compound_key",
    "source": "source",
    "product_name": "product_name",
    "product_headline": "product_headline",
    # Decision F: one price column, tax-inclusive. Ex-tax is recoverable via
    # detail_tax_percentage, so nothing is lost.
    "product_price": "price_including_tax",
    "product_currency": "currency",
    "product_price_options": "price_options_summary",
    "product_duration_minutes": "duration_minutes",
    "product_main_image": "main_image",
    "product_images": "images",
    "product_category": "tags",
    "location_street": "location_street",
    "location_city": "location_city",
    "location_state": "location_state",
    "location_country": "location_country",
    "location_postcode": "location_postcode",
    "location_latitude": "location_lat",
    "location_longitude": "location_lng",
    "detail_cancellation_hours": "cancellation_hours",
    "detail_tax_percentage": "tax_percentage",
    "detail_pickup_available": "is_pickup_available",
    "meta_supplier_name": "supplier_alias",
}

# BOOKING ONLY - the description side never fills these
BOOKING_ONLY = {
    "detail_booking_notes": "redo_booking_notes",
    "detail_departure_info": "redo_booking_departure_info",   # Decision D: NOT merged
    "detail_before_arrival": "redo_booking_before_arrival",
    "detail_what_not_to_bring": "redo_booking_what_not_to_bring",
    "detail_special_requirements": "redo_booking_special_requirements",
    "detail_operator_contact": "redo_booking_contact",        # Decision E: raw blob
}

DEV_COLUMNS = [
    # Product (10)
    "compound_key", "product_id", "source", "product_name", "product_headline",
    "product_price", "product_currency", "product_price_options",
    "product_duration", "product_duration_minutes",
    # Media & category (3)
    "product_main_image", "product_images", "product_category",
    # Location (7)
    "location_street", "location_city", "location_state", "location_country",
    "location_postcode", "location_latitude", "location_longitude",
    # Detail (21)
    "detail_description", "detail_highlights", "detail_what_is_included",
    "detail_what_is_not_included", "detail_itinerary", "detail_important_info",
    "detail_booking_notes", "detail_meeting_point", "detail_check_in",
    "detail_departure_info", "detail_before_arrival", "detail_what_to_bring",
    "detail_what_not_to_bring", "detail_accessibility", "detail_restrictions",
    "detail_special_requirements", "detail_health_safety", "detail_group_size",
    "detail_faqs", "detail_extras", "detail_disclaimers",
    # Policy & commercial (5)
    "detail_cancellation_policy", "detail_cancellation_hours",
    "detail_tax_percentage", "detail_pricing_notes", "detail_pickup_available",
    # Supplier (2)
    "meta_supplier_name", "detail_operator_contact",
]

INTERNAL_COLUMNS = [
    "compound_key", "meta_raw_description", "meta_raw_booking_notes",
    "meta_desc_flags", "meta_booking_flags", "meta_variant_count",
    "meta_has_structured_desc", "meta_field_sources",
]


# ------------------------------------------------------------------------- loading
def load_booking():
    out, unrepairable = {}, []
    for line in open(BOOK_JSONL, encoding="utf-8"):
        rec = json.loads(line)
        data, note = parse_booking_json(body(rec))
        if data is None:
            unrepairable.append(product_id(rec))
            continue
        out[product_id(rec)] = data
    return out, unrepairable


def load_desc(wanted):
    out, unparseable = {}, []
    for line in open(DESC_JSONL, encoding="utf-8"):
        rec = json.loads(line)
        pid = product_id(rec)
        if pid not in wanted:
            continue
        text = body(rec).strip()
        try:
            out[pid] = json.loads(text)
        except json.JSONDecodeError:
            try:
                out[pid] = json.loads(STRAY_COMMA.sub("}", text))
            except json.JSONDecodeError:
                unparseable.append(pid)
    return out, unparseable


# -------------------------------------------------------------------------- build
def build_row(pid, etl_row, desc, book):
    row, sources, notes = {"product_id": pid}, {"product_id": "api"}, []

    for unified, col in API_DIRECT.items():
        row[unified] = clean(etl_row.get(col))
        sources[unified] = "api" if row[unified] else ""

    for unified, key in BOOKING_ONLY.items():
        row[unified] = clean(book.get(key))
        sources[unified] = "booking" if row[unified] else ""

    row["detail_description"] = clean(desc.get("redo_desc_about"))
    sources["detail_description"] = "desc" if row["detail_description"] else ""
    row["detail_group_size"] = clean(desc.get("redo_group_size"))
    sources["detail_group_size"] = "desc" if row["detail_group_size"] else ""

    for unified, (dk, bk, booking_first) in MERGED.items():
        row[unified], sources[unified] = merge(desc.get(dk), book.get(bk), booking_first)

    # Rule #10: dedicated API field first, extraction second.
    api_cancel = clean(etl_row.get("cancellation_policy"))
    if api_cancel:
        row["detail_cancellation_policy"], sources["detail_cancellation_policy"] = api_cancel, "api"
    else:
        row["detail_cancellation_policy"], sources["detail_cancellation_policy"] = merge(
            desc.get("redo_desc_cancellation"), book.get("redo_booking_cancellation"), True)

    api_dur = clean(etl_row.get("duration_text"))
    if api_dur:
        row["product_duration"], sources["product_duration"] = api_dur, "api"
    else:
        row["product_duration"], sources["product_duration"] = merge(
            desc.get("redo_desc_duration_text"), book.get("redo_booking_duration_text"), False)

    # Booking beats the API here: 15.4% vs 9.6% fill, measured over the 500.
    book_hs = clean(book.get("redo_booking_health_safety"))
    if book_hs:
        row["detail_health_safety"], sources["detail_health_safety"] = book_hs, "booking"
    else:
        api_hs = clean(etl_row.get("health_safety"))
        row["detail_health_safety"], sources["detail_health_safety"] = api_hs, "api" if api_hs else ""

    # REPORT, never delete (blocker F2). 21 of 27 description accessibility values are
    # the literal string "CLICK HERE for accessibility information" - a link, not data.
    # It stays in the column; the internal file records it so it can be found later.
    acc = row["detail_accessibility"]
    if acc and re.search(r"click here", acc, re.I) and len(acc) < 120:
        notes.append("accessibility is link-only text, not accessibility data")

    internal = {
        "compound_key": row["compound_key"],
        "meta_raw_description": clean(etl_row.get("desc_about")),
        "meta_raw_booking_notes": clean(etl_row.get("booking_notes")),
        "meta_desc_flags": clean(desc.get("redo_flags")),
        "meta_booking_flags": clean(book.get("redo_booking_flags")),
        "meta_variant_count": clean(etl_row.get("prototype_count")),
        "meta_has_structured_desc": clean(etl_row.get("has_structured_desc")),
        "meta_field_sources": json.dumps(
            {"sources": {k: v for k, v in sources.items() if v}, "notes": notes},
            ensure_ascii=False),
    }
    return row, internal, sources


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Input checksums (read-only, re-verified after the build):")
    before = {p: sha256(p) for p in (ETL_CSV, DESC_JSONL, BOOK_JSONL)}
    for path, digest in before.items():
        print(f"  {digest[:16]}  {path.name}")

    book, unrepairable = load_booking()
    ids = set(book)
    desc, unparseable = load_desc(ids)
    etl = pd.read_csv(ETL_CSV, dtype=str, low_memory=False)
    etl = etl[etl["product_id"].isin(ids)].set_index("product_id")

    print(f"\nUniverse: {len(ids)} products from the booking V5.4 run")
    print(f"  description V5.3 found : {len(desc)}")
    print(f"  API/ETL rows matched   : {len(etl)}")
    if unrepairable:
        print(f"  !! booking JSON unrepairable: {unrepairable}")
    if unparseable:
        print(f"  !! description JSON unparseable: {unparseable}")

    missing_desc = sorted(ids - set(desc))
    missing_etl = sorted(ids - set(etl.index))
    if missing_desc:
        print(f"  !! {len(missing_desc)} products have no description row: {missing_desc[:5]}")
    if missing_etl:
        print(f"  !! {len(missing_etl)} products have no ETL row: {missing_etl[:5]}")

    dev_rows, int_rows, all_sources = [], [], []
    for pid in sorted(ids):
        if pid not in etl.index or pid not in desc:
            continue
        row, internal, sources = build_row(pid, etl.loc[pid].to_dict(), desc[pid], book[pid])
        dev_rows.append(row)
        int_rows.append(internal)
        all_sources.append(sources)

    dev = pd.DataFrame(dev_rows)
    internal = pd.DataFrame(int_rows)

    # A rename into an existing name silently swaps two columns' data. Assert instead.
    assert len(dev.columns) == len(set(dev.columns)), "duplicate headers in dev table"
    assert len(internal.columns) == len(set(internal.columns)), "duplicate headers in internal"
    missing = set(DEV_COLUMNS) - set(dev.columns)
    extra = set(dev.columns) - set(DEV_COLUMNS)
    assert not missing, f"dev table missing columns: {sorted(missing)}"
    assert not extra, f"dev table has unexpected columns: {sorted(extra)}"
    assert len(DEV_COLUMNS) == 48, f"expected 48 dev columns, spec lists {len(DEV_COLUMNS)}"
    assert len(INTERNAL_COLUMNS) == 8, f"expected 8 internal columns, spec lists {len(INTERNAL_COLUMNS)}"

    dev = dev[DEV_COLUMNS]
    internal = internal[INTERNAL_COLUMNS]

    dev.to_csv(OUT_DIR / "fareharbor_unified.csv", index=False, encoding="utf-8")
    internal.to_csv(OUT_DIR / "fareharbor_internal.csv", index=False, encoding="utf-8")
    dev.map(for_excel).to_excel(OUT_DIR / "fareharbor_unified.xlsx", index=False)

    print(f"\nWrote {len(dev)} rows x {len(dev.columns)} columns -> fareharbor_unified.csv/.xlsx")
    print(f"Wrote {len(internal)} rows x {len(internal.columns)} columns -> fareharbor_internal.csv")

    after = {p: sha256(p) for p in (ETL_CSV, DESC_JSONL, BOOK_JSONL)}
    assert before == after, "an input file was modified during the build"
    print("Inputs unchanged (checksums re-verified).")

    print("\nFill rate per column:")
    for col in DEV_COLUMNS:
        n = int((dev[col].fillna("").astype(str).str.strip() != "").sum())
        bar = "#" * round(n / len(dev) * 28)
        print(f"  {col:30s} {n:4d}  {100*n/len(dev):5.1f}%  {bar}")

    merged_counts = {}
    for src in all_sources:
        for field, note in src.items():
            if note.startswith("desc+booking") or "SAME" in note:
                key = ("REWORDED-REVIEW" if "REWORDED" in note
                       else "DIFFERENT" if "DIFFERENT" in note else "SAME")
                merged_counts[key] = merged_counts.get(key, 0) + 1
    total = sum(merged_counts.values())
    print(f"\nMerge collisions: {total}")
    for band in ("SAME", "REWORDED-REVIEW", "DIFFERENT"):
        n = merged_counts.get(band, 0)
        print(f"  {band:16s} {n:4d}  ({100*n/total:.0f}%)" if total else f"  {band}: 0")


if __name__ == "__main__":
    main()
