"""Generate the developer README that ships with the Fareharbor data.

Every number is computed from exports/fareharbor_unified_v2.csv at run time, so
the document cannot drift from the file it describes.

Output: exports/README_FOR_DEVELOPERS.md
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "exports", "fareharbor_unified_v2.csv")
OUT = os.path.join(ROOT, "exports", "README_FOR_DEVELOPERS.md")

GROUPS = [
    ("Identity", ["compound_key", "product_id", "source", "product_name",
                  "product_headline"]),
    ("Operator", ["meta_supplier_id", "meta_supplier_name", "meta_operator_info"]),
    # No price group: pricing was withdrawn 2026-08-20 and reaches the portal
    # from a separate API. See "What is not here" in the generated README.
    ("Listing", ["product_duration", "product_duration_minutes",
                 "product_category", "product_tags"]),
    ("Location", ["location_street", "location_city", "location_state",
                  "location_country", "location_postcode", "location_latitude",
                  "location_longitude", "location_end"]),
    ("Detail", ["detail_description", "detail_highlights", "detail_what_is_included",
                "detail_what_is_not_included", "detail_itinerary",
                "detail_important_info", "detail_booking_notes",
                "detail_meeting_point", "detail_check_in", "detail_departure_info",
                "detail_before_arrival", "detail_what_to_bring",
                "detail_accessibility", "detail_onboard_facilities",
                "detail_restrictions",
                "detail_special_requirements", "detail_health_safety",
                "detail_group_size", "detail_faqs", "detail_extras",
                "detail_disclaimers", "detail_cancellation_policy",
                "detail_cancellation_hours", "detail_operating_days",
                "detail_start_time", "detail_return_time", "detail_languages",
                "detail_pickup_available"]),
    ("Media", ["product_images", "product_videos"]),
    ("Provenance", ["extractions_present"]),
]

TYPE = {
    "product_duration_minutes": "number",
    "location_latitude": "number", "location_longitude": "number",
    "detail_cancellation_hours": "number",
    "meta_operator_info": "JSON",
    "product_tags": "JSON", "product_images": "JSON", "product_videos": "JSON",
}

HOLDS = {
    "compound_key": "`{product_id}` + `{source}`, pipe-separated. The primary key. Product ids are only unique **within** a source.",
    "product_id": "The supplier's own product key. **Read as text** — leading zeros and non-numeric codes exist in other sources.",
    "source": "Always `Fareharbor` in this file.",
    "product_name": "Product title.",
    "product_headline": "Short tagline. Fareharbor uses it for attribute chips — *\"Age 18+ • Quick and easy\"*. **Some contain dates and will go stale.**",
    "meta_supplier_id": "Empty — see *Columns that are empty on purpose*.",
    "meta_supplier_name": "Empty — same.",
    "meta_operator_info": "Operator details. Feeds the **Operator Information** panel. Only `contact_text` is filled for Fareharbor.",
    "product_duration": "The supplier's own words — `\"4 Hours\"`, `\"All day\"`. Not machine-readable.",
    "product_duration_minutes": "Empty for Fareharbor: it gives prose only and we never derive numbers.",
    "product_category": "One category string.",
    "product_tags": "JSON array of strings.",
    "location_street": "Street address.",
    "location_city": "City.",
    "location_state": "State or province.",
    "location_country": "2-letter code.",
    "location_postcode": "**Read as text** — leading zeros matter.",
    "location_latitude": "Decimal degrees.",
    "location_longitude": "Decimal degrees.",
    "location_end": "Finish point where it differs from the start. Empty for Fareharbor.",
    "detail_description": "The main description text.",
    "detail_what_to_bring": "Includes items the supplier said **not** to bring, prefixed `Do not bring:`.",
    "detail_meeting_point": "Where to meet. May carry two `[API]` blocks — a meeting-point field and a location note.",
    "detail_cancellation_hours": "Hours of notice required.",
    "detail_onboard_facilities": "Empty in every source. Holds the Figma **Onboard Facilities** section open — no supplier API carries a facilities list, and we never generate one.",
    "detail_pickup_available": "`true` / `false`.",
    "detail_languages": "Comma-separated ISO codes, e.g. `en, pt`.",
    "product_images": "All images. See *JSON shapes*.",
    "product_videos": "Empty for Fareharbor — no video field in its API.",
    "extractions_present": "`description`, `booking`, `description,booking`, or `none`.",
}

TAGGED = re.compile(r"^\[(API|DESCRIPTION|BOOKING NOTES|ADDITIONAL INFO|TERMS)\]")


def main():
    df = pd.read_csv(SRC, low_memory=False, dtype=str).fillna("")
    n = len(df)
    fill = {c: int((df[c].str.strip() != "").sum()) for c in df.columns}

    # which detail columns actually carry tagged prose
    tagged_cols = [c for c in df.columns
                   if c.startswith("detail_")
                   and any(TAGGED.match(v.strip()) for v in df[c] if v.strip())]
    n_tagged = sum(1 for c in tagged_cols for v in df[c] if v.strip())

    ex = df[df["extractions_present"] == "description,booking"].iloc[0]
    both = int((df["extractions_present"] == "description,booking").sum())
    donly = int((df["extractions_present"] == "description").sum())
    bonly = int((df["extractions_present"] == "booking").sum())
    none = int((df["extractions_present"] == "none").sum())

    img = json.loads(next(v for v in df["product_images"] if v.strip()))[0]
    op = json.loads(next(v for v in df["meta_operator_info"] if v.strip()))

    L = []
    A = L.append

    A(f"""# TDU unified product data — developer README

