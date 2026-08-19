# TDU unified product data — developer README

**Fareharbor · 11,231 products · 59 columns**

This is the first source delivered against the unified schema. Rezdy, Livn,
CustomLinc, Ventus and Ingresso follow later **in the same 59 columns** — so
build against this shape and nothing changes when they arrive, except that
columns currently empty start filling.

| File | What it is |
|---|---|
| `fareharbor_unified_v2.csv` | The data. UTF-8, comma-separated, quoted. |
| `fareharbor_unified_v2.xlsx` | Same data, plus a Schema sheet and a Read me sheet. |
| `unified_schema_sample.html` | 10 worked examples across all six sources. Open it first. |

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
const clean = raw.replace(/^\[[A-Z ]+\]\s*/gm, '');
```

Skip this and agents see `[BOOKING NOTES]` on the page.

**Tags in use:**

| Tag | Meaning |
|---|---|
| `[API]` | A dedicated field the supplier filled in. Most trustworthy — **always listed first**. |
| `[DESCRIPTION]` | Pulled out of the product description by AI. |
| `[BOOKING NOTES]` | Pulled out of the supplier's booking notes by AI. |
| `[ADDITIONAL INFO]` · `[TERMS]` | Other sources. Not used by Fareharbor. |

**77,623 cells** across **22 columns** carry tags in this file.

Blocks are **not de-duplicated**. If a supplier said the same thing twice, you
get it twice. That was deliberate — merging would have destroyed the record of
where each piece came from.

### 2. Prices are already in dollars

The Fareharbor API returns **cents**. This file has divided by 100.
`product_price` of `89.0` means **$89.00**. Do not divide again.

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

Four columns hold JSON as text. `JSON.parse()` them.

### `product_price_options` — one object per ticket type

```json
{
  "label": "1 person",
  "price": 69.0,
  "price_ex_tax": 62.73,
  "price_net": null,
  "age_min": null,
  "age_max": null,
  "min_quantity": null,
  "max_quantity": null,
  "is_vehicle": null,
  "seats_used": null,
  "rate_type": null,
  "note": "1 people",
  "source_option_id": "1200321"
}
```

Keys a source does not supply are `null`. **`note` is worth surfacing** — it
carries age rules in prose (*"Ages 5-12"*, *"60+ and ID Required!"*,
*"Total of 2 people/buggy"*) on products where `age_min` / `age_max` are empty.

### `product_images` — one object per image

```json
{
  "source_image_id": 478160,
  "url": "https://cdn.filestackcontent.com/ZCZmoQTRUZsjOeL1x8AS",
  "is_main": true,
  "thumbnail_url": null,
  "medium_url": null,
  "large_url": null,
  "width": null,
  "height": null,
  "file_size": null,
  "mime_type": null
}
```

`thumbnail_url`, `medium_url` and `large_url` are `null` for Fareharbor — it
ships one size. **Rezdy fills all four**, so build the component to use them
when present.

### `meta_operator_info` — one object per product

```json
{
  "name": null,
  "description": null,
  "phone": null,
  "email": null,
  "website": null,
  "address": null,
  "logo_url": null,
  "contact_text": "For more info or questions please do not reply to this email as we won't see it!\nSend an email to hello@adventuresailing.com.au (hello@adventuresailing.com.au) or call 0428372931\nwww.adventuresailing.com.au"
}
```

Feeds the **Operator Information** panel. For Fareharbor only `contact_text`
is filled, on **253 products (2.3%)** — free text, not parsed into
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
| `product_price_unit` | Fareharbor prices per customer type, not per unit | **Rezdy** — and it matters: some prices are per jetski, boat or hour, not per person |
| `product_min_quantity`, `product_max_quantity` | no quantity limits in the API | Rezdy |
| `product_duration_minutes` | Fareharbor gives prose only, and we never derive numbers | Rezdy, Livn |
| `product_videos` | no video field | Rezdy |
| `detail_operating_days`, `detail_start_time`, `detail_return_time` | not in the API | Livn, CustomLinc |
| `location_end` | no separate finish point | Livn, CustomLinc |

---

## Every column

`Fill` is the share of the 11,231 products with a value.


### Identity

| Column | Type | Fill | What it holds |
|---|---|---|---|
| `compound_key` | text | **100%** | `{product_id}` + `{source}`, pipe-separated. The primary key. Product ids are only unique **within** a source. |
| `product_id` | text | **100%** | The supplier's own product key. **Read as text** — leading zeros and non-numeric codes exist in other sources. |
| `source` | text | **100%** | Always `Fareharbor` in this file. |
| `product_name` | text | **100%** | Product title. |
| `product_headline` | text | **92%** | Short tagline. Fareharbor uses it for attribute chips — *"Age 18+ • Quick and easy"*. **Some contain dates and will go stale.** |

### Operator

| Column | Type | Fill | What it holds |
|---|---|---|---|
| `meta_supplier_id` | text | — | Empty — see *Columns that are empty on purpose*. |
| `meta_supplier_name` | text | — | Empty — same. |
| `meta_operator_info` | JSON | **2%** | Operator details. Feeds the **Operator Information** panel. Only `contact_text` is filled for Fareharbor. |

### Listing & price

| Column | Type | Fill | What it holds |
|---|---|---|---|
| `product_price` | number | **100%** | Lowest ticket price, **already in dollars**. |
| `product_currency` | text | **100%** | ISO code. Always `AUD` here. |
| `product_price_unit` | text | — | What the price is *per*. Empty for Fareharbor — it prices per customer type. |
| `product_price_tax_inclusive` | text | **100%** | `true` / `false` / empty. Empty means **unknown**, not false. |
| `product_price_options` | JSON | **100%** | Every ticket type. See *JSON shapes*. |
| `product_min_quantity` | number | — | Smallest bookable quantity. Empty for Fareharbor. |
| `product_max_quantity` | number | — | Largest. Empty means **not stated**, not unlimited. |
| `product_duration` | text | **78%** | The supplier's own words — `"4 Hours"`, `"All day"`. Not machine-readable. |
| `product_duration_minutes` | number | — | Empty for Fareharbor: it gives prose only and we never derive numbers. |
| `product_category` | text | **59%** | One category string. |
| `product_tags` | JSON | **59%** | JSON array of strings. |

### Location

| Column | Type | Fill | What it holds |
|---|---|---|---|
| `location_street` | text | **71%** | Street address. |
| `location_city` | text | **72%** | City. |
| `location_state` | text | **70%** | State or province. |
| `location_country` | text | **72%** | 2-letter code. |
| `location_postcode` | text | **69%** | **Read as text** — leading zeros matter. |
| `location_latitude` | number | **62%** | Decimal degrees. |
| `location_longitude` | number | **62%** | Decimal degrees. |
| `location_end` | text | — | Finish point where it differs from the start. Empty for Fareharbor. |

### Detail

| Column | Type | Fill | What it holds |
|---|---|---|---|
| `detail_description` | text | **98%** | The main description text. |
| `detail_highlights` | text | **24%** |  |
| `detail_what_is_included` | text | **59%** |  |
| `detail_what_is_not_included` | text | **19%** |  |
| `detail_itinerary` | text | **18%** |  |
| `detail_important_info` | text | **28%** |  |
| `detail_booking_notes` | text | **54%** |  |
| `detail_meeting_point` | text | **66%** | Where to meet. May carry two `[API]` blocks — a meeting-point field and a location note. |
| `detail_check_in` | text | **26%** |  |
| `detail_departure_info` | text | **3%** |  |
| `detail_before_arrival` | text | **2%** |  |
| `detail_what_to_bring` | text | **48%** | Includes items the supplier said **not** to bring, prefixed `Do not bring:`. |
| `detail_accessibility` | text | **11%** |  |
| `detail_restrictions` | text | **25%** |  |
| `detail_special_requirements` | text | **13%** |  |
| `detail_health_safety` | text | **9%** |  |
| `detail_group_size` | text | **23%** |  |
| `detail_faqs` | text | **12%** |  |
| `detail_extras` | text | **11%** |  |
| `detail_disclaimers` | text | **20%** |  |
| `detail_cancellation_policy` | text | **98%** |  |
| `detail_cancellation_hours` | number | **100%** | Hours of notice required. |
| `detail_pricing_notes` | text | **22%** |  |
| `detail_tax_percentage` | number | **100%** | Tax rate as a percent, e.g. `10`. |
| `detail_operating_days` | text | — |  |
| `detail_start_time` | text | — |  |
| `detail_return_time` | text | — |  |
| `detail_languages` | text | **3%** | Comma-separated ISO codes, e.g. `en, pt`. |
| `detail_pickup_available` | text | **100%** | `true` / `false`. |

### Media

| Column | Type | Fill | What it holds |
|---|---|---|---|
| `product_images` | JSON | **97%** | All images. See *JSON shapes*. |
| `product_videos` | JSON | — | Empty for Fareharbor — no video field in its API. |

### Provenance

| Column | Type | Fill | What it holds |
|---|---|---|---|
| `extractions_present` | text | **100%** | `description`, `booking`, `description,booking`, or `none`. |

---

## Coverage and known gaps

Some products have no description or no booking notes. Check
`extractions_present` before assuming a blank is a bug.

| `extractions_present` | Products |
|---|---|
| `description,booking` | 8,185 |
| `description` only | 2,884 |
| `booking` only | 59 |
| `none` | 103 |

**Other things worth knowing:**

- **Operator contact is under-captured.** It was only ever extracted from
  booking notes. Roughly 3–4% of descriptions also carry a phone or email that
  was never asked for, so the true figure is likely 400–800 products rather than
  253. Being addressed separately.
- **The operator name is blank on every row.** Fareharbor's Details API has none.
  It exists in a different TDU endpoint that this build deliberately does not
  read.
- **The catalogue is 11,231, not 11,236.** Five raw files are API error responses —
  access forbidden, or an invalid product id — not products.
- **`detail_accessibility` means different things per source.** Fareharbor writes
  a warning to the customer (*"requires some agility"*); Rezdy lists conditions it
  can accommodate (*"Vision Impaired, Hearing Impaired"*). Both are correct. A
  filter built on Rezdy's keywords will not work on Fareharbor's prose.

---

## A worked row

Product `102322` — *NRMA Insurance SurfGroms Intensive Surf Program - Devonp*

```
product_price          175.0          ← dollars, already converted
product_currency       AUD
location_city          (empty)
detail_cancellation_hours  24
extractions_present    description,booking
```

Open `unified_schema_sample.html` for ten of these, laid out in full across all
six sources.

---

## Questions

The full decision record — every column, why it exists, what was dropped and
why — is `reports/ALL_SOURCES_FIELD_MAP.md`. Each decision is dated and states
the evidence it was based on.

*Generated from `fareharbor_unified_v2.csv` by `scripts/build_dev_readme.py`.
Re-run it after any rebuild and the numbers above update.*
