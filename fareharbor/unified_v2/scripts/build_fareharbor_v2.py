"""Build the Fareharbor catalogue in the agreed unified schema (59 columns).

Inputs, all already on disk - nothing is fetched and nothing is re-extracted:
  data/Fareharbor/*.json                              11,236 raw Details-API files
  exports/all_extractions/description/*.jsonl         11,069 V5.3 outputs
  exports/all_extractions/booking/*.jsonl              8,244 V5.4 outputs

Output: exports/fareharbor_unified_v2.csv

DECISIONS APPLIED (reports/ALL_SOURCES_FIELD_MAP.md):
  · SOURCE TAGS on every text column - [API] / [DESCRIPTION] / [BOOKING NOTES].
    [API] always leads. ALWAYS tagged, even a single block.
  · NO DE-DUPLICATION. Blocks are stacked, never compared or merged.
  · Prices divided by 100 - the Fareharbor API gives CENTS.
  · Location from locations[] (74%), taking type=="primary" else first.
    NOT primary_location (21%), which is a copy of locations[0].
  · locations[].note joins detail_meeting_point as an [API] block.
  · The cover image is ADDED to product_images when absent from images[],
    flagged is_main. 35 of 600 sampled products need this.
  · what_not_to_bring MERGES into what_to_bring, prefixed "Do not bring:".
  · GENERATE NOTHING. A blank means the supplier gave nothing.
  · NO METADATA API. meta_supplier_id / _name are therefore blank for
    Fareharbor - its Details API carries no supplier data at all.

WHY THE RAW TEXTS ARE NOT ADDED AS [API] BLOCKS:
  build_v5_3_full_batch.py feeds the extraction structured_description.description;
  build_booking_v5_4_full_batch.py feeds it item.booking_notes. Those two strings
  ARE the extractions' input, so re-adding them would duplicate every field.
  The OTHER structured_description.* fields were never fed to any extraction and
  are therefore genuine, separate [API] content.
"""
import csv
import glob
import html
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data_pipeline", "batch_api_test"))
from booking_common import parse_booking_json  # noqa: E402

RAW = os.path.join(ROOT, "data", "Fareharbor")
DESC = os.path.join(ROOT, "exports", "all_extractions", "description")
BOOK = os.path.join(ROOT, "exports", "all_extractions", "booking")
OUT = os.path.join(ROOT, "exports", "fareharbor_unified_v2.csv")

# DECIDED 2026-08-20 (manager review): the unified schema carries NO pricing.
# Price reaches the portal from a separate API that is not this project's
# concern, so nine columns were withdrawn - product_price, product_currency,
# product_price_unit, product_price_tax_inclusive, product_price_options,
# product_min_quantity, product_max_quantity, detail_tax_percentage,
# detail_pricing_notes. They are NOT deleted from anywhere: the values are still
# in the raw supplier files and every one is listed in the dropped-fields
# register in reports/ALL_SOURCES_FIELD_MAP.md with the reason. Restoring any of
# them is re-adding a name here plus its build line - nothing was thrown away.
#
# ADDED the same day: detail_onboard_facilities, the Figma "Onboard Facilities"
# section. NO source supplies it - searched all six APIs, zero matching fields;
# the chip text ("Car Park", "Restroom Facilities") exists only as prose inside
# descriptions. The column ships EMPTY and stays empty until a source supplies
# it, because generating it is forbidden. See section 5 of the field map.
COLUMNS = [
    "compound_key", "product_id", "source", "product_name", "product_headline",
    "meta_supplier_id", "meta_supplier_name", "meta_operator_info",
    "product_duration", "product_duration_minutes",
    "product_category", "product_tags",
    "location_street", "location_city", "location_state", "location_country",
    "location_postcode", "location_latitude", "location_longitude", "location_end",
    "detail_description", "detail_highlights", "detail_what_is_included",
    "detail_what_is_not_included", "detail_itinerary", "detail_important_info",
    "detail_booking_notes", "detail_meeting_point", "detail_check_in",
    "detail_departure_info", "detail_before_arrival", "detail_what_to_bring",
    "detail_accessibility", "detail_onboard_facilities", "detail_restrictions",
    "detail_special_requirements",
    "detail_health_safety", "detail_group_size", "detail_faqs", "detail_extras",
    "detail_disclaimers", "detail_cancellation_policy", "detail_cancellation_hours",
    "detail_operating_days", "detail_start_time", "detail_return_time",
    "detail_languages", "detail_pickup_available",
    "product_images", "product_videos", "extractions_present",
]