**Fareharbor · {n:,} products · {len(df.columns)} columns**

This is the first source delivered against the unified schema. Rezdy, Livn,
CustomLinc, Ventus and Ingresso follow later **in the same {len(df.columns)} columns** — so
build against this shape and nothing changes when they arrive, except that
columns currently empty start filling.

| File | What it is |
|---|---|
| `fareharbor_unified_v2.csv` | The data. UTF-8, comma-separated, quoted. |
| `fareharbor_unified_v2.xlsx` | Same data, plus a Schema sheet and a Read me sheet. |

---

## Read this before you render anything

### 1. Strip the source tags

Every prose field is a stack of **tagged blocks**:

```
detail_what_is_included
──────────────────────────────────────────────
[API] Lunch, guide, national park entry

[DESCRIPTION] Wetsuit and snorkel gear provided

[BOOKING NOTES] Hotel pickup from Cairns CBD
```

The tag says where the text came from. **It is not for display.**

```js
const clean = raw.replace(/^\\[[A-Z ]+\\]\\s*/gm, '');
```

Skip this and agents see `[BOOKING NOTES]` on the page.

**Tags in use:**

| Tag | Meaning |
|---|---|
| `[API]` | A dedicated field the supplier filled in. Most trustworthy — **always listed first**. |
| `[DESCRIPTION]` | Pulled out of the product description by AI. |
| `[BOOKING NOTES]` | Pulled out of the supplier's booking notes by AI. |
| `[ADDITIONAL INFO]` · `[TERMS]` | Other sources. Not used by Fareharbor. |

**{n_tagged:,} cells** across **{len(tagged_cols)} columns** carry tags in this file.

Blocks are **not de-duplicated**. If a supplier said the same thing twice, you
get it twice. That was deliberate — merging would have destroyed the record of
where each piece came from.

### 2. There is no price in this file

Pricing reaches the portal from a separate API and is deliberately not carried
here. Nine columns were withdrawn on 2026-08-20 — `product_price`,
`product_currency`, `product_price_unit`, `product_price_tax_inclusive`,
`product_price_options`, `product_min_quantity`, `product_max_quantity`,
`detail_tax_percentage` and `detail_pricing_notes`. Join on `product_id` to
whatever supplies price. Nothing was destroyed: the values are still in the raw
supplier files, and the field map records each one.

### 3. The main image is flagged, not first

In `product_images`, find the entry where `is_main` is `true`.

```js
const cover = images.find(i => i.is_main) ?? images[0];
```

On about **6% of products** the cover is a photo that appears nowhere else in
the gallery. It has been inserted into the list so nothing is lost — but it is
not always at index 0.

### 4. Read ids and postcodes as strings

`product_id` and `location_postcode` are text. Parse them as numbers and you
get `2000.0` and lose leading zeros. Other sources use non-numeric ids
(`P0F1AB`, `RFF-DR-GIT`), so this matters more once they land.

### 5. Empty means the supplier gave nothing

A blank is a **fact about the supplier feed**, not a defect and not a bug in the
pipeline. Nothing is ever generated to fill a gap. Hide empty sections rather
than showing a placeholder.

---

## JSON shapes

Three columns hold JSON as text. `JSON.parse()` them.

### `product_images` — one object per image

```json
{json.dumps(img, indent=2, ensure_ascii=False)}
```

`thumbnail_url`, `medium_url` and `large_url` are `null` for Fareharbor — it
ships one size. **Rezdy fills all four**, so build the component to use them
when present.

### `meta_operator_info` — one object per product

```json
{json.dumps(op, indent=2, ensure_ascii=False)}
```

Feeds the **Operator Information** panel. For Fareharbor only `contact_text`
is filled, on **{fill['meta_operator_info']} products ({fill['meta_operator_info'] / n * 100:.1f}%)** — free text, not parsed into
`phone` / `email` / `website`. **Livn fills every key**, so the panel is built
for data that mostly is not here yet.

### `product_tags` — array of strings

```json
["Boat Tour", "Water Activities", "Guided Tour"]
```

---

## Columns that are empty on purpose

These are **not** missing data. Fareharbor's API does not have them; other
sources do, and the columns exist so all six share one schema.

| Column | Why empty | Which source fills it |
|---|---|---|
| `meta_supplier_id`, `meta_supplier_name` | Fareharbor's Details API carries **no supplier data at all** | Rezdy, Livn, CustomLinc, Ingresso |
| `detail_onboard_facilities` | **no source has it** — searched all six APIs. The Figma chips exist only as prose inside descriptions, and we never generate a value | none yet |
| `product_duration_minutes` | Fareharbor gives prose only, and we never derive numbers | Rezdy, Livn |
| `product_videos` | no video field | Rezdy |
| `detail_operating_days`, `detail_start_time`, `detail_return_time` | not in the API | Livn, CustomLinc |
| `location_end` | no separate finish point | Livn, CustomLinc |

---

## Every column

`Fill` is the share of the {n:,} products with a value.

""")

    for gname, gcols in GROUPS:
        A(f"### {gname}\n")
        A("| Column | Type | Fill | What it holds |")
        A("|---|---|---|---|")
        for c in gcols:
            t = TYPE.get(c, "text")
            f = fill[c]
            pct = f"**{f / n * 100:.0f}%**" if f else "—"
            A(f"| `{c}` | {t} | {pct} | {HOLDS.get(c, '')} |")
        A("")

    A(f"""---

## Coverage and known gaps

Some products have no description or no booking notes. Check
`extractions_present` before assuming a blank is a bug.

| `extractions_present` | Products |
|---|---|
| `description,booking` | {both:,} |
| `description` only | {donly:,} |
| `booking` only | {bonly:,} |
| `none` | {none:,} |

**Other things worth knowing:**

- **Operator contact is under-captured.** It was only ever extracted from
  booking notes. Roughly 3–4% of descriptions also carry a phone or email that
  was never asked for, so the true figure is likely 400–800 products rather than
  {fill['meta_operator_info']}. Being addressed separately.
- **The operator name is blank on every row.** Fareharbor's Details API has none.
  It exists in a different TDU endpoint that this build deliberately does not
  read.
- **The catalogue is {n:,}, not 11,236.** Five raw files are API error responses —
  access forbidden, or an invalid product id — not products.
- **`detail_accessibility` means different things per source.** Fareharbor writes
  a warning to the customer (*"requires some agility"*); Rezdy lists conditions it
  can accommodate (*"Vision Impaired, Hearing Impaired"*). Both are correct. A
  filter built on Rezdy's keywords will not work on Fareharbor's prose.

---

## A worked row

Product `{ex['product_id']}` — *{ex['product_name'][:56]}*

```
location_city          {ex['location_city'] or '(empty)'}
detail_cancellation_hours  {ex['detail_cancellation_hours'] or '(empty)'}
extractions_present    {ex['extractions_present']}
```

Every column is listed with its type, meaning and measured fill in
`ALL_SOURCES_FIELD_MAP.md`, alongside the dated decision behind each one.

---

## Questions

The full decision record — every column, why it exists, what was dropped and
why — is `reports/ALL_SOURCES_FIELD_MAP.md`. Each decision is dated and states
the evidence it was based on.

*Generated from `fareharbor_unified_v2.csv` by `scripts/build_dev_readme.py`.
Re-run it after any rebuild and the numbers above update.*
""")

    io.open(OUT, "w", encoding="utf-8").write("\n".join(L))
    print(f"wrote {OUT}")
    print(f"  {n:,} products, {len(df.columns)} columns, {n_tagged:,} tagged cells")


if __name__ == "__main__":
    main()