# Withdrawn 2026-08-20. Kept as a named list, not a comment, so the build can
# assert none of them came back and the register cannot drift from the code.
WITHDRAWN_PRICE = [
    "product_price", "product_currency", "product_price_unit",
    "product_price_tax_inclusive", "product_price_options",
    "product_min_quantity", "product_max_quantity",
    "detail_tax_percentage", "detail_pricing_notes",
]

# Fareharbor returns the literal string "<p>None</p>" for empty structured fields.
EMPTY = {"", "none", "null", "n/a", "-", "<p>none</p>", "[]", "{}"}
# openpyxl rejects these; strip now so an .xlsx export later cannot fail.
CONTROL = re.compile(r"[\000-\010\013\014\016-\037]")


def clean(v):
    if v is None:
        return ""
    s = str(v)
    if s.strip().lower() in EMPTY:
        return ""
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|div|li|h[1-6])>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)                      # decode ONCE - CLAUDE.md
    s = CONTROL.sub("", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def blocks(*pairs):
    """[(label, text), ...] -> tagged blocks, [API] first, blanks dropped."""
    out = []
    for label, text in pairs:
        t = clean(text)
        if t:
            out.append(f"[{label}] {t}")
    return "\n\n".join(out)


def load_extractions(folder, kind):
    """-> {product_id: {field: value}}. Reports parse failures rather than hiding them."""
    data, failed = {}, []
    for path in sorted(glob.glob(os.path.join(folder, "*.jsonl"))):
        for line in io.open(path, encoding="utf-8"):
            rec = json.loads(line)
            pid = rec["custom_id"].split("|")[0]
            try:
                body = rec["response"]["body"]["choices"][0]["message"]["content"]
            except (KeyError, TypeError, IndexError):
                failed.append(pid)
                continue
            parsed, _note = parse_booking_json(body)
            if parsed is None:
                failed.append(pid)
                continue
            data[pid] = parsed
    print(f"  {kind:12s} {len(data):,} parsed, {len(failed)} unparseable")
    return data


def build_row(path, desc, book):
    item = json.load(io.open(path, encoding="utf-8")).get("item") or {}
    if not item:
        return None
    sd = item.get("structured_description") or {}
    pid = str(item.get("pk"))
    d = desc.get(pid, {})
    b = book.get(pid, {})

    r = {c: "" for c in COLUMNS}
    r["product_id"] = pid
    r["source"] = "Fareharbor"
    r["compound_key"] = f"{pid}|Fareharbor"
    r["product_name"] = clean(item.get("name"))
    r["product_headline"] = clean(item.get("headline"))

    # -- supplier: the Details API carries NONE. Metadata API deliberately unused.
    contact = clean(b.get("redo_booking_contact"))
    if contact:
        r["meta_operator_info"] = json.dumps({
            "name": None, "description": None, "phone": None, "email": None,
            "website": None, "address": None, "logo_url": None,
            "contact_text": contact,
        }, ensure_ascii=False)

    # -- price: NOT CARRIED (2026-08-20). The portal takes price from a separate
    # API. item.customer_prototypes[] (cents), item.tax_percentage and
    # structured_description.pricing are still in the raw files and still read
    # correctly by this script's ancestors - see WITHDRAWN_PRICE above.

    # -- duration: prose only. Never derived (section 7).
    r["product_duration"] = blocks(
        ("API", sd.get("duration")),
        ("DESCRIPTION", d.get("redo_desc_duration_text")),
        ("BOOKING NOTES", b.get("redo_booking_duration_text")))

    tags = [clean(t.get("name")) for t in (item.get("tags") or []) if t.get("name")]
    tags = [t for t in tags if t]
    if tags:
        r["product_category"] = tags[0]
        r["product_tags"] = json.dumps(tags, ensure_ascii=False)

    # -- location: locations[], type=="primary" else first
    locs = item.get("locations") or []
    loc = next((x for x in locs if x.get("type") == "primary"), locs[0] if locs else {})
    addr = loc.get("address") or {}
    r["location_street"] = clean(addr.get("street"))
    r["location_city"] = clean(addr.get("city"))
    r["location_state"] = clean(addr.get("province"))
    r["location_country"] = clean(addr.get("country")).upper()
    r["location_postcode"] = clean(addr.get("postal_code"))
    if loc.get("latitude") is not None:
        r["location_latitude"] = loc["latitude"]
    if loc.get("longitude") is not None:
        r["location_longitude"] = loc["longitude"]

    # -- detail. sd.description and booking_notes are NOT re-added: they are the
    #    extractions' own input (see module docstring).
    r["detail_description"] = blocks(("DESCRIPTION", d.get("redo_desc_about")))
    r["detail_highlights"] = blocks(
        ("API", sd.get("highlights")), ("DESCRIPTION", d.get("redo_desc_highlights")),
        ("BOOKING NOTES", b.get("redo_booking_highlights")))
    r["detail_what_is_included"] = blocks(
        ("API", sd.get("what_is_included")), ("DESCRIPTION", d.get("redo_desc_what_included")),
        ("BOOKING NOTES", b.get("redo_booking_what_included")))
    r["detail_what_is_not_included"] = blocks(
        ("API", sd.get("what_is_not_included")),
        ("DESCRIPTION", d.get("redo_desc_what_excluded")),
        ("BOOKING NOTES", b.get("redo_booking_what_excluded")))
    r["detail_itinerary"] = blocks(
        ("API", sd.get("itinerary")), ("DESCRIPTION", d.get("redo_desc_itinerary")),
        ("BOOKING NOTES", b.get("redo_booking_itinerary")))
    r["detail_important_info"] = blocks(
        ("DESCRIPTION", d.get("redo_desc_important_info")),
        ("BOOKING NOTES", b.get("redo_booking_important_info")))
    r["detail_booking_notes"] = blocks(("BOOKING NOTES", b.get("redo_booking_notes")))
    r["detail_meeting_point"] = blocks(
        ("API", sd.get("meeting_point")), ("API", loc.get("note")),
        ("DESCRIPTION", d.get("redo_meeting_point")),
        ("BOOKING NOTES", b.get("redo_booking_meeting_point")))
    r["detail_check_in"] = blocks(
        ("API", sd.get("check_in_details")), ("DESCRIPTION", d.get("redo_desc_check_in")),
        ("BOOKING NOTES", b.get("redo_booking_check_in")))
    r["detail_departure_info"] = blocks(
        ("BOOKING NOTES", b.get("redo_booking_departure_info")))
    r["detail_before_arrival"] = blocks(
        ("BOOKING NOTES", b.get("redo_booking_before_arrival")))

    # what_not_to_bring merges in, negation preserved (section 5 decision 3a)
    notbring = clean(b.get("redo_booking_what_not_to_bring"))
    r["detail_what_to_bring"] = blocks(
        ("API", sd.get("what_to_bring")), ("DESCRIPTION", d.get("redo_desc_what_to_bring")),
        ("BOOKING NOTES", b.get("redo_booking_what_to_bring")),
        ("BOOKING NOTES", f"Do not bring: {notbring}" if notbring else ""))

    r["detail_accessibility"] = blocks(
        ("API", sd.get("accessibility")), ("DESCRIPTION", d.get("redo_desc_accessibility")),
        ("BOOKING NOTES", b.get("redo_booking_accessibility")))
    # detail_onboard_facilities is INTENTIONALLY left at "". No Fareharbor field
    # carries it and none of the other five sources do either. The Figma chips
    # ("Car Park", "Restroom Facilities") appear only as prose inside supplier
    # descriptions, and deriving a facilities list from prose is generating a
    # value - the one thing this schema never does. The column exists so the
    # front end can build the section now and so a source that DOES supply it
    # later needs no schema change.
    r["detail_restrictions"] = blocks(
        ("API", sd.get("restrictions")), ("DESCRIPTION", d.get("redo_desc_restrictions")),
        ("BOOKING NOTES", b.get("redo_booking_restrictions")))
    r["detail_special_requirements"] = blocks(
        ("API", sd.get("special_requirements")),
        ("DESCRIPTION", d.get("redo_desc_special_requirements")),
        ("BOOKING NOTES", b.get("redo_booking_special_requirements")))
    r["detail_health_safety"] = blocks(
        ("API", item.get("health_and_safety_policy")),
        ("BOOKING NOTES", b.get("redo_booking_health_safety")))
    r["detail_group_size"] = blocks(
        ("API", sd.get("group_size")), ("DESCRIPTION", d.get("redo_group_size")),
        ("BOOKING NOTES", b.get("redo_booking_group_size")))
    faq_items = sd.get("faq_items") or []
    faq_api = " ".join(f"{clean(x.get('question'))} {clean(x.get('answer'))}"
                       for x in faq_items) if faq_items else sd.get("faqs")
    r["detail_faqs"] = blocks(
        ("API", faq_api), ("DESCRIPTION", d.get("redo_desc_faqs")),
        ("BOOKING NOTES", b.get("redo_booking_faqs")))
    r["detail_extras"] = blocks(
        ("API", sd.get("extras")), ("DESCRIPTION", d.get("redo_desc_extras")),
        ("BOOKING NOTES", b.get("redo_booking_extras")))
    r["detail_disclaimers"] = blocks(
        ("API", sd.get("disclaimers")), ("DESCRIPTION", d.get("redo_desc_disclaimers")),
        ("BOOKING NOTES", b.get("redo_booking_disclaimers")))
    r["detail_cancellation_policy"] = blocks(
        ("API", item.get("cancellation_policy")), ("API", sd.get("cancellation_summary")),
        ("DESCRIPTION", d.get("redo_desc_cancellation")),
        ("BOOKING NOTES", b.get("redo_booking_cancellation")))
    ecp = item.get("effective_cancellation_policy") or {}
    if ecp.get("cutoff_hours_before") is not None:
        r["detail_cancellation_hours"] = ecp["cutoff_hours_before"]
    # detail_pricing_notes withdrawn with the rest of the price block.

    langs = [clean(x.get("language_code")) for x in (sd.get("guided_languages") or [])]
    r["detail_languages"] = ", ".join(x for x in langs if x)
    if item.get("is_pickup_ever_available") is not None:
        r["detail_pickup_available"] = str(item["is_pickup_ever_available"]).lower()

    # -- images: the cover is sometimes a photo found nowhere in images[]
    cover = item.get("image_cdn_url")
    gallery = item.get("images") or []
    urls = [g.get("image_cdn_url") for g in gallery]
    imgs = []
    if cover and cover not in urls:
        imgs.append({"source_image_id": None, "url": cover, "is_main": True,
                     "thumbnail_url": None, "medium_url": None, "large_url": None,
                     "width": None, "height": None, "file_size": None, "mime_type": None})
    for g in gallery:
        u = g.get("image_cdn_url")
        imgs.append({"source_image_id": g.get("pk"), "url": u,
                     "is_main": bool(cover) and u == cover,
                     "thumbnail_url": None, "medium_url": None, "large_url": None,
                     "width": None, "height": None, "file_size": None, "mime_type": None})
    if imgs and not any(i["is_main"] for i in imgs):
        imgs[0]["is_main"] = True
    if imgs:
        r["product_images"] = json.dumps(imgs, ensure_ascii=False)

    present = []
    if pid in desc:
        present.append("description")
    if pid in book:
        present.append("booking")
    r["extractions_present"] = ",".join(present) if present else "none"
    return r


def main():
    print("loading extractions")
    desc = load_extractions(DESC, "description")
    book = load_extractions(BOOK, "booking")

    files = sorted(glob.glob(os.path.join(RAW, "*.json")))
    print(f"\nreading {len(files):,} raw products")

    rows, skipped = [], 0
    for n, path in enumerate(files, 1):
        try:
            row = build_row(path, desc, book)
        except Exception as exc:                                   # noqa: BLE001
            print(f"  ! {os.path.basename(path)}: {exc}")
            skipped += 1
            continue
        if row is None:
            skipped += 1
            continue
        rows.append(row)
        if n % 2500 == 0:
            print(f"  {n:,}")

    seen = {}
    for r in rows:
        seen.setdefault(r["compound_key"], 0)
        seen[r["compound_key"]] += 1
    dupes = [k for k, v in seen.items() if v > 1]
    if dupes:
        raise SystemExit(f"duplicate compound keys: {dupes[:5]}")

    # The 2026-08-20 withdrawal, asserted rather than trusted. A price column
    # reintroduced by a merge would otherwise ship silently.
    back = [c for c in WITHDRAWN_PRICE if c in COLUMNS]
    if back:
        raise SystemExit(f"withdrawn price columns are back in COLUMNS: {back}")
    leaked = sorted({c for r in rows for c in r if c not in COLUMNS})
    if leaked:
        raise SystemExit(f"rows carry columns not in COLUMNS: {leaked}")
    if any(str(r["detail_onboard_facilities"]).strip() for r in rows):
        raise SystemExit("detail_onboard_facilities is filled - no source "
                         "supplies it, so a value here was generated")

    with io.open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    print(f"\nwrote {OUT}")
    print(f"  {len(rows):,} rows x {len(COLUMNS)} columns   (skipped {skipped})")
    print("\nfill by column:")
    for c in COLUMNS:
        n = sum(1 for r in rows if str(r[c]).strip())
        print(f"  {c:32s} {n:6,}  {n / len(rows) * 100:5.1f}%")


if __name__ == "__main__":
    main()
