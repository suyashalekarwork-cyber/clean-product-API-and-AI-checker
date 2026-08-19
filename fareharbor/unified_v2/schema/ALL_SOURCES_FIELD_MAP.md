# All sources ↔ unified schema — raw API field map

*2026-08-19. Six sources: **Fareharbor, Rezdy, Livn, CustomLinc, Ventus,
Ingresso**. TDU excluded (no Stage 1 or Stage 2 pipeline exists — see
`SCHEMA_DECISIONS_REQUIRED.md` scope note).*

Built from the measured structure docs in `reports/api_structure/`, not from the
schema tables. Companion to `FAREHARBOR_REZDY_FIELD_MAP.md`, which covers the
two large sources in more depth.

| Source | Products | Sampled | Field paths | Always empty |
|---|---|---|---|---|
| Fareharbor | 11,236 | 1,199 | 122 | 2 |
| Rezdy | 9,373 | 1,199 | 115 | 0 |
| Livn | 167 | all | 145 | 0 |
| CustomLinc | 24 | all | 171 | **40** |
| Ventus | 19 | all | 39 | 0 |
| Ingresso | 16 | all | 120 | 5 |

**20,835 products. Fareharbor and Rezdy are 98.9% of them.** The four small
sources are 226 products combined — 1.1%. Worth remembering when a decision is
framed as "six sources": it is really two sources and four long-tail exceptions.

---

## THE 59 COLUMNS — description and measured fill

*Catalogue fill = the share of all **20,835** products where the source supplies a
value, weighting each source by its product count. Computed from
`reports/api_structure/`; nothing estimated.*

> **¹ marks a column filled by EXTRACTION, where the figure is an UPPER BOUND.**
> Those columns fill only when a supplier wrote a heading naming the field, so the
> built column is lower than the raw text it is drawn from — Fareharbor's raw
> `structured_description.highlights` is 19.6% while the built `detail_highlights`
> is 5.2%. Columns without ¹ are read straight from a field and the figure is real.
>
> **Fareharbor is 54% of the catalogue and Rezdy 45%** — the other four sources are
> 226 products (1.1%), so a column only they fill reads near 0% here even at 100%
> of their own products.

| Column | Type | What it holds | Products | Catalogue fill |
|---|---|---|---|---|
| **IDENTITY** | | | | |
| `product_id` | `str` | Supplier product key. Text always. | 20,816 | **100%** |
| `source` | `str` | Which supplier system. | 20,835 | **100%** |
| `product_name` | `str` | Product title. | 20,835 | **100%** |
| `product_headline` | `str` | Short tagline. | 19,900 | **96%** |
| **SUPPLIER  (internal, never displayed)** | | | | |
| `meta_supplier_id` | `str` | Supplier key. | 9,580 | **46%** |
| `meta_supplier_name` | `str` | Supplier company name. | 9,580 | **46%** |
| **LISTING & PRICE** | | | | |
| `product_price` | `float` | Headline price. Fareharbor is CENTS. | 20,835 | **100%** |
| `product_currency` | `str` | Currency code, uppercased. | 9,580 | **46%** |
| `product_price_unit` | `str` | What the price is per. **D5.** | 9,416 | **45%** |
| `product_price_tax_inclusive` | `str` | true / false / unknown. **D6.** | 5,127 | **25%** |
| `product_price_options` | `JSON` | Every ticket type, 13 keys. | 20,602 | **99%** |
| `product_min_quantity` | `float` | Smallest bookable quantity. | 9,373 | **45%** |
| `product_max_quantity` | `float` | Largest. Null = not stated. | 7,618 | **37%** |
| `product_duration` | `str` | Supplier's own words. | 4,855 | **23%** |
| `product_duration_minutes` | `float` | Minutes, only where given as a number. | 8,931 | **43%** |
| `product_category` | `str` | What kind of thing this is. | 13,234 | **64%** |
| `product_tags` | `JSON` | Filterable attributes. | 13,189 | **63%** |
| **LOCATION** | | | | |
| `location_street` | `str` | Street address. | 15,685 | **75%** |
| `location_city` | `str` | City. | 16,328 | **78%** |
| `location_state` | `str` | State / province. | 15,791 | **76%** |
| `location_country` | `str` | Country, normalised to 2 letters. | 16,988 | **82%** |
| `location_postcode` | `str` | Postcode. | 15,610 | **75%** |
| `location_latitude` | `float` | GPS latitude. | 17,841 | **86%** |
| `location_longitude` | `float` | GPS longitude. | 17,841 | **86%** |
| `location_end` | `str` | Finish point where different. | 169 | **1%** |
| **DETAIL** | | | | |
| `detail_description` | `str` | Main description. Default home for un-headed text. | 20,640 | **99%** |
| `detail_highlights` | `str` | Key selling points. | 2,369 | **11%** ¹ |
| `detail_what_is_included` | `str` | What's included. | 4,534 | **22%** ¹ |
| `detail_what_is_not_included` | `str` | What's excluded. | 1,697 | **8%** ¹ |
| `detail_itinerary` | `str` | Route / day-by-day. | 1,819 | **9%** ¹ |
| `detail_important_info` | `str` | General notes, catch-all. | 3,899 | **19%** ¹ |
| `detail_booking_notes` | `str` | Booking notes. | 12,258 | **59%** ¹ |
| `detail_meeting_point` | `str` | Where to meet. | 5,411 | **26%** ¹ |
| `detail_check_in` | `str` | Arrival instructions. | 2,343 | **11%** ¹ |
| `detail_departure_info` | `str` | Departure details. | — | *extraction only* |
| `detail_before_arrival` | `str` | Before you arrive. | — | *extraction only* |
| `detail_what_to_bring` | `str` | What to bring, incl. "Do not bring". | 2,684 | **13%** ¹ |
| `detail_accessibility` | `str` | Accessibility. | 7,469 | **36%** ¹ |
| `detail_restrictions` | `str` | Who can take part. | 7,941 | **38%** ¹ |
| `detail_special_requirements` | `str` | Dietary, medical, disability needs. | 1,572 | **8%** ¹ |
| `detail_health_safety` | `str` | Health & safety. | 772 | **4%** ¹ |
| `detail_group_size` | `str` | Group size in prose. | 2,277 | **11%** ¹ |
| `detail_faqs` | `str` | FAQs. | 1,247 | **6%** ¹ |
| `detail_extras` | `str` | Optional add-ons. | 4,603 | **22%** ¹ |
| `detail_disclaimers` | `str` | Legal text. | 5,186 | **25%** ¹ |
| `detail_cancellation_policy` | `str` | Cancellation policy. | 14,267 | **68%** ¹ |
| `detail_cancellation_hours` | `float` | Notice period. Rezdy is DAYS. | 18,423 | **88%** |
| `detail_pricing_notes` | `str` | How pricing works + D6 fees. | 6,024 | **29%** ¹ |
| `detail_tax_percentage` | `float` | Tax rate as a percent. | 16,326 | **78%** |
| `detail_operating_days` | `str` | Which days it runs. | 171 | **1%** |
| `detail_start_time` | `str` | Departure time or window. | 187 | **1%** |
| `detail_return_time` | `str` | Return time. | 24 | **0%** |
| `detail_languages` | `str` | Guided languages. | 9,659 | **46%** |
| `detail_pickup_available` | `str` | Whether pickup is offered. | 13,800 | **66%** |
| **MEDIA** | | | | |
| `product_images` | `JSON` | All images, cover flagged is_main. | 19,842 | **95%** |
| `product_videos` | `JSON` | Videos with platform. | 1,359 | **7%** |
| **PROVENANCE** | | | | |
| `compound_key` | `str` | product_id + source. The primary key. | 20,835 | **100%** |
| `extractions_present` | `str` | Which extractions ran on this product. | 20,835 | **100%** |

---

## STILL OPEN

*Updated 2026-08-19. Everything else is settled — the full register is at the
end of this document.*

### Needs a decision

| # | Item | What is blocking it |
|---|---|---|
| 1 | **6 ratings fields** — Google rating & count, TripAdvisor rating, reviews, ranking, badge | No Figma section for ratings, and Fareharbor is the only source with them. Present on 100% of Fareharbor products in the raw API, so nothing is lost by waiting. |
| 2 | **Rezdy `extras[].image`** (33.1%) | No Figma design for a priced add-on with a picture. The extras text ships; only the images are parked. |
| 3 | **Operator name for Fareharbor** | Sitting in `products_raw.json` on 10,943/10,943 products, including *"Fantasea Cruising"* — the operator in the Figma mock-up. Blank on every row because the Metadata API is deliberately unused. **Reversible at any time.** |

### Needs work, not a decision

| # | Item | Size of the job |
|---|---|---|
| 4 | **Contact details are under-captured** — 253 products, true figure likely 400–800 | Contact was only ever extracted from booking notes; the description prompt has 22 fields and none is contact. Needs a prompt change and a re-run of 11,069 products. |
| 5 | **Five sources not yet built** — Rezdy, Livn, CustomLinc, Ventus, Ingresso | Fareharbor is done (`exports/fareharbor_unified_v2.csv`). Rezdy's description extraction is mid-ladder; the other four have had no extraction pass at all. |
| 6 | **TDU has no pipeline** | No Stage 1, no Stage 2, no rows anywhere. The only source entirely absent. |
| 7 | **Dead image URLs unchecked** | Needs HTTP requests to ~20,000 URLs. Before launch, not part of schema design. |

### Known and accepted, no action planned

- **`detail_accessibility` means different things per source.** Fareharbor writes a
  warning to the customer (*"requires some agility"*); Rezdy lists conditions it can
  accommodate (*"Vision Impaired, Hearing Impaired"*). A filter built on Rezdy's
  keywords will not work on Fareharbor's prose.
- **Text is not de-duplicated.** Source tags preserve provenance instead; the
  rapidfuzz merge remains available and can be run over the tagged output later.
- **`exports/fareharbor_unified_full.csv` (the old 49-column file) is not rebuilt.**
  It keeps the review site on port 5056 working. Superseded by `_v2`.

---

## How to read this

**FILL %** = share of sampled products with a real value. Present-but-empty
(`""`, `[]`, `{}`, `null`, Fareharbor's literal `"<p>None</p>"`) does not count.

`—` means the source has no field for this concept at all. A blank column for
that source is **correct**, not a gap.

Wrapper keys differ per source and are not stripped:

| Source | Wrapper |
|---|---|
| Fareharbor | `item.*` |
| Rezdy | `product.*` (plus a `requestStatus` envelope) |
| Livn, CustomLinc, Ventus | root level, no wrapper |
| Ingresso | root, but `events_by_id` and `currency_details` are **dynamic keys** — shown as `*` |

---

# 1. IDENTITY

> ### DECIDED — 2026-08-19, Suyash · section 1
>
> **1. `product_id` is stored as TEXT for every source.** Three sources supply an
> int (Fareharbor `pk`, Livn `id`, CustomLinc `uniqueId`), two a string (Rezdy
> `productCode`, Ingresso `event_id`). A mixed column would render Livn's `72` as
> `72.0` — the pandas int-promotion problem already recorded for postcodes. The
> compound key `(product_id, source)` keeps Livn `72` distinct from any other
> source's `72`.
>
> | Source | Field used | Type | Example |
> |---|---|---|---|
> | Fareharbor | `pk` | int → text | `102327` |
> | Rezdy | `productCode` | str | `PKGUF6` |
> | Livn | `id` | int → text | `72` |
> | **CustomLinc** | **`code`** | str | `RFF-DR-GIT` |
> | Ingresso | `event_id` | str | `14U5L` |
> | Ventus | **filename** — no internal ID exists | str | `111` |
>
> No duplicate IDs found in any source.
>
> **2. CustomLinc uses `code`, not `uniqueId`.** It is the only source with two
> candidate identifiers. `code` is readable and is what the supplier's own staff
> use, matching Rezdy's readable-string pattern. `uniqueId` (e.g. `75635824`) is
> kept as a second column, nothing discarded.
>
> **3. ⚠ THE FILENAME RULE DOES NOT WORK FOR CUSTOMLINC — read `code` from
> inside the file.** The "product ID = last hyphen segment of the filename" rule
> holds for Fareharbor (300/300), Rezdy (300/300) and Livn (167/167). For
> CustomLinc it **truncates 14 of 24 files**, because the code itself contains
> hyphens:
>
> | `code` in file | filename segment | lost |
> |---|---|---|
> | `RFF-DR-GIT` | `GIT` | `RFF-DR-` |
> | `ITO-0800` | `0800` | `ITO-` |
> | `RFF-DRF-BIT1115` | `BIT1115` | `RFF-DRF-` |
>
> **And it collides:** `BIT1115` and `RFF-DRF-BIT1115` are two different products
> that both reduce to `BIT1115` — one would overwrite the other. CLAUDE.md records
> this as "12/24"; measured it is **14/24**, and the collision is not recorded there.
>
> **4. Ingresso uses `event_id`, not `event_code`.** `event_id` (`14U5L`) matches
> the filename AND the dynamic `events_by_id` key, so all three agree.
> `event_code` is inconsistent — `"66"`, `"n/10524"`, `"n/2204"` — and looks like
> an internal supplier reference.
>
> **5. Ventus IDs are DERIVED, not supplied.** Verified: 0 of 19 files contain any
> internal identifier. The filename (`Ventus-1-111.json` → `111`) is the only
> source of truth, so there is nothing to cross-check against. Recorded here so it
> is visible rather than assumed — if Ventus changes its file naming, those IDs
> break silently. 19 products, so the exposure is small.
>
> **6. `product_headline` keeps whatever the supplier calls a headline.**
>
> | Source | Field | Fill | Contains |
> |---|---|---|---|
> | Fareharbor | `headline` | 92.2% | attribute chips — *"Age 18+ • Quick and easy • Great for couples"* |
> | Rezdy | `shortDescription` | 100% | a marketing sentence |
> | Livn | `nameOriginal` | 100% | the product name in its original language |
>
> These are three different kinds of text, and all three are kept as the supplier
> presents them. *Noted, not a schema problem:* Fareharbor's headline sometimes
> carries dates (*"Available Wed, 16 Jun 2027 – Sat, 19 Jun 2027"*) which will go
> stale — the front end should be aware.
>
> **Checked, not an issue:** product names are near-unique. Fareharbor has 5
> duplicate names in 600 (`"General Admission"` ×3), which is harmless since the
> ID is the key — but a search page will show visually identical rows.



| Unified | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|
| `product_id` | `pk` 100% | `productCode` 100% | `id` 100% | `uniqueId` 100% | — **filename only** | `events_by_id.*.event.event_id` 100% |
| `product_name` | `name` 100% | `name` 100% | `name` 100% | `name` 100% | `name` 100% | `event_desc` 100% |
| `product_headline` | `headline` 92.2% | `shortDescription` 100% | `nameOriginal` 100% | — | — | — |

> **Ventus has no internal ID field on any of its 19 files.** The filename is the
> only source of truth (already recorded in CLAUDE.md). There is nothing to
> cross-check against, so verify structural safety instead.

> **ID types differ.** Fareharbor `int`, Rezdy `string` code (`P0F1AB`), Livn
> `int`, CustomLinc `int`, Ingresso `string`. The compound key
> `(product_id, source)` must treat these as text.

---

# 2. SUPPLIER

> ### DECIDED — 2026-08-19, Suyash · `meta_operator_info` — SUPERSEDES part of section 2 below
>
> **A THIRD supplier column ships: `meta_operator_info`, one JSON object.**
>
> ```json
> {"name": "...", "description": "...", "phone": "...", "email": "...",
>  "website": "...", "address": "...", "logo_url": "...", "contact_text": "..."}
> ```
>
> One shape for every source, `null` where a supplier gives nothing — the same
> rule already used for `product_images` and `product_price_options`.
>
> #### Why this reverses an earlier decision
>
> Section 2 held ten Livn supplier fields back on the grounds that **`meta_*` is
> internal and never displayed.** **That premise was wrong.** The Figma prototype
> has an **Operator Information** section — operator name, a description
> paragraph, then PHONE / EMAIL / WEBSITE / ADDRESS. Supplier data IS
> customer-facing, so the fields have a home and ship.
>
> #### What each source can actually fill
>
> | Source | Products | name | description | phone | email | website | address |
> |---|---|---|---|---|---|---|---|
> | **Livn** | 167 | ✅ 100% | ✅ 100% | ✅ 85% | ✅ 100% | ✅ 100% | ✅ 100% |
> | Rezdy | 9,373 | ✅ 100% | — | — | — | — | — |
> | CustomLinc | 24 | ✅ 100% | — | — | — | — | — |
> | Ingresso | 16 | ✅ 100% | — | — | — | — | — |
> | **Fareharbor** | 11,236 | **—** | — | 253 only | — | — | — |
> | Ventus | 19 | — | — | — | — | — | — |
>
> **Only Livn fills the section properly.** Its `supplier` object maps to the
> Figma layout almost field for field.
>
> #### Fareharbor's `contact_text`
>
> Fareharbor's Details API has **no supplier data at all**. The one thing it has
> is contact details the operator wrote into their booking notes, captured by the
> V5.4 extraction as `redo_booking_contact` — **253 of 11,231 products (2.3%)**:
>
> ```
> Facebook Messenger (m.me/skydivefranz)
> Phone: +64 3 752 0714 · Freephone: 0800 800 702
> "Contact Us For The Latest Weather Call:"  ← skydives and scenic flights
> ```
>
> These land in `contact_text` as free text, not parsed into `phone`/`email`.
> This also settles `detail_operator_contact`, which the 58-column list had
> dropped by oversight: it is **not** a separate column — it is this key.
>
> #### THE METADATA API IS STILL NOT USED — and it costs the operator name
>
> `products_raw.json` carries `supplierName` on **10,943 of 10,943** Fareharbor
> products, including *"Fantasea Cruising"* — the very operator in the Figma
> mock-up. Using it would give every Fareharbor product an operator name.
>
> **Decided: still no.** The Metadata API stays out, as settled in section 8.
> Consequence, stated plainly: **the operator name is blank on all 11,231
> Fareharbor products**, and the Figma Operator Information section will be
> effectively empty for 54% of the catalogue.
>
> Reversible at any time — the file is already on disk.
>
> #### Contact data is UNDER-CAPTURED, and this is not fixed
>
> Contact was only ever extracted from **booking notes**. The description prompt
> has 22 fields and none is contact — it was never asked. Measured on 1,200
> products, with matches read by hand to exclude regex noise:
>
> | | phone | email | website |
> |---|---|---|---|
> | in description text | ~4% | ~2% | ~5% |
> | in booking notes | ~19% | ~12% | — |
>
> So the true figure is likely **400–800 products**, not 253. Closing that needs a
> prompt change and a re-run of 11,069 products. **Not done** — the section stays
> thin for Fareharbor regardless, because name, address and website are absent
> from the API entirely.
>
> ---
>
> ### DECIDED — 2026-08-19, Suyash · section 2
>
> **TWO columns ship. Details API only — the Metadata API is not used here.**
>
> | Column | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
> |---|---|---|---|---|---|---|
> | `meta_supplier_id` | — | `supplierAlias` 100% | `supplier.id` 167/167 | `ocb` 24/24 | — | `source_code` 16/16 |
> | `meta_supplier_name` | — | `supplierName` 100% | `supplier.name` 167/167 | `ocbName` 24/24 | — | `source_desc` 16/16 |
>
> **1. Rezdy uses `supplierAlias` as the identifier, not `supplierId`.** This
> answers **D13**. Measured on 800 products: **485 distinct suppliers, and the
> id ↔ alias ↔ name mapping is perfectly consistent** — no supplier has two
> aliases or two ids. So the two are interchangeable within Rezdy and D13's
> silent-join-failure risk does not arise. The text alias is chosen because it is
> also what the Metadata API returns as `supplierId` (e.g. `gowest-au`).
> `supplierId` (the integer) is **not carried**.
>
> **2. CustomLinc uses `ocb` as the id and `ocbName` as the name.**
> `opcName` — sometimes a code (`"69001"`), sometimes a name (`"LANCELIN 4X4"`),
> undocumented — has no home under this decision. It is a real supplied field, so
> it is **parked in section 10d as unresolved**, not silently dropped.
>
> **3. ⚠ FAREHARBOR AND VENTUS ARE BLANK ON BOTH COLUMNS.**
> Verified: **zero** supplier-related keys across 200 sampled Fareharbor products
> and all 19 Ventus files. Their Details APIs simply do not carry supplier data.
>
> **The current Fareharbor file fills `meta_supplier_name` from the FILENAME**
> (`Fareharbor-24hoursinsydney-252849.json` → `24hoursinsydney`). Under the
> governing rule — *generate nothing; a blank is an acceptable answer* — that is
> **derived, not supplied**, and is therefore dropped.
>
> **Consequence: 11,255 products — 54% of the catalogue — carry no supplier
> value.**
>
> **⚠ CORRECTED.** This block originally justified that as low-impact because
> "supplier data is INTERNAL and is not shown on the website." **That was wrong** —
> the Figma prototype has an Operator Information section, so supplier data IS
> customer-facing. See the `meta_operator_info` decision immediately above, which
> supersedes this reasoning and ships the ten Livn fields that were held here.
>
> **4. Livn's `tnc` (121/167) is not supplier contact data** — it is legal terms
> text, and routes to `detail_disclaimers`.
>
> **5. Livn's name variants are not carried.** `nameCompany` (167/167) and
> `nameTradingAs` (157/167) sit alongside `name`; all three were identical on the
> product inspected. Only `name` ships. *Unverified:* whether they ever differ
> across the full 167.



| Unified | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|
| `meta_supplier_name` | — | `supplierName` 100% | `supplier.name` 100% | `ocbName` 100% | — | `source_desc` 100% |
| `meta_supplier_id` | — | `supplierId` 100% | `supplier.id` 100% | `ocb` 100% | — | `source_code` 100% |
| `meta_supplier_alias` | — | `supplierAlias` 100% | — | — | — | — |
| `meta_supplier_website` | — | — | `supplier.website` 100% | — | — | — |
| `meta_supplier_email` | — | — | `supplier.email` 100% | — | — | — |
| `meta_supplier_phone` | — | — | `supplier.phoneRes` 85.0% | — | — | — |
| `meta_supplier_logo` | — | — | `supplier.logo.url` 100% | — | — | — |
| `meta_supplier_tnc` | — | — | `supplier.tnc` 72.5% | — | — | — |

> **Livn is the richest supplier source by far** — website, email, phone, logo,
> trading name, business number, full postal address. It is also the smallest
> that has them (167 products).
>
> **Fareharbor and Ventus supply no supplier data at all.** Fareharbor's unified
> file fills `meta_supplier_name` from the **filename**, not the API.

---

# 3. PRICE

Each row gives the **path**, the **SOURCE type**, a **real value**, and how many
values the field carries per product. Types were counted across files — 400
random (seed 42) for Fareharbor and Rezdy, every file for the other four.

> **Source type ≠ unified type.** The tables below give the type as it arrives
> from each API. The type the unified column actually stores is different, and is
> given in the summary immediately below. Read that first.

> ### DECIDED — 2026-08-19, Suyash · D5 and D6 — the two price-accuracy decisions
>
> These are the only two schema defects that make an agent **quote a wrong price**
> rather than merely see less information.
>
> ---
>
> #### D5 — `product_price_unit` SHIPS. Store the supplier's word verbatim.
>
> **1,004 of 9,363 Rezdy products (10.7%) price something that is not a person** —
> measured across the full catalogue, not a sample.
>
> | Unit | Products |
> |---|---|
> | Boat | 87 |
> | Jet Ski / Jetski | 57 |
> | Bike | 55 |
> | Hour | 38 |
> | Group | 35 |
> | Vehicle | 23 · Charter 23 · Package 23 |
> | Kayak | 17 · Party 16 · Trike 10 |
>
> **The damage:** Casino Royale (`P0F1AB`) is `advertisedPrice: 199.0`,
> `unitLabel: "Jetski"`, max 8. The portal renders *"$199 per person"*. A jetski
> carries two, so a couple is quoted **double** the real price, and `max 8` means
> eight jetskis — sixteen people — not eight guests.
>
> **NO controlled vocabulary.** There are **308 distinct labels**, including
> non-English ones (`位`). Any mapping list would be incomplete and would fail
> **silently** on the next label a supplier invents. The supplier's own word is
> stored and rendered as *"per {unit}"*.
>
> Rezdy-only in practice: Fareharbor prices per customer prototype and has no such
> field; Ventus's `attribute_name` is always a person type, so it carries no risk.
>
> *An earlier figure of "1,460 / 16%" in `SCHEDULE_DECISIONS_REQUIRED.md` counted
> borderline labels (`Rider`, `Kayaker`) as non-person. Counting those as people
> gives **1,004 / 10.7%**.*
>
> ---
>
> #### D6 — a flag PLUS the fee text. The advertised price is NOT recomputed.
>
> **378 of 9,363 Rezdy products (4.0%)** carry a charge that sits **outside** the
> advertised price. Rezdy states this per charge, via `taxes[].priceInclusive`.
>
> Real record — `P9FC8N`, *Day Tour to Lady Musgrave Island*:
>
> ```
> advertisedPrice           295.00
> taxes[0] GST 10%          priceInclusive: TRUE   ← inside the 295
> taxes[1] EMC/QPWS $11.00  priceInclusive: FALSE  ← EXTRA, per person
> taxes[2] fuel levy 6%     priceInclusive: FALSE  ← EXTRA
>
>   295.00 advertised + 11.00 park fee + 17.70 levy = 323.70 actual
> ```
>
> An agent quoting $295 is **$28.70 (9.7%) short per person** — $114.80 for a
> family of four, discovered at the counter.
>
> **What ships:**
>
> | Column | Value |
> |---|---|
> | `product_price_tax_inclusive` | `"false"` where ANY charge row is non-inclusive |
> | `detail_pricing_notes` | the fee detail as `[API]`-tagged text |
>
> ```
> detail_pricing_notes
> [API] Not included in the advertised price:
>       EMC/QPWS $11.00 per person
>       Fuel levy 6%
> ```
>
> **The price is NOT recomputed.** Two reasons. The charges come in **three
> shapes** — `PERCENT` (202), `FIXED_PER_QUANTITY` (95), `FIXED_PER_ORDER` (56) —
> and a per-order fee cannot be resolved without knowing the party size, which a
> browse-only portal does not have. And `$295` is the price the **supplier**
> advertises; republishing `$323.70` would be publishing a price they did not set.
>
> **`product_price_tax_inclusive` is TEXT with three states, not a boolean:**
>
> | Source | Value | Why |
> |---|---|---|
> | Rezdy | `"true"` / `"false"` | stated per charge row |
> | Fareharbor | `"true"` | ships both `total` and `total_including_tax`, so it is unambiguous |
> | Livn, Ventus | `""` — **unknown** | their APIs say nothing about tax at all |
> | CustomLinc | `"true"` | implied by `priceGross` vs `priceNet` |
>
> A boolean would force `false` onto Livn and Ventus, which asserts something the
> data does not say.

---

## UNIFIED COLUMN TYPES — what the schema stores

| Unified column | Unified type | Storage form | Why |
|---|---|---|---|
| `product_price` | **`float`** | one number | Three sources mix `int`/`float`; Fareharbor is cents and must be ÷100. Never store as `int`. |
| `product_currency` | **`str`** | 3-letter code, **uppercased** | Ingresso ships `"aud"` lowercase. Normalise on write. |
| `product_price_unit` | **`str`** | free text | `"Passenger"`, `"Jetski"`. Supplier wording kept verbatim — do not map to a controlled list. |
| `product_price_options` | **`str` holding JSON** | `'[{...}, {...}]'` | **See below — this is the one real decision in this section.** |
| `detail_tax_percentage` | **`float`** | one number, a **percent** | Ingresso gives an amount not a rate and cannot fill this column — leave null there. |
| `product_price_tax_inclusive` | **`str`** (3 values) | `"true"` / `"false"` / `""` | **Not a bool.** Unknown for Livn and Ventus; a bool forces a wrong guess. |
| `product_commission_percent` | **`float`** | one number | Rezdy only in practice. |
| `product_price_net` | **`float`** | one number | CustomLinc only in practice. |
| `product_min_quantity` | **`float`** | one number | **DECIDED: ship.** Nullable — Rezdy max absent on 19%. Float, not int, so null survives a pandas round-trip. |
| `product_max_quantity` | **`float`** | one number | **DECIDED: ship.** CustomLinc has no product-level value; Ingresso has a list, not a bound. |

### `product_price_options` — why it is `str`, not a list

**The source shape is an array of objects on 5 of 6 sources**, and the array is
not small:

| Source | Options per product (min / median / max) |
|---|---|
| Fareharbor | 1 / 3 / **26** |
| Rezdy | 0 / 2 / 13 |
| CustomLinc | 4 / 4 / 6 |
| Ventus | **8 / 8 / 8** |

A CSV cell and a SQLite column each hold **one value**, so an array has to be
encoded. Three encodings are possible and **the built file already uses two of
them, inconsistently**:

| Field in `fareharbor_unified_full.csv` | Encoding used today |
|---|---|
| `product_images` | **JSON array string** — `'["https://…", "https://…"]'` |
| `product_price_options` | **display string** — `'Four Hours: $152.00 &#124; Five Hours: $190.00'` |

That inconsistency is itself a defect: two list fields, two conventions, in one
file.

**Recommendation: `str` holding a JSON array**, matching `product_images`.

```json
[
  {"label": "Adult",  "price": 35.0, "price_net": 26.25, "age_min": 0, "pax_max": 25},
  {"label": "Child",  "price": 25.0, "price_net": 18.75},
  {"label": "Family", "price": 99.0, "price_net": 74.25}
]
```

Reasons, in order of weight:

1. **The display string is lossy and the loss is silent.** CustomLinc's fare
   types carry `priceNet`, `ageMin`, `ageMax`, `paxMax` and `isVehicle`.
   Flattening to `"Adult: $35.00"` discards all five with nothing to show it
   happened. Rezdy's `seatsUsed` and Fareharbor's age bounds go the same way.
2. **Ventus cannot be flattened honestly.** Its 8 rows are two dimensions
   (Adult/Child × anyday/weekday, each with a sales variant). A one-line string
   cannot express a matrix; it reads as 8 unrelated prices.
3. **It matches the precedent already set** by `product_images` in the same file.
4. **It is reversible.** A display string can always be generated from JSON;
   JSON cannot be recovered from a display string.

**The cost:** consumers must `json.loads()` the column, and it cannot be filtered
in SQL without JSON functions. If the front end needs a ready-made display
string, add `product_price_options_text` as a **second, derived** column — never
replace the JSON with it.

**A relational child table** (one row per option, keyed on `product_id` +
`source`) is the textbook answer and would be genuinely queryable — but it breaks
the one-row-per-product CSV shape the whole pipeline and the review site are
built on, and turns 20,835 products into roughly 60,000 option rows. Worth
revisiting when the FastAPI layer needs `WHERE price < 50`; not worth it now.

### The `int` trap in every one of these

**Do not type any of these columns `int`.** pandas silently promotes an integer
column to `float64` the moment one value is missing (CLAUDE.md, Data Quirks), so
a nullable int round-trips as `2000.0` and renders as `"2000.0"`. Every numeric
column above is `float` for that reason, including the quantity fields.



## `product_price`

| Source | Path | Source type | Real value | Per product |
|---|---|---|---|---|
| **Fareharbor** | `customer_prototypes[].total_including_tax` | `int` | `17500` = **$175.00 — CENTS** | 2–7 (one per prototype) |
| **Rezdy** | `advertisedPrice` | `float` | `69.0` = $69.00 | **1** |
| **Livn** | `fromPrices[].amount` | `int` (164) / `float` (3) | `189` — a **"from"** price | 1 per currency |
| **CustomLinc** | `fareTypes[].priceGross` | `int` (72) / `float` (28) | `35` | **4** (one per fare type) |
| **Ventus** | `pricing[].price` | `float` (18) / `int` (1) | `351.2` | **8** (type × rate_type) |
| **Ingresso** | `cost_range.min_combined` | `float` | `24.0` — a **range floor** | 1 |

> **CustomLinc's `lowestPrice` is `0` on all 24** — an unpopulated summary field.
> The real prices are one level down in `fareTypes[]`.

## `product_currency`

| Source | Path | Source type | Real value |
|---|---|---|---|
| **Fareharbor** | — | — | **not in the Details API** (built CSV fills it from the ETL) |
| **Rezdy** | `currency` | `str` | `"AUD"` |
| **Livn** | `fromPrices[].currency` | `str` | `"AUD"` |
| **CustomLinc** | `currency` | `str` | `"AUD"` (24/24) |
| **Ventus** | — | — | not present |
| **Ingresso** | `currency_details.*.currency_code` | `str` | **`"aud"` — lowercase**, behind a dynamic key |

## `product_price_unit`

| Source | Path | Source type | Real value | What the unit is |
|---|---|---|---|---|
| **Fareharbor** | — | — | — | implicitly a person |
| **Rezdy** | `unitLabel` | `str` | `"Passenger"`, **`"Jetski"`** | **person OR vehicle** — 16.4% non-person |
| **Livn** | — | — | — | implicitly a person |
| **CustomLinc** | `fareTypes[].fareType` | `str` | `"Passenger"` | + an explicit `isVehicle` bool |
| **Ventus** | `pricing[].attribute_name` | `str` | `"Adult"`, `"Child"` | **always a person type** |
| **Ingresso** | — | — | — | implicitly a ticket |

## `product_price_options`

| Source | Path | Source type | Real value | Items |
|---|---|---|---|---|
| **Fareharbor** | `customer_prototypes[]` | `list[obj]` | `{"display_name": "Child", "total": 8091, "total_including_tax": 8900, "minimum_age": null, "maximum_age": null}` | 2–7 |
| **Rezdy** | `priceOptions[]` | `list[obj]` | `{"label": "Jetski (1 adult)", "price": 199.0, "seatsUsed": 1}` | 1+ |
| **Livn** | — | — | — | — |
| **CustomLinc** | `fareTypes[]` | `list[obj]` | `{"description": "Adult", "priceGross": 35, "priceNet": 26.25, "ageMin": 0, "paxMax": 25, "isVehicle": false}` | **4** |
| **Ventus** | `pricing[]` | `list[obj]` | `{"attribute_name": "Adult", "rate_type": "anyday_rate", "price": 351.2}` | **8** |
| **Ingresso** | `cost_range_details.ticket_type[]` | `list[obj]`, **4 levels deep** | `ticket_type[] → price_band[] → cost_range → alternate_discounts[]` | varies |

> **Five sources supply this array and no two agree on the key name** —
> `display_name` / `label` / `description` / `attribute_name` all mean the same thing.

## `detail_tax_percentage`

| Source | Path | Source type | Real value | Shape |
|---|---|---|---|---|
| **Fareharbor** | `tax_percentage` | `int` | `10` = 10% | **scalar** |
| **Rezdy** | `taxes[].taxPercent` | `float` | `10.0` | **`list[obj]`** — up to 3 rows, each with `taxFeeType`, `priceInclusive`, `compound` |
| **Livn** | — | — | — | — |
| **CustomLinc** | — | — | — | implied by gross vs net |
| **Ventus** | — | — | — | — |
| **Ingresso** | `cost_range.min_combined_combined_tax_component` | `float` | `2.18` | **an AMOUNT, not a rate** — $2.18 inside $24.00 |

## `product_price_tax_inclusive`

| Source | Path | Source type | Real value |
|---|---|---|---|
| **Fareharbor** | — | — | **implied `true`** — ships `total` AND `total_including_tax` |
| **Rezdy** | `taxes[].priceInclusive` | `bool` | `true` / `false`, **per tax row** |
| **Livn** | — | — | **unknown** |
| **CustomLinc** | — | — | implied by `priceGross` vs `priceNet` |
| **Ventus** | — | — | **unknown** |
| **Ingresso** | — | — | tax given as an amount |

> **Tri-state, not boolean:** true structurally (Fareharbor), per-row (Rezdy),
> genuinely **unknown** (Livn, Ventus). A `bool` column forces a guess on two sources.

## `product_commission_percent`

| Source | Path | Source type | Real value | Useful? |
|---|---|---|---|---|
| **Fareharbor** | — | — | — | — |
| **Rezdy** | `maxCommissionPercent` | `float` | `18.0`, `13.0` | **yes** — 398/400 |
| **Livn** | `commissionPerc` | `int` | **`0` on all 167** | **no** |
| **CustomLinc** | — | — | — | — |
| **Ventus** | — | — | — | — |
| **Ingresso** | — | — | — | — |

## `product_price_net`

| Source | Path | Source type | Real value | Useful? |
|---|---|---|---|---|
| **Fareharbor** | — | — | — | — |
| **Rezdy** | `maxCommissionNetRate` | `float` | `0.0`, on the 1 product of 400 that has it | **no** |
| **Livn** | `usesNetRates` | `bool` | **`False` on all 167** — a flag, not a price | **no** |
| **CustomLinc** | `fareTypes[].priceNet` | `float` / `int` | `26.25` against gross `35` | **yes** — 24/24 |
| **Ventus** | — | — | — | — |
| **Ingresso** | — | — | — | — |

> **CustomLinc is the only source with a genuine net price.**

## `product_min_quantity` / `product_max_quantity`

> ### DECIDED — 2026-08-19, Suyash
>
> **KEEP, as two new columns of their own.** Not merged into
> `detail_group_size`, not dropped as booking plumbing.
>
> | | |
> |---|---|
> | **Columns** | `product_min_quantity`, `product_max_quantity` |
> | **Type** | `float`, nullable |
> | **Unit** | read from `product_price_unit` — never assume people |
> | **Null means** | "the supplier did not state a limit" — **NOT** "unlimited" |
>
> **Why kept:** 201 Rezdy products (16.8%) have a minimum above 1. "This tour
> needs 10 people" is something an agent must know *before* calling a customer
> back, so it passes the browse-only test even though the field looks like
> checkout machinery.
>
> **Why not `detail_group_size`:** that column holds supplier PROSE
> (`"Maximum 15 people"`, `"Up to 3 riders"`); this is a NUMBER. Merging forces
> either generated sentences (unsearchable, and Critical Rule #11 would need a
> `*_source` flag) or prose-parsing (fragile). They are also different concepts —
> group size describes the TOUR, this constrains the BOOKING.
>
> **Rendering rule:** always print the unit. `"1–8 Jetskis"`, never
> `"1–8 people"`.
>
> **Accepted cost:** effectively Rezdy-only. Livn fills `groupSizeMax` on 7 of
> 167; CustomLinc's limits are per-fare-type and stay inside the
> `product_price_options` JSON; Fareharbor, Ventus and Ingresso have nothing.
> Blank for ~55% of the catalogue, and blank is the correct answer there.
>
> **Not carried:** Rezdy's third field `quantityRequired` (a bool at position 15,
> "must a quantity be chosen") — checkout behaviour, tells an agent nothing.

*Booking quantity limits. **Omitted from an earlier draft of this table** — added
back after review.*

| Source | Path | Source type | Real value | Unit is |
|---|---|---|---|---|
| **Fareharbor** | — | — | **no quantity field of any kind** | — |
| **Rezdy** | `quantityRequiredMin` / `quantityRequiredMax` | `int` / `int` (max is `null` on 19%) | `1` / `8` | **the `unitLabel`** — so `8` can mean **8 jetskis** |
| **Livn** | `groupSizeMax` | `int` | `24` — **4.2% filled only** | people |
| **CustomLinc** | `fareTypes[].paxMin` / `.paxMax` | `int` / `int` | `0` / `25` | **per fare type**, so Adult max 25, Child max 10 |
| **Ventus** | — | — | — | — |
| **Ingresso** | `events_by_id.*.valid_quantities` | **`list[int]`** | `[1, 2, 3, … 20]` — an **enumeration**, not a range | tickets |

### Same trap as `product_price_unit`, and it compounds it

Rezdy's `quantityRequiredMax` is **denominated in `unitLabel`**, not in people.
On Casino Royale (`P0F1AB`) `unitLabel` is `"Jetski"` and
`quantityRequiredMax` is `8` — that is **eight jetskis**, carrying up to sixteen
people. A portal reading it as a party-size cap is wrong in the same direction as
the price, so the two errors multiply rather than cancel.

Three further shape problems:

- **Rezdy `quantityRequiredMax` is `null` on 19%** (76 of 400). Absent, not unlimited.
- **CustomLinc's limits are per fare type**, not per product — Adult `paxMax` 25,
  Child `paxMax` 10 on the same product. There is no product-level number.
- **Ingresso enumerates instead of bounding** — `valid_quantities` is a list of
  every permitted quantity. Reading `max(list)` loses the fact that the set can
  have gaps.

## Five type rules for the build

1. **Cast every price to `float`.** Three sources mix `int` and `float` in one
   field (Livn 164/3, Ventus 18/1, CustomLinc 72/28). Nothing here is safely an int.
2. **Divide Fareharbor by 100.** It is the only cents source, and its `int` type
   is the only hint.
3. **Never trust a scalar summary field.** `lowestPrice` (0/24) and
   `commissionPerc` (0/167) are both `int`, both 100% present, both empty.
4. **Normalise the price-option key name** — four different spellings of one concept.
5. **`product_price_tax_inclusive` needs a third state** for "unknown".

### Price is the least comparable field in the schema

**Every source means something different by "price":**

| Source | `product_price` actually is |
|---|---|
| Fareharbor | tax-inclusive total **in CENTS**, per prototype — usually a person type, occasionally a **group size** (0.3%) |
| Rezdy | advertised price in dollars **per `unitLabel`** — 16.4% are not per person |
| Livn | a **"from" price** — the cheapest of a list |
| CustomLinc | `fareTypes[].priceGross` — real prices on 24/24, plus a **net** price. `lowestPrice` is 0 everywhere. |
| Ventus | one row per `rate_type`; no single product price |
| Ingresso | `min_combined` of a **cost range**, with separate tax components |

Four of the six are explicitly a **minimum or a "from" price**. Only Fareharbor
and Rezdy carry something that could be shown as "the price" — and they use
**different denominations**: Fareharbor in cents, Rezdy in dollars, with nothing
in either field name to say so.

**See `PRICE_STRUCTURE_REAL_EXAMPLES.md` for the actual JSON of one product per
source.** Reading it corrected three rows of this table.

> **D5 and D6 are wider than Rezdy.** `product_price_unit` is needed for Ventus
> too (`attribute_name`), and a "from price" flag is arguably needed for Livn,
> CustomLinc and Ingresso.

> **Commission is Rezdy-only in practice.** Livn has a `commissionPerc` field on
> 100% of products, but **its value is `0` on all 167** — verified across every
> file. It is a present-but-meaningless field, so D7 remains a Rezdy question.
> Livn also carries `usesNetRates` (100%), which may be how its commercials are
> actually expressed; that has not been investigated.

---

# 4. LOCATION

> ### DECIDED — 2026-08-19, Suyash · section 4
>
> **1. Fareharbor location reads `item.locations[]`, NOT `item.primary_location`.**
> The two are not alternatives — `primary_location` is a **copy** of
> `locations[0]`. Measured on 1,199 sampled products:
>
> | | Products |
> |---|---|
> | has `primary_location` | 249 |
> | has `locations[]` | **885** |
> | has `primary_location` but NOT `locations[]` | **0** |
> | has `locations[]` but NOT `primary_location` | **636** ← lost today |
> | `primary_location.address` == `locations[0].address` | **249 / 249** |
>
> `locations[]` also carries `google_place_id` and `tripadvisor_url`, which
> `primary_location` does not. The 314 with neither genuinely have no location —
> blank is correct.
>
> **⚠ CORRECTION (2026-08-19): the running ETL is ALREADY right; only the
> DOCUMENTATION is wrong.** `etl_fareharbor.py:79` reads `locations[0]` first and
> falls back to `primary_location`. The built file's `location_city` is **72.2%**,
> matching `locations[]` at 73.9% — not the 20% that reading `primary_location`
> would give.
>
> An earlier version of this block claimed switching would "gain ~6,000 products."
> **That was wrong.** The wrong mapping exists only in CLAUDE.md's Source Field
> Mapping table, which lists `item.primary_location.*`. Nothing in the pipeline
> needs changing; **CLAUDE.md does**.
>
> One real (small) difference remains: the ETL takes `locations[0]`, while this
> decision specifies `type == "primary"` else first. Those usually agree, but not
> always.
>
> **2. Ingresso location reads `venue_desc` (100%), NOT `venue_addr` (6.2%).**
> `venue_desc` is sometimes a venue name (`"Madame Tussauds Sydney"`) and
> sometimes a full address (`"1-5 Wheat Rd, Sydney NSW 2000"`) — it is the best
> available location string rather than a clean street field. Accepted: something
> beats nothing on 16 products.
>
> **3. Multiple locations — take `type == "primary"`, else the first.** No
> start/end column pairs. `locations[]` is a list, but **761 of 885 products have
> exactly one entry**, and only **45 (5%)** carry genuinely different addresses
> across entries. Fareharbor types them `primary` (798), `start` (172), `end`
> (86), `pre` (53). Doubling the location columns for 5% of one source is not
> worth it. If those 45 ever need full treatment they fit the source-tag rule
> (`[START] … [END] …`) without a schema change.
>
> **4. `locations[].note` (37.9%) is wired into `detail_meeting_point`** as an
> `[API]` block. It holds meeting instructions — *"We meet next to the Surf
> Lifesaving Club toilets"*, *"Please arrive 20 minutes prior for safety
> briefing"* — and currently reaches no column at all. This needs no new
> decision: the concept already has a column, so under the source-tag rule a new
> source is simply another tagged block, `[API]` leading. May be part of the
> missing meeting-point data recorded in CLAUDE.md (18 of 50 sampled products had
> meeting-point text that reached no field).
>
> **5. Country must be normalised before use** — Fareharbor writes a code
> (`"NZ"`), Rezdy's `countryCode` is noisy (`AUSTRALIA`, `NF` alongside `AU`,
> `NZ`), Ingresso writes a name (`country_desc`). Normalise to the 2-letter code.
>
> **Not resolved here:** CustomLinc has effectively no location — `startLocation`
> on 2 of 24. Its `defaultPickupLocationWeb` (54%) is a better source and is
> listed in section 10a as a proposed addition.



| Unified | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|
| `location_street` | `locations[].address.street` 73.9% | `locationAddress.addressLine` 77.2% | `locationsStart[].address1` 70.1% | `startLocation` **8.3%** | — | `venue_addr` **6.2%** |
| `location_city` | `locations[].address.city` 73.9% | `locationAddress.city` 83.5% | `locationsStart[].city` 100% | — | `location.name` 100% | `city_desc` 75.0% |
| `location_state` | `locations[].address.province` 73.9% | `locationAddress.state` 78.1% | `locationsStart[].state` 100% | — | — | — |
| `location_country` | `locations[].address.country` 73.9% | `locationAddress.countryCode` 90.7% | `locationsStart[].country` 100% | — | — | `country_desc` 100% |
| `location_postcode` | `locations[].address.postal_code` 73.9% | `locationAddress.postCode` 76.0% | `locationsStart[].postcode` 100% | — | — | `postcode` 100% |
| `location_latitude` | `locations[].latitude` 73.9% | `product.latitude` 99.8% | `locationsStart[].latitude` 100% | — | — | `geo_data.latitude` 100% |
| `location_longitude` | `locations[].longitude` 73.9% | `product.longitude` 99.8% | `locationsStart[].longitude` 100% | — | — | `geo_data.longitude` 100% |
| `location_end` | — | — | `locationsEnd[]` 100% | `endLocation` 8.3% | — | — |
| `location_timezone` | — | `timezone` 100% | `locationsStart[].tz` 100% | — | — | — |

### Three things to know

**Trap — Fareharbor's location mapping is reading the wrong field.** CLAUDE.md
maps location to `item.primary_location.*`, filled on **20.8%**. The sibling
`item.locations[]` is filled on **73.9%** — same data, 3.5× the coverage.
Detailed in `FAREHARBOR_REZDY_FIELD_MAP.md`.

**Livn is the only source with 100% location on every component**, and the only
one with a distinct **end** location (`locationsEnd[]`) as well as a start.

**CustomLinc effectively has no location.** `startLocation` is filled on 2 of 24
products. Its 24 products will be blank on the map.

---

# 5. DESCRIPTION AND DETAIL

> ### DECIDED — 2026-08-19, Suyash · THE SOURCE-TAG RULE (governs every text column)
>
> **When more than one place in a product supplies the same concept, KEEP THEM
> ALL in one column, each labelled with where it came from. Merge nothing. Delete
> nothing. Decide nothing about the content yet.**
>
> ```
> detail_cancellation_policy
> ───────────────────────────────────────────────────
> [API] Cancel up to 7 days before for a full refund.
>
> [DESCRIPTION] Cancellations within 48 hours incur a 50% charge.
>
> [BOOKING NOTES] No refund for no-shows.
> ```
>
> **Applies to every text column, not just the seven overlapping ones.**
>
> #### The rules
>
> 1. **One column per concept.** The schema does NOT gain per-source columns
>    (`description_what_included`, `additionalinfo_what_included`). Every source
>    fills the same column with different tags, so the schema stays the same width
>    for all six and no source invents its own column names.
> 2. **Tags come from a fixed, closed list.** `[API]` · `[DESCRIPTION]` ·
>    `[BOOKING NOTES]` · `[ADDITIONAL INFO]` · `[TERMS]`. `[API]` means a
>    dedicated supplier field, not extracted text. A tag outside this list is a
>    build error, so the vocabulary cannot drift.
> 3. **`[API]` always comes first**, then extracted blocks. This is Critical Rule
>    #10's precedence (dedicated field → parsed → generated) expressed inside the
>    cell, so the most trustworthy content leads.
> 4. **ALWAYS tag, even when there is only one block.** Uniform shape means the
>    front end has ONE strip rule instead of two, and provenance is visible on
>    every product rather than only the messy ones.
> 5. **Extraction stays separate.** Each extraction pass writes its own output as
>    it does today; tagging happens at the unified-build step. The extractions are
>    not re-run to change this.
>
> #### Why
>
> The question "which source wins?" is a decision about CONTENT. This schema work
> is about STRUCTURE. Tagging lets the structure be settled now and the content
> question be answered later — from the built data, not in advance — because the
> provenance is preserved in the text. Merging destroys that; tagging keeps it.
>
> It also supersedes the need for a `*_source` companion column (Critical Rule
> #10): with several blocks present there is no single winner to record, and the
> tag does the job inline.
>
> #### Consequences — both must be carried into the handover
>
> - **The front end MUST strip the tags before display**, or agents will see
>   `[BOOKING NOTES]` on the page. One regex on `^\[[A-Z ]+\]\s*`. **This is a
>   required integration step for the web team, not an optional nicety.**
> - **Cells get longer**, sometimes carrying the same fact twice, because
>   de-duplication is deliberately not done. That is accepted for now.
>
> #### Deferred, on purpose
>
> - **De-duplication.** Fareharbor's three-band rapidfuzz merge (97 / 80) is NOT
>   applied. Nothing is compared, nothing is dropped. It stays available and can
>   be run later over the tagged output.
> - **`exports/fareharbor_unified_full.csv` is NOT rebuilt yet.** It keeps its
>   current merged form so the review site on port 5056 keeps working. All sources
>   move to the tagged format in one build when Rezdy is ready. **Until then the
>   schema document and that file deliberately disagree.**
>
> #### Format
>
> Plain text tags, not JSON — the data stays readable in Excel while it is being
> reviewed, which matters more right now than machine-parsing. `product_price_options`
> stays JSON because it holds structured objects, not prose.



## 5a. The structural divide

| Source | Pre-split detail fields? | What extraction must do |
|---|---|---|
| **Fareharbor** | **Yes** — `structured_description`, 22 sub-fields, **76.7%** | fill the 23.3% gap |
| **Livn** | **Yes** — `highlights`, `inclusions.items[]`, `itinerary.items[]` as real objects | almost nothing |
| **Ventus** | **Partly** — `inclusions.non_flight_items[]`, `terms.*` split | almost nothing |
| **Ingresso** | **Partly** — `structured_info.overview` **12.5%**, `custom_field[]` 43.8% | little available |
| **Rezdy** | **No** — one HTML blob | **everything**, from headings |
| **CustomLinc** | **No** — and the description fields are **empty** | nothing to work with |

> ### DECIDED — 2026-08-19, Suyash · section 5 decisions 1-3
>
> **1. Livn itinerary — keep the day structure.** `itinerary.items[]` is stitched
> into ONE text string in `detail_itinerary`, with each block's label kept:
> `title` if present, else `Day N` / `Days N–M` from `dayFrom`/`dayTo`. Without
> it a 19-day course arrives as 12 unlabelled paragraphs. Affects ~8 of the 10
> Livn products that have an itinerary at all.
>
> **2. Livn `specialNotes` — split on its headings, do not dump in one column.**
> The field is filled on 167/167 but is a CATCH-ALL, not a packing list: a census
> of all 167 found **29 distinct headings**. Routing (simulated over all 167 —
> 506 blocks routed, 60 left, nothing lost):
>
> | Heading(s) | Blocks | Destination |
> |---|---|---|
> | `Conditions` | 167 | `important_info` (23,003 words — the heaviest column for this source) |
> | `What to bring`, `What to wear` | 146 | `what_to_bring` |
> | `Optional extra(s)`, `Optional activities`, `Option extras` | 99 | `extras` |
> | `Fuel surcharge`, `Levies`, `Levy`, `Surcharge`, `Fuel levy` | 56 | `pricing_notes` |
> | `Health & Safety`, `Health and Safety` | 19 | `health_safety` |
> | `Restrictions`, `Restriction` | 9 | `restrictions` |
> | `Not included` | 9 | `what_is_not_included` |
> | `Requirements` | 1 | `special_requirements` |
> | topic headings — `Vessel amenities`, `Food & drinks`, `Snorkel safety information`, `Scuba diving conditions`, `Helicopter tours`, `Diving`, `Dive centre`, `Tubing` | 60 | **`description`** |
>
> Topic headings are NOT column names and get no column — same rule already
> settled for Fareharbor (`MEALS`, `TAXI`, `LYCRA SUITS & WETSUITS`). Text before
> the first heading (18 products) also goes to `description`.
>
> The surcharge group matters beyond Livn: 56 blocks of *money not in the
> advertised price*, which is **D6** arriving through a different door.
>
> **3a. `detail_what_not_to_bring` — DROPPED as a column, merged into
> `what_to_bring`.** All 25 values are packing instructions phrased negatively
> (`"Glass bottles / Red wine"`, `"Selfie sticks"`, `"BYO alcohol"`). A reader
> treats bring/don't-bring as one thought; two sections means someone packs from
> the first and never reads the second. **The negation MUST be preserved on
> merge** — each merged block is prefixed `Do not bring:` so the meaning cannot
> invert. Thin in both big sources (FH 0.2%, Rezdy 0.3%).
>
> **3b. `detail_special_requirements` — KEPT as its own column.** Thin (FH 0.5%,
> Rezdy 0.4%) but the highest-consequence content in the section: age limits,
> swimming ability, fitness, **disability access**, dietary needs — *who can and
> cannot do this tour*. Merging it into `restrictions` (mostly difficulty ratings)
> would bury accessibility information. Not merged.
>
> **Every other detail column is KEPT**, however thin on Fareharbor: thin there is
> not thin everywhere (`what_is_included` 22.4% FH but **100% Livn and Ventus**;
> `health_safety` 9.3% FH but **100% Ventus**; `highlights` 5.2% FH but **100%
> Livn**; `languages` 2.8% FH but **99.7% Rezdy**). Four sources still have no
> extraction pass, so no column is judged dead yet. Empty sections are hidden by
> the front end — a display concern, not a schema one. **Ship fill rates alongside
> the schema** so the web team can plan for a section that renders on 1 product
> in 80.

> ### DECIDED — 2026-08-19, Suyash · section 5 decision 4
>
> **Products with no description are INCLUDED, with the column left BLANK.**
> 40 products carry no supplier prose at all: CustomLinc 24/24 (every mapped
> description field empty on every file) and Ingresso 13/16.
>
> **We do not generate a description for them.** A blank is a fact about the
> supplier feed, not a gap to be filled — the same principle as Critical Rule #11
> (never present generated text as supplier data), applied one step earlier.
>
> They are not useless: CustomLinc still has fare types with prices, departure and
> return times, and a pickup location on 54%; Ingresso has a venue name on 100%.
> That is a usable listing, just a thin one.

## 5b. Field by field

| Unified | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|
| `detail_description` | `description` 98.7% | `description` 100% | `description` 100% | `webpageDesc` **0%** | `description` 36.8% | `event_info` 18.8% |
| `detail_highlights` | `structured_description.highlights` 19.6% | extraction | **`highlights.highlights[]` 100%** | — | — | — |
| `detail_what_is_included` | `.what_is_included` 38.7% | extraction | **`inclusions.items[].content` 100%** | `fareIncludes` **0%** | `inclusions.non_flight_items[]` 100% | — |
| `detail_itinerary` | `.itinerary` 16.1% | extraction | `itinerary.items[].body` **6.0%** | — | — | — |
| `detail_meeting_point` | `.meeting_point` 47.0% | extraction | `locationsStart[].business` 70.1% | — | `inclusions.transfer.attributes[].attributes_id.address` 26.3% | — |
| `detail_what_to_bring` | `.what_to_bring` 22.4% | extraction | `specialNotes` 100% | — | — | — |
| `detail_booking_notes` | `booking_notes` 73.1% | `additionalInformation` 41.6% | `pickupNotes` 86.8% | `alert` **0%** | — | — |
| `detail_cancellation_policy` | `cancellation_policy` 98.3% | `terms` 34.3% | — | — | `terms.booking_terms` 36.8% | — |
| `detail_health_safety` | `health_and_safety_policy` 6.7% | extraction | — | — | `terms.fit_to_fly_terms` 100% | — |
| `detail_accessibility` | `.accessibility` **10.1%** | extraction | — | — | — | — |
| `detail_group_size` | `.group_size` **20.2%** | extraction | `groupSizeMax` 4.2% | — | — | — |
| `detail_min_age` | `.min_age` **17.4%** | extraction | `ageMin` 19.8% | — | — | — |
| `detail_max_age` | `.max_age` **6.8%** | extraction | — | — | — | — |
| `detail_disclaimers` | `.disclaimers` 16.4% | `terms` 34.3% | `supplier.tnc` 72.5% | — | `terms.fit_to_fly_terms` 100% | — |
| `detail_faqs` | `.faqs` 11.1% | extraction | — | — | — | `custom_field[]` 43.8% |
| `detail_extras` | `.extras` 7.2% | `extras[]` 38.7% | — | — | — | — |
| `detail_dropoff_notes` | — | — | `dropoffNotes` 58.7% | — | — | — |

### CustomLinc's description fields are empty — on all 24 products

CLAUDE.md's Source Field Mapping gives CustomLinc four mappings. **Verified
against all 24 raw files, every one of them is empty:**

| CLAUDE.md maps | Filled |
|---|---|
| `webpageDesc` → `detail_description` | **0 / 24** |
| `fareIncludes` → `detail_what_is_included` | **0 / 24** |
| `languageName` → `detail_languages` | **0 / 24** |
| `alert` → `detail_booking_notes` | **0 / 24** |

Also empty on all 24: `webLongDesc`, `webShortDesc`, `webContent`, `image`,
`imageCaption`, `origins`, `dropoffLocations`, `nights`.

CLAUDE.md already rates CustomLinc "Weak — no description in detail API". This
confirms it and puts a number on it: **CustomLinc contributes no product text at
all.** 40 of its 171 fields are present-but-never-filled — by far the highest
dead-field rate of any source.

### Livn is the best-structured source in the catalogue

`highlights.highlights[]`, `inclusions.items[].content` and `itinerary.items[]`
are **real arrays of typed objects**, filled at 100% / 100% / 6%. No extraction,
no heading-gating, no HTML parsing. If Livn had 10,000 products instead of 167 it
would be the reference implementation.

---

# 6. MEDIA

> ### DECIDED — 2026-08-19, Suyash · section 6
>
> **TWO media columns. No separate main-image column.**
>
> | Column | Type | Holds |
> |---|---|---|
> | `product_images` | `str` (JSON) | every image, one object each, cover flagged inside |
> | `product_videos` | `str` (JSON) | Rezdy only — `{url, platform, id}`, 14.5% (~1,360 products) |
>
> #### The image object — one shape for all sources, blank where not supplied
>
> ```json
> {
>   "source_image_id": 2667118,
>   "url":             "https://…photo.PNG",
>   "is_main":         true,
>   "thumbnail_url":   "https://…photo_tb.PNG",
>   "medium_url":      "https://…photo_med.PNG",
>   "large_url":       "https://…photo_lg.PNG",
>   "width":  1920, "height": 1440,
>   "file_size": 286635, "mime_type": "image/jpg"
> }
> ```
>
> | Key | Fareharbor | Rezdy | Livn | Ventus | CustomLinc | Ingresso |
> |---|---|---|---|---|---|---|
> | `url` | 96.2% | 100% | 99.4% | 100% | — | — |
> | `source_image_id` | `pk`, 543/543 | `id`, 4,060/4,060 | — | — | — | — |
> | `is_main` | **supplier's own choice** | first in list | first | first | — | — |
> | `thumbnail_url` | — | 100% | — | — | — | — |
> | `medium_url` / `large_url` | — | 98.5% | — | — | — | — |
> | `width`/`height`/`file_size`/`mime_type` | — | — | 99.4% | — | — | — |
>
> **"Only one source has it" is not a reason to drop a field.** Rezdy's four
> sizes, Livn's dimensions and the supplier image ids are all kept on that basis,
> consistent with every other section today.
>
> **1. NO `product_main_image` column.** It was proposed and rejected: `is_main`
> inside the JSON already identifies the cover, so a separate column stores the
> same URL twice and creates two things that can disagree. The argument for it
> was listing-page performance — a real concern, but for an API layer that does
> not exist yet, and it can be added later if measured to be slow.
>
> **2. THE COVER IS SOMETIMES A PHOTO THAT IS NOWHERE ELSE.** Measured on 600
> Fareharbor products:
>
> | | Products |
> |---|---|
> | cover == `images[0]` | 545 |
> | **cover NOT in `images[]` at all** | **35 (~6%, ≈1,000 at full scale)** |
> | cover present, no image list | 7 |
>
> So the cover must be **added into the list** when absent, at position 0 with
> `is_main: true`. Taking "the first gallery image" instead would show a photo the
> supplier did not choose on ~1,000 products; keeping the cover only in its own
> column would hide it from the gallery on the same products. Both halves matter.
>
> *An earlier note in this document said the two were "identical, so
> first-in-list would likely give the same answer." That was based on ONE
> product and is wrong — corrected here.*
>
> **3. `is_main` means two different things.** On Fareharbor it is the supplier's
> editorial choice (`image_cdn_url`, 97.3%); on Rezdy, Livn and Ventus it is
> **our convention** — first in the list — because **no other source has a
> dedicated cover field at all** (verified across all six). The web team must be
> told: to get the main image, find `is_main == true`, do NOT take the first
> entry.
>
> **4. Fareharbor's `gallery` is dropped.** Every image object carries
> `gallery: "carousel"` — **1,719 of 1,719, a single value.** It carries no
> information.
>
> **5. 40 products have no image and stay that way.** CustomLinc's `image` AND
> `imageCaption` are both empty on all 24 (verified); Ingresso has no image field
> in its API. Included in the catalogue, blank in the column, nothing generated.
>
> **Clean results, checked and not an issue:** no duplicate image URLs within a
> product (450 multi-image Rezdy products, zero repeats); supplier image ids are
> unique per image and never reused across products (4,060 ids, 4,060 distinct),
> so they cannot serve as a de-duplication key — they are kept as provenance and
> as a future incremental-update key.
>
> **NOT checked:** whether any image URL is dead. That needs HTTP requests to
> ~20,000 URLs — worth doing before launch, not part of schema design.

> ### DECIDED — 2026-08-19, Suyash · EXTRAS — resolved, no longer blocked
>
> **Rezdy's `extras[]` goes into `detail_extras` as `[API]`-tagged text**, under
> the standard source-tag rule. It is a dedicated supplier field, so it takes the
> `[API]` tag and leads the cell.
>
> ```
> detail_extras
> [API] Damage Liability Cover — $25.00
>       Reduce repair costs to $2500 for an additional $25.
>
> [DESCRIPTION] Grip socks can be purchased separately online
>       or at the check-in desk.
> ```
>
> | Source | Field | Fill | Tag |
> |---|---|---|---|
> | Rezdy | `extras[]` (structured: name, description, price, priceType, image) | 38.7% | `[API]` |
> | Fareharbor | `structured_description.extras` (prose) | 7.2% | `[DESCRIPTION]` |
> | Livn | `specialNotes` "Optional extra" blocks (prose) | 99 blocks | `[DESCRIPTION]` |
>
> **This unblocks the column without waiting on a Figma design.** The earlier
> position — hold Rezdy's extras in a separate structured column until a design
> exists — is superseded: it left a filled supplier field with no destination for
> an unknown period.
>
> **Accepted losses, both recoverable:**
> - **The price becomes text.** `25.0` renders as `"$25.00"` inside the cell, so
>   add-on prices are not sortable or filterable. ~3,600 products have priced
>   extras.
> - **The add-on image has no destination.** `extras[].image` (33.1%) is not
>   carried.
>
> Both remain in the raw API data, so a structured `product_extras` column can be
> added later without re-fetching anything — **once a Figma design shows how a
> priced add-on with a picture renders.**

---

# 7. SCHEDULE AND DURATION

> ### DECIDED — 2026-08-19, Suyash · section 7
>
> **THE GOVERNING RULE: generate nothing. A blank is an acceptable answer.**
> Only values the supplier actually stated are stored. This is Critical Rule #11
> applied one step earlier — do not create the text in the first place.
>
> **1. Two columns, kept — they are complements, not duplicates.**
>
> | Column | Holds |
> |---|---|
> | `product_duration` | the supplier's own words, verbatim |
> | `product_duration_minutes` | a number the supplier actually gave as a number |
>
> No source fills both. An earlier note called these a "duplicate concept"; they
> are not — Fareharbor supplies only prose, Rezdy/Livn/CustomLinc only numbers.
>
> **2. CustomLinc — use `durationLong`, never `duration`.**
> `duration` mixes TWO UNITS in one string with no flag: `"1"` means one **day**,
> `"02:00"` means two **hours**. Read as a number, a one-day tour becomes 1.
>
> They are also not two fields. **On all 24 files `durationLong` starts with
> `duration`** — it is the same value plus the unit word (`"1"` → `"1 Day"`,
> `"02:00"` → `"02:00 Hrs"`). `duration` is `durationLong` with the vital part
> removed, so keeping both stores one fact twice, once broken.
>
> `duration` is therefore **deliberately dropped** — recorded here so a
> 100%-filled unused field is not later "helpfully" wired in.
>
> **3. The Metadata API is NOT used for duration.** D4 asked whether its
> unreliability was a recoverable unit bug. Measured across all 23,034 metadata
> products: **8,871 (38%) carry a duration under 1 hour**, mixing legitimate
> values (`"Jabiru 30 minute Helicopter Flight"` = 0.5 hrs) with corrupt ones
> (`644378` "Lake Mountain Snow Tour" = 0.18333 hrs = **11 minutes** for a full
> day). The two cannot be told apart. Coverage is also **76.5%**, not the 100%
> recorded in D4. **Not recoverable — dropped.**
>
> **4. Fareharbor gets prose only; its minutes column stays BLANK.**
> Its `structured_description.duration` (43%) is unparseable in general —
> `"3 Hours"`, `"6 Weeks"`, `"All day"`, `"Half day/ Full day"`,
> `"2 - 2.5 Hours"`, `"2  Hours\t\t\t\t"`, and full sentences. Parsing `"3 Hours"`
> to `180` would be a DERIVED number, which the governing rule forbids. Accepted
> cost: `product_duration_minutes` is blank for Fareharbor.
>
> **5. Rezdy and Livn get minutes only; their prose column stays BLANK.**
> Both supply clean integer minutes (Rezdy 93.5%, Livn 100%). Rendering `120` as
> `"2 hours"` is a DISPLAY job for the front end, not data for us to write.
>
> **6. Livn duration RANGES — `durationRangeMax` is kept as its own value.**
> 26 products run a range (`duration` 240 → `durationRangeMax` 11520: boat hire
> from 4 hours to 8 days). `product_duration_minutes` holds the **minimum**; the
> maximum is carried alongside rather than discarded or averaged.
>
> **7. `0` is not a duration — store blank.** Both Rezdy and Livn have products
> with `durationMinutes == 0`, which means "not stated", not "zero minutes".
> *Unverified:* Rezdy's maximum of **71,582 minutes (50 days)** may be a genuine
> expedition or junk — not checked.
>
> **8. Start / return time and operating days are KEPT**, filled only by Livn
> (`timeStart` 97.6%, `operatingDaysStr` 100%) and CustomLinc (`departureTime`
> and `returning` 100%, `operatingDays` 16.7%). Blank for the other four sources,
> which is ~98.9% of the catalogue — and correct, since they do not supply it.



| Unified | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|
| `product_duration` | `.duration` prose 43.0% | — | — | `durationLong` 100% | — | — |
| `product_duration_minutes` | — | `durationMinutes` 93.5% | `duration` int 100% | `duration` string 100% | — | — |
| `detail_operating_days` | — | — | `operatingDaysStr` 100% | `operatingDays` 16.7% | — | — |
| `detail_start_time` | — | — | `timeStart` 97.6% | `departureTime` 100% | — | — |
| `detail_languages` | `guided_languages[]` 2.8% | `languages[]` **99.7%** | — | `languageName` **0%** | — | — |
| `detail_pickup_available` | `is_pickup_ever_available` 100% | `pickupId` 27.1% | `pickupNotes` 86.8% | `isPickupCompulsory` 100% | — | — |

### Duration is a four-way unit conflict

| Source | Field | Unit | Type |
|---|---|---|---|
| Fareharbor | `structured_description.duration` | prose ("4 Hours") | string |
| Rezdy | `durationMinutes` | minutes | int |
| Livn | `duration` | **minutes** | int |
| CustomLinc | `duration` | **unknown** | **string** |
| CustomLinc | `durationLong` | prose | string |

**CustomLinc has two competing duration fields, both 100% filled**, and its
`duration` is a *string* where Livn's identically-named field is an *int*. A
merge that keys on field name will mix units silently. **D4.**

---

# 8. TAGS AND CATEGORY

> ### DECIDED — 2026-08-19, Suyash · section 8
>
> **1. Rezdy's tags are SPLIT BY PREFIX — they are eight facets, not one list.**
> Rezdy writes `"PREFIX:value"` strings. Measured across 1,199 products:
>
> | Prefix | Tags | Destination |
> |---|---|---|
> | `SUITABILITY` | 2,463 | `product_tags` |
> | `AGE` | 1,833 | **`detail_restrictions`** |
> | `INTEREST` | 1,399 | `product_tags` |
> | **`ACCESSIBILITY`** | **1,042** | **`detail_accessibility`** |
> | `CATEGORY` | 834 | **`product_category`** |
> | `TYPE` | 725 | `product_tags` |
> | `INTENSITY` | 508 | `product_tags` |
> | `SKILL_LEVEL` | 494 | `product_tags` |
>
> **`ACCESSIBILITY` is the reason this matters.** 1,042 tags — while
> `detail_accessibility` reads 1.2% on Fareharbor and was nearly dropped in
> section 5 for being too thin. Rezdy has supplied it all along, inside a field
> we were flattening into tag soup. Same for `AGE`, against
> `detail_min_age`/`max_age` currently marked always-empty by design.
>
> Same move as Livn's `specialNotes`: one field carrying several concepts, split
> on labels the supplier already wrote. No classification by meaning.
>
> **2. The Metadata API is NOT used for category.** `product_category` is filled
> from **each source's own Details API only**. The Metadata API has category at
> 99% for both big sources, but using it pulls a second API into the build and
> re-opens D1 ("is Metadata the spine?"). Rejected as unnecessary complication —
> the Details API already carries category on every source:
>
> | Source | Field | Coverage |
> |---|---|---|
> | Livn | `categories[].name` | 100% |
> | Ventus | `flight_type.name` | 100% |
> | Ingresso | `classes` | 100% |
> | Rezdy | `CATEGORY:` prefix | ~70% |
> | Fareharbor | `tags[].name` | 59.3% |
> | CustomLinc | `productTypeCode` | 4/24 |
>
> This closes the *"`product_category` is 0% for Fareharbor and Rezdy"* gap in
> the current unified database — 20,609 products gain a category — without
> touching the Metadata API.
>
> **3. `product_category` and `product_tags` stay as TWO columns.** Category is
> *what the thing is* (`"Boat Tour"`, `"Eco-Tours"`); tags are *attributes to
> filter on* (`"Family"`, `"Beginner"`). Rezdy separates them itself via the
> `CATEGORY:` prefix; for the others, decision 2's field is the category and
> anything else is a tag. Settled by decisions 1 and 2 — no separate call needed.
>
> **4. CustomLinc `""` and `"Undefined"` are treated as BLANK.**
> `productTypeCode` is empty on 20 of 24 and literally `"Undefined"` on 2. Under
> the section 7 rule, nothing is invented to fill them.
>
> #### Shape normalisation
>
> Six sources, six shapes for one idea. All normalise to a list of plain strings:
>
> | Source | Raw shape | Note |
> |---|---|---|
> | Fareharbor | `[{"name": "Distillery"}]` | objects — read `.name` |
> | Rezdy | `["TYPE:Daytour", …]` | prefixed strings — **`.get('name')` returns nothing** (CLAUDE.md) |
> | Livn | `[{"id": 10, "name": "Full Day Trips"}]` | objects with ids — id discarded |
> | CustomLinc | `"TOUR"` | single string |
> | Ventus | `"General Flight"` | single string — one value across all 19 |
> | Ingresso | `{attractions: "Attractions", passes: "Passes"}` | object of key=value |
>
> *Unverified:* Fareharbor has 68 distinct tag values and Rezdy 146 in the
> samples measured; whether the two vocabularies can be reconciled into one
> controlled list has not been examined, and is not required by this decision.



| Unified | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|
| `product_tags` | `tags[].name` 59.3% | `tags[]` 67.7% | `categories[].name` 100% | `productTypeCode` 100% | `flight_type.name` 100% | `classes.attractions` 100% |
| `product_type` | — | `productType` 100% | — | `packageType` 16.7% | `flight_type.name` 100% | `event_type` 100% |

**Four different shapes for one concept:**

| Source | Shape |
|---|---|
| Fareharbor | list of **objects** with `.name` |
| Rezdy | flat list of **prefixed strings** (`"AGE:adult"`) |
| Livn | list of **objects** with `.id` + `.name` |
| CustomLinc / Ventus / Ingresso | a **single string** |

Calling `.get('name')` on a Rezdy tag silently returns nothing (CLAUDE.md).

---

# 9. FIELDS ONLY ONE SOURCE HAS

Worth knowing before a column is dropped for being thin — thin across the
catalogue is not the same as absent.

| Field | Only source | Fill |
|---|---|---|
| Google / TripAdvisor ratings | **Fareharbor** | 26.3% / 13.1% |
| Cancellation *type* (non-refundable etc.) | **Fareharbor** | 100% |
| Google place ID | **Fareharbor** | 73.9% |
| Price unit label | **Rezdy** | 100% |
| Booking mechanics (`bookingFields[]`, `confirmMode`) | **Rezdy** | ~100% |
| Videos | **Rezdy** | 14.5% |
| SEO tags | **Rezdy** | 35.1% |
| Supplier contact (website/email/phone/logo) | **Livn** | 100% |
| End location | **Livn** | 100% |
| Dropoff notes | **Livn** | 58.7% |
| Fit-to-fly terms | **Ventus** | 100% |
| Vehicle/yield fields | **CustomLinc** | 100% |
| Seated / add-on flags | **Ingresso** | 100% |

---

> ### DECIDED — 2026-08-19, Suyash · scope — three things NOT carried
>
> **Commission data is NOT carried.** `maxCommissionPercent` (Rezdy, 99.5%) and
> `agentPaymentType` (98.4%) do not enter the schema. This closes **D7**, which
> had been marked "needs TDU" — the answer is no. Livn's `commissionPerc` was
> already established as useless: present 167/167, value `0` on every one.
> Recoverable from the raw API if TDU later wants agents to compare margin.
>
> **Fields that are not agent-facing are NOT carried.** Supplier internals with
> no use in a browse portal:
>
> | Field | Source | Why not |
> |---|---|---|
> | `productSeoTags[]` | Rezdy 35.1% | search-engine metadata, not product information |
> | `isA` (`CT`/`PR`/`PK`/`PS`) | CustomLinc 100% | undocumented internal codes |
> | `event_subdata` | Ingresso 75% | unexamined supplier internal |
> | `opcName` | CustomLinc 100% | sometimes a code, sometimes a name; `ocbName` is the name |
>
> **The Metadata API is NOT read.** Settled in section 8 for category, and it
> holds for supplier name too — see the `meta_operator_info` block in section 2
> for what that costs.

---

# 10. UNMAPPED FIELDS — everything the sections above do NOT carry

*Added 2026-08-19 after `quantityRequiredMin`/`Max` were found missing from
section 3 — dropped by accident, not by decision. This section exists so no other
field can go missing silently.*

**Generated mechanically** by `scripts/audit_unmapped_fields.py`: every measured
path in `reports/api_structure/` whose leaf name appears nowhere in this document
or its companions. **204 non-empty leaf fields are unmapped.**

| Source | Unmapped | Of total paths |
|---|---|---|
| Fareharbor | 11 | 122 |
| Rezdy | 20 | 115 |
| Livn | 47 | 145 |
| CustomLinc | 77 | 171 |
| Ventus | 4 | 39 |
| Ingresso | 45 | 120 |

Re-run the script after any edit to this document; it is the check, not the list.

---

> ### DECIDED — 2026-08-19, Suyash · sections 10a and 10d
>
> #### 10a — ADDED. Real supplier content that reaches no column today.
>
> | Field | Source | Fill | Destination |
> |---|---|---|---|
> | `defaultPickupLocationWeb` | CustomLinc | 54% | `detail_meeting_point` — *"Hillarys Boat Harbour"*, *"At 4WD Kiosk located 100m within the dunes"* |
> | `departing` | CustomLinc | 100% | `detail_start_time` — *"10:00 AM"* |
> | `returning` | CustomLinc | 100% | `detail_return_time` — *"10:45 AM"* |
> | `breakfast_name` | Ventus | 78.9% | `detail_what_is_included` — *"Celebration Breakfast @ Three Blue Ducks"* |
> | `has_pax_breakfast` / `has_pax_transfer` | Ventus | 100% | `detail_what_is_included` |
> | `custom_field[]` | Ingresso | 6 of 7 | `detail_check_in` — *"Please proceed to the front entry of Dreamworld and follow the instructions…"* |
> | `operatingSchedule` | Livn | 26.9% | `detail_operating_days` — *"Departs Cairns daily."* |
> | `timeStartRangeMax` | Livn | 25.1% | `detail_start_time`, as a WINDOW with `timeStart` — *"09:00 – 10:30"* |
> | `durationRangeMax` | Livn | 15.6% | decided in section 7 |
> | `extras[].extraPriceType` | Rezdy | 38.7% | inside `detail_extras` text — `ANY` / `FIXED` / `QUANTITY` |
>
> Plus two mapping FIXES already recorded elsewhere: Ingresso location reads
> `venue_desc` (100%) not `venue_addr` (6.2%) — section 4; Livn's itinerary keeps
> its day labels — section 5.
>
> **`custom_field[]` was nearly dismissed.** The first entry inspected was empty;
> reading all of them, **6 of 7 hold real check-in instructions**. On a source with
> almost no text at all, that is most of what Ingresso has.
>
> **⚠ CustomLinc `departureTime` is BROKEN and must not be used** —
> `/Date(-6213556080000)` decodes to 1773. `departing` (*"10:00 AM"*) is the
> usable field.
>
> **⚠ Column-name mismatch to fix:** CLAUDE.md records that the built column is
> `return_time`, not `detail_return_time` — never renamed to the unified name.
>
> #### 10d — the three remaining fields, all KEPT
>
> | Field | Source | Fill | Decision |
> |---|---|---|---|
> | `priceOptions[].minQuantity` / `maxQuantity` | Rezdy | 4,369 options | **Keep**, inside the `product_price_options` JSON. Not a duplicate of the product-level limits: `"Group of 3"` means exactly 3 while the product allows 1–15. No new column. |
> | `taxes[].taxAmount` | Rezdy | 148 rows | **Keep.** It is a dependency of D6 — without the amount, `detail_pricing_notes` says *"a park fee applies"* instead of *"$11.00 per person"*. |
> | `classes.passes` / `.family` / `.themeparks` | Ingresso | 14/16, 1/16, 1/16 | **Keep, all four into `product_tags`**, with `attractions` also serving as `product_category`. A product can be both an Attraction and a Pass. Same multi-facet treatment as Rezdy's tags in section 8. |
>
> #### ALL RATINGS FIELDS — HELD, not in the unified schema
>
> **There is no Figma section for TripAdvisor or Google ratings, and they are
> Fareharbor-only.** The whole family is held for a later decision:
>
> | Field | Fill |
> |---|---|
> | `detail_google_rating` | 26.3% |
> | `detail_google_review_count` | 26.3% |
> | `detail_tripadvisor_rating` | 13.1% |
> | `detail_tripadvisor_reviews` | 13.1% |
> | `detail_tripadvisor_ranking` (`ranking_string` — *"#3 of 8 Transportation in Tongariro National Park"*) | 13.1% |
> | `detail_tripadvisor_badge_url` | 13.1% |
>
> **This reverses the earlier section 6 decision to ship the badge URL.** That
> decision predated the "no Figma section" test, and shipping a badge while
> holding the rating it belongs to would be incoherent. All six are recoverable
> from the raw API whenever a ratings design exists.
>
> `item.ratings` is present on 100% of Fareharbor products, so nothing is lost by
> waiting.

---

## 10a. RECOMMEND ADDING — real product data, currently dropped

Verified by reading actual values, not just fill rates.

| Field | Source | Fill | What it is | Why add |
|---|---|---|---|---|
| `defaultPickupLocationWeb` | CustomLinc | 54.2% | `"Hillarys Boat Harbour"`, `"Rottnest Island Settlement Main Bus Stop"` | **A real meeting point.** CustomLinc has no description at all — this is one of only two text fields it populates. |
| `departing` / `returning` | CustomLinc | 100% | `"10:00 AM"` and times | Departure and return time. Maps to the Figma Departure Time section, otherwise empty for this source. |
| `operatingSchedule` | Livn | 26.9% | `"Departs Cairns daily."`, `"Operates Monday, Wednesday and Saturday."` | Prose schedule. Complements `operatingDaysStr` and reads better than a day bitmask. |
| `timeStartRangeMax` | Livn | 25.1% | `"10:30:00"` | With `timeStart`, gives a departure **window** rather than a single time. |
| `durationRangeMax` | Livn | 15.6% | `360`, `2880` (minutes) | With `duration`, a duration **range**. `2880` = 2 days — these are multi-day tours. |
| `itinerary.items[].title` / `.dayFrom` / `.dayTo` | Livn | 5.4–6.0% | `"Great Barrier Reef"`, day 1 to 2 | Section 5b maps `itinerary.items[].body` but **drops the title and day numbers** — the structure that makes an itinerary an itinerary. |
| `breakfast_name` | Ventus | 78.9% | `"Buffet Breakfast"`, `"Celebration Breakfast @ Three Blue Ducks"` | A named inclusion. Belongs with `what_is_included`. |
| `has_pax_breakfast` / `has_pax_transfer` | Ventus | 100% | bool | The structured form of Ventus inclusions. Cheap filter facets. |
| `venue_desc` | Ingresso | 100% | `"Madame Tussauds Sydney"`, `"1-5 Wheat Rd, Sydney NSW 2000"` | **Ingresso's only reliable location string** — `venue_addr` is 6.2%. Section 4 maps the wrong field. |
| `custom_field[].custom_field_name` + `_data` | Ingresso | 43.8% / 37.5% | `"self_print_ticket_text"` | Supplier key/value pairs — the nearest thing Ingresso has to booking notes. |
| `ranking_string` | Fareharbor | 13.1% | `"#3 of 8 Transportation in Tongariro National Park"` | Human-readable TripAdvisor ranking. Section 8 takes the numeric parts and drops the sentence. |
| `extras[].extraPriceType` | Rezdy | 38.7% | `ANY` / `QUANTITY` / `FIXED` | How an extra is priced. Section 5b maps `extras[]` but not how to charge it. |

**Two of these are corrections, not additions:** Ingresso's location should read
`venue_desc` (100%) rather than `venue_addr` (6.2%), and Livn's itinerary is
mapped body-only, losing its day structure.

---

> ### DECIDED — 2026-08-19, Suyash · sections 10b and 10c APPROVED
>
> The ~100 fields below were previously marked "my recommendation, not approved."
> They are now **decided**, reviewed as groups.
>
> #### 10b — booking-engine plumbing: **ALL DROPPED**
> The portal is browse-only. Checkout forms, availability logic, fare-rule
> machinery, revenue-management fields and platform wiring all serve a transaction
> that never happens here.
>
> #### 10c — duplicates: **DROPPED, with two corrections**
>
> | Group | Decision |
> |---|---|
> | `_safe_html` / `_html` twins (Fareharbor ×5, Ingresso ×4) | **Drop the HTML, keep PLAIN TEXT.** Verified identical wording — only `<p>` wrappers differ. Plain is what the extraction pipeline already reads. |
> | Ingresso `country_code`, `venue_code` | **Drop.** We keep the readable `*_desc` twin. |
> | **Ingresso `source_code`** | **KEPT — not a duplicate.** It feeds `meta_supplier_id` (section 2), with `source_desc` as `meta_supplier_name`. Same id+name pairing as Rezdy's `supplierAlias` + `supplierName`. |
> | Ingresso `no_singles_cost_range` (12 fields) | **Drop.** It repeats the entire `cost_range` block — **14 of 15 values identical** on the product checked. It is a reserved-seating booking concept ("the price if no single seat is stranded"); `is_seated` is false on all 16 Ingresso products, and we do not book. |
> | Fareharbor `images[].gallery` | Already dropped — single-valued, `"carousel"` 1,719/1,719. |
> | **Livn image `width`/`height`/`fileSize`/`mimeType`** | **KEPT — this list was wrong.** Section 6 already decided to keep the full image structure with blanks elsewhere. Listing them as droppable predated that decision. |
> | Livn `supplier.nameCompany`, `nameTradingAs`, `emailRes`, `businessNumber`, `address2` | Drop — legal-entity variants of fields already carried. |
> | Fareharbor `cached_at`, `geo_location_name` | Drop — cache timestamps and a TripAdvisor locality string. (`rating_image_url` was separately KEPT — see section 6.) |
> | Ingresso `main_class_key`, `event_path`, `event_uri_desc`, `venue_uri_desc`, `event_code` | Drop — URL slugs and internal keys for fields already carried by name. |
>
> **Two of my own list entries were wrong** and are corrected above — Livn's image
> metadata and Ingresso's `source_code`. Both were flagged as duplicates before
> later decisions gave them a job. This is the third and fourth time today a
> judgement of this kind needed correcting by re-reading the data.

---

## 10b. RECOMMEND DROPPING — booking-engine plumbing

This portal is **browse-only, no booking** (CLAUDE.md). Everything here serves a
transaction we do not perform.

| Fields | Source | Why drop |
|---|---|---|
| `bookingFields[].*` (label, fieldType, required/visible ×4) | Rezdy | The checkout form definition. 99.9% filled and entirely useless without booking. |
| `isApiBookingSupported`, `isMultiProductBookingSupported`, `quantityRequired`, `confirmModeMinParticipants`, `waitListingEnabled` | Rezdy | Booking-engine capability flags. |
| `xeroAccount` (5.8%), `qrCodeType` (2.3%) | Rezdy | Supplier accounting and ticketing internals. |
| `paxNumberList`, `paxNumbers[]`, `paxQty`, `validateUsing`, `displayOrder`, `captureAge/Concession/Pensioner/Senior`, `countAsConcession/Infant/Room` | CustomLinc | Fare-rule machinery for a booking form. ~20 fields. |
| `promotionValueNet`, `priceGrossOptionsIncluded`, `transferPriceType` | CustomLinc | Internal pricing mechanics. |
| `yieldVehicle`, `yieldVehicleUnits`, `expiryMonths`, `webLeadTime`, `termFirstDay`, `termLastDay` | CustomLinc | Revenue-management and contract fields. |
| `early_horizon`, `late_horizon`, `need_departure_date`, `need_duration`, `need_performance`, `show_perf_time`, `has_no_perfs`, `is_*_add_on`, `perf_offsale_delay_seconds`, `venue_is_enforced` | Ingresso | Availability and add-on booking logic. |
| `demo`, `disabled`, `directConnect`, `usesNetRates`, `resSystem`, `catalogueProductId`, `catalogueSupplierId`, `v1Cid`, `channel.*`, `distributor.*` | Livn | Platform plumbing — Livn's own integration wiring, not product data. **~20 fields.** |
| `*.created`, `*.modified` on nested objects | Livn | Record timestamps for supplier/channel/distributor rows. |
| `valid`, `event_status`, `charter` | Ventus / Ingresso / Rezdy | Single-valued in the data (`True`, `"live"`, mostly `False`). Carry no information. |

---

## 10c. RECOMMEND DROPPING — duplicates of a mapped field

Not plumbing; the **same content already carried elsewhere**.

| Field | Source | Duplicate of | Note |
|---|---|---|---|
| `description_safe_html`, `booking_notes_safe_html`, `cancellation_policy_safe_html`, `health_and_safety_policy_safe_html`, `note_safe_html` | Fareharbor | their non-`_safe_html` twins | Identical fill rates. Same text, two encodings — **pick one and document which**. |
| `event_info_html`, `venue_addr_html`, `custom_field_data_html`, `structured_info.*.value_html` | Ingresso | their non-`_html` twins | Same. |
| `images[].height/width/mimeType/fileSize`, `supplier.logo.height/width/mimeType/title` | Livn | `images[].url` | Media metadata. Add only if the front end needs dimensions for layout. |
| `images[].gallery` | Fareharbor | — | `"carousel"` on 196 of 200. Single-valued in practice. |
| `cached_at`, `geo_location_name`, `rating_image_url` | Fareharbor | `ratings.*` | Cache timestamps and a TripAdvisor badge image. |
| `locationsEnd[].continent`, `streetAddressAccuracy`, `district`, `building`, `landmark` | Livn | `locationsStart[]` / `location_*` | Address sub-components below the granularity the schema carries. |
| `area_code`, `city_code`, `country_code`, `venue_code`, `event_code`, `main_class_key`, `event_path`, `event_uri_desc`, `venue_uri_desc` | Ingresso | `*_desc` twins | Code forms of fields already mapped by their description. |
| `cost_range.*surcharge_tax_sub_component`, `no_singles_cost_range.*` (12 fields) | Ingresso | `cost_range` | Sub-components of a price we take one number from. `no_singles_*` duplicates the whole structure for a booking case we do not handle. |
| `supplier.nameCompany`, `nameTradingAs`, `emailRes`, `businessNumber`, `address2` | Livn | `supplier.name`, `.email` | Legal-entity variants. Useful internally; not portal data. |

---

## 10d. NEEDS A DECISION — genuinely ambiguous

Neither obviously product data nor obviously plumbing.

| Field | Source | Fill | The question |
|---|---|---|---|
| `productSeoTags[].attrKey` / `.attrValue` / `.metaType` | Rezdy | 35.1% | SEO metadata the supplier wrote. Could enrich `product_tags`, or could be keyword spam. **Needs a look at the values.** |
| `priceOptions[].minQuantity` / `.maxQuantity` | Rezdy | 13.2% | Per-price-option quantity limits, **separate from** the product-level `quantityRequiredMin/Max` now in section 3. Two levels of the same concept. |
| `taxes[].taxAmount` | Rezdy | 1.4% | A **fixed-amount** tax rather than a percent. Rare, but it is the shape D6 says the schema cannot express. |
| `classes.attractions` / `.passes` / `.family` / `.themeparks` | Ingresso | 100% / 87.5% / 6.2% | Category taxonomy. Section 8 maps `classes.attractions` only; the other three are also categories. |
| `event_subdata` | Ingresso | 75.0% | Unexamined. The name suggests supplementary content. |
| `isA`, `packageType`, `productTypeCode` | CustomLinc | 100% / 16.7% | `isA` is `CT`/`PR`/`PK`/`PS` — undocumented codes. Product type is already mapped from `productTypeCode`; these may be finer classification or may be redundant. |
| `defaultDepartureDate`, `departureDate` | CustomLinc | 100% | Two date fields plus `departureTime`. Relationship unclear. |
| `fareTypes[].shortName`, `.fareType`, `.isVehicle` | CustomLinc | 100% | `isVehicle` is the cleanest per-unit flag in any source (see section 3) — but on 24 products. Worth carrying only if `product_price_unit` ships. |

---

## 10e. The rule this section enforces

**A field is dropped only by decision, recorded here.** Anything absent from
sections 1–9 and from this section is an omission, not a choice —
`audit_unmapped_fields.py` will find it.

The governing rule from `UNIFIED_SCHEMA_PROPOSED.md` is *sparsity is fine,
coverage is not optional*. Note that 10b and 10c do not contradict it: that rule
is about **thin product data**, which is kept. Booking plumbing and duplicate
encodings are not thin product data.

---

# What this says about the schema

**1. It is two sources plus four exceptions.** Fareharbor and Rezdy are 98.9% of
rows. Livn, CustomLinc, Ventus and Ingresso together are 226 products. Designing
the schema around all six equally over-weights 1.1% of the catalogue.

**2. Coverage decisions cannot be made on Fareharbor's fill rates.** Several
columns Fareharbor barely fills are near-100% elsewhere — `highlights` (Livn
100%), `what_is_included` (Livn 100%, Ventus 100%), `health_safety` (Ventus
100%), `languages` (Rezdy 99.7%). **D11's "thin in every source" test has to be
run across all six, and this table is the input for it.**

**3. Commission is Rezdy-only.** D7's scope is right. Livn's `commissionPerc`
looks like a second source but is `0` on all 167 products — a field that exists
and says nothing.

**4. Price is the least comparable field in the schema.** Four of six sources
supply a *minimum* or *"from"* price, not a price. Any portal that renders
`product_price` as "the price" is wrong on those four.

**5. CustomLinc contributes no product text** — 24 products, four mapped
description fields, all empty on every file. But it **does** have prices, in
`fareTypes[]` (gross and net, 24/24); the `lowestPrice` summary field is the part
that is empty. Its rows will be name, price, fare types and schedule, with no
prose. Decide whether that is worth shipping.

**See `PRICE_FIELD_TYPES.md` for the JSON type and a real value behind every cell
of the price table.**

**6. Two of six sources have no images.** Ingresso supplies none; CustomLinc's
field is empty on all 24.

---

## Provenance

Generated by `scripts/build_api_structure_docs.py` →
`reports/api_structure/{Source}_api_structure.txt`. Fareharbor and Rezdy sampled
at 1,199 files (random, seed 42); the other four read in full.

**Independently re-verified for this document:**

- Fareharbor `structured_description` accessibility / min_age / max_age /
  group_size, and both rating families, recomputed directly from `data/Fareharbor/*.json`.
- CustomLinc's four mapped description fields checked against **all 24** raw
  files — 0/24 filled on each.
- Rezdy `unitLabel` distribution recomputed from `data/Rezdy/*.json`.
- Livn `highlights` / `inclusions.items` confirmed 167/167 filled, and
  `commissionPerc` confirmed present 167/167 but **zero-valued on every one**.
  An earlier draft of this document read that 100% presence as 100% coverage;
  it was wrong and is corrected above.

**Not verified here:** the 288 surplus Fareharbor and 130 missing Rezdy products
(D3); all figures are from files on disk, not the Metadata API. Ventus (19),
Ingresso (16) and CustomLinc (24) are complete populations, so their percentages
are exact but statistically fragile — one product is 4–6%.

---

# THE UNIFIED SCHEMA

*Generated 2026-08-19 from the decisions above. **Fill percentages are measured**,
read from `reports/api_structure/` — the same documents every decision in this
file was made from. `—` means the source has no field for that concept, and a
blank there is correct, not a gap.*

**Scope: 6 sources, 20,835 products.** TDU excluded (no pipeline exists).
**Details API only** — the Metadata API is not read.

## Column count

| Group | Columns |
|---|---|
| Identity | 4 |
| Supplier | 3 |
| Listing & price | 10 |
| Location | 8 |
| Detail | 24 |
| Media | 2 |
| Provenance | 2 |
| **Total** | **59** |


## 1. Identity — 4

| Column | Type | Holds | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|---|---|
| `product_id` | `str` | Supplier product key. **Text always** — Rezdy and Ingresso are non-numeric. | `pk` 100% | `productCode` 100% | `id` 100% | `code` 100% | `filename` | `event_id` 100% |
| `source` | `str` | Which supplier system. With `product_id`, the compound key. | — | — | — | — | — | — |
| `product_name` | `str` | Product title. | `name` 100% | `name` 100% | `name` 100% | `name` 100% | `name` 100% | `event_desc` 100% |
| `product_headline` | `str` | Short tagline. Each source means something different by it. | `headline` 92% | `shortDescription` 100% | `nameOriginal` 100% | — | — | — |

> `product_id` is TEXT for every source — a mixed column renders Livn's `72` as `72.0`.
> **Ventus has no internal ID on any of its 19 files**; the filename is the only source of truth.
> **CustomLinc must read `code` from inside the file** — the filename truncates 14 of 24 and collides two products on `BIT1115`.


## 2. Supplier — 3

| Column | Type | Holds | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|---|---|
| `meta_supplier_id` | `str` | Supplier key. | — | `supplierAlias` 100% | `supplier.id` 100% | `ocb` 100% | — | `source_code` 100% |
| `meta_supplier_name` | `str` | Supplier company name. | — | `supplierName` 100% | `supplier.name` 100% | `ocbName` 100% | — | `source_desc` 100% |
| `meta_operator_info` | `str` (JSON) | Everything the supplier gives about the operator — name, description, phone, email, website, address, logo. Feeds the Figma **Operator Information** section. | `contact_text` only, **2.3%** | name only | **all 7 keys**, 100% | name only | — | name only |

> **Fareharbor and Ventus are blank** — their Details APIs carry no supplier data at all.
> 11,255 products (54%). The old file filled this from the *filename*; that is derived, not
> supplied, so it is dropped. Low impact — `meta_*` is internal and never displayed.


## 3. Listing & price — 10

| Column | Type | Holds | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|---|---|
| `product_price` | `float` | Headline price. **Fareharbor is CENTS — divide by 100.** | `total_including_tax` 100% | `advertisedPrice` 100% | `fromPrices[].amount` 100% | `fareTypes[].priceGross` 100% | `pricing[].price` 100% | `cost_range.min_combined` 100% |
| `product_currency` | `str` | 3-letter code, **uppercased** — Ingresso ships `"aud"`. | — | `currency` 100% | `fromPrices[].currency` 100% | `currency` 100% | — | `currency_code` 100% |
| `product_price_unit` | `str` | **D5.** What the price is *per*, verbatim. 10.7% of Rezdy is not a person. | — | `unitLabel` 100% | — | `fareTypes[].fareType` 100% | `attribute_name` 100% | — |
| `product_price_tax_inclusive` | `str` | **D6.** `"true"` / `"false"` / `""` — three states, not a bool. | — | `taxes[].priceInclusive` 55% | — | — | — | — |
| `product_price_options` | `str` (JSON) | Every ticket type. 13 keys — see below. | `customer_prototypes[]` 100% | `priceOptions[]` 99% | — | `fareTypes[]` 100% | `pricing[]` 100% | `ticket_type[]` 100% |
| `product_min_quantity` | `float` | Smallest bookable quantity, in `product_price_unit`. | — | `quantityRequiredMin` 100% | — | — | — | — |
| `product_max_quantity` | `float` | Largest. Null = not stated, **not** unlimited. | — | `quantityRequiredMax` 81% | `groupSizeMax` 4% | — | — | — |
| `product_duration` | `str` | Supplier's own words. Never derived. | `sd.duration` 43% | — | — | `durationLong` 100% | — | — |
| `product_duration_minutes` | `float` | Minutes, only where stated as a number. `0` → blank. | — | `durationMinutes` 94% | `duration` 100% | — | — | — |
| `product_category` | `str` | What kind of thing this is. | `tags[].name` 59% | ``CATEGORY:` tags` 68% | `categories[].name` 100% | `productTypeCode` 100% | `flight_type.name` 100% | `classes.attractions` 100% |
| `product_tags` | `str` (JSON) | Filterable attributes. | `tags[].name` 59% | `non-CATEGORY tags` 68% | `categories[].name` 100% | — | — | `classes.*` 88% |

> **`product_price_options` object — 13 keys.** One shape, blank where a source gives less:
>
> ```json
> {"label": "Adult", "price": 35.0, "price_ex_tax": null, "price_net": 26.25,
>  "age_min": 0, "age_max": 0, "min_quantity": 1, "max_quantity": 25,
>  "is_vehicle": false, "seats_used": null, "rate_type": null,
>  "note": "Ages 18+", "source_option_id": "ADULT"}
> ```
>
> `note` (Fareharbor 68.4%) carries age rules in prose — *"Ages 5-12"*,
> *"60+ and ID Required!"*, *"Total of 2 people/buggy"* — covering products where
> the numeric age fields are empty.


## 4. Location — 8

| Column | Type | Holds | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|---|---|
| `location_street` | `str` | Street address | `street` 74% | `addressLine` 77% | `address1` 70% | `defaultPickupLocationWeb` 54% | — | `venue_desc` 100% |
| `location_city` | `str` | City | `city` 74% | `city` 84% | `city` 100% | — | `name` 100% | `city_desc` 75% |
| `location_state` | `str` | State / province | `province` 74% | `state` 78% | `state` 100% | — | — | — |
| `location_country` | `str` | Country — **normalise to 2-letter code** | `country` 74% | `countryCode` 91% | `country` 100% | — | — | `country_desc` 100% |
| `location_postcode` | `str` | Postcode | `postal_code` 74% | `postCode` 76% | `postcode` 100% | — | — | `postcode` 100% |
| `location_latitude` | `str` | GPS latitude | `latitude` 74% | `latitude` 100% | `latitude` 100% | — | — | `latitude` 100% |
| `location_longitude` | `str` | GPS longitude | `longitude` 74% | `longitude` 100% | `longitude` 100% | — | — | `longitude` 100% |
| `location_end` | `str` | Finish point, where different | — | — | `city` 100% | `endLocation` 8% | — | — |

> **Fareharbor reads `locations[]` (74%), NOT `primary_location` (21%)** — the latter is a
> copy of `locations[0]`, and switching gains ~6,000 products with nothing lost.
> Take `type == "primary"`, else the first: 761 of 885 products have exactly one.


## 5. Detail — 24

| Column | Type | Holds | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|---|---|
| `detail_description` | `str` | Main description — the default destination for un-headed text | `description` 99% | `description` 100% | `description` 100% | — | `description` 37% | `event_info` 19% |
| `detail_highlights` | `str` | Key selling points | `sd.highlights` 20% | — | `highlights.highlights[]` 100% | — | — | — |
| `detail_what_is_included` | `str` | What's included | `sd.what_is_included` 39% | — | `inclusions.items[].content` 100% | — | `inclusions.non_flight_items[]` 100% | — |
| `detail_what_is_not_included` | `str` | What's excluded | `sd.what_is_not_included` 15% | — | — | — | — | — |
| `detail_itinerary` | `str` | Route / day-by-day. **Livn keeps its day labels.** | `sd.itinerary` 16% | — | `itinerary.items[].body` 6% | — | — | — |
| `detail_important_info` | `str` | General notes — catch-all | — | `additionalInformation` 42% | — | — | — | — |
| `detail_booking_notes` | `str` | Booking notes | `booking_notes` 73% | `additionalInformation` 42% | `pickupNotes` 87% | — | — | — |
| `detail_meeting_point` | `str` | Where to meet | `sd.meeting_point` 47% | — | `locationsStart[].business` 70% | `defaultPickupLocationWeb` 54% | — | — |
| `detail_check_in` | `str` | Arrival instructions | `sd.check_in_details` 21% | — | — | — | — | `custom_field[].custom_field_data` 38% |
| `detail_departure_info` | `str` | Departure details | — | — | — | — | — | — |
| `detail_before_arrival` | `str` | Before you arrive | — | — | — | — | — | — |
| `detail_what_to_bring` | `str` | What to bring. **Includes "Do not bring:" items.** | `sd.what_to_bring` 22% | — | `specialNotes` 100% | — | — | — |
| `detail_accessibility` | `str` | Accessibility | `sd.accessibility` 10% | `tags[]` 68% | — | — | — | — |
| `detail_restrictions` | `str` | Who can take part | `sd.restrictions` 14% | `tags[]` 68% | — | — | — | — |
| `detail_special_requirements` | `str` | Dietary, medical, disability needs | `sd.special_requirements` 12% | — | `specialNotes` 100% | — | — | — |
| `detail_health_safety` | `str` | Health & safety | `health_and_safety_policy` 7% | — | `specialNotes` 100% | — | `terms.fit_to_fly_terms` 100% | — |
| `detail_group_size` | `str` | Group size, in prose | `sd.group_size` 20% | — | `groupSizeMax` 4% | — | — | — |
| `detail_faqs` | `str` | FAQs | `sd.faqs` 11% | — | — | — | — | — |
| `detail_extras` | `str` | Optional add-ons. **Rezdy `extras[]` as `[API]` text.** | `sd.extras` 7% | `extras[]` 39% | `specialNotes` 100% | — | — | — |
| `detail_disclaimers` | `str` | Legal text | `sd.disclaimers` 16% | `terms` 34% | `supplier.tnc` 72% | — | `terms.booking_terms` 37% | — |
| `detail_cancellation_policy` | `str` | Cancellation policy | `cancellation_policy` 98% | `terms` 34% | — | — | `terms.booking_terms` 37% | — |
| `detail_cancellation_hours` | `str` | Notice period. **Rezdy is DAYS — convert. `9999` = non-refundable.** | `effective_cancellation_policy.cutoff_hours_before` 100% | `cancellationPolicyDays` 77% | — | — | — | — |
| `detail_pricing_notes` | `str` | How pricing works + **D6 fees outside the price** | `sd.pricing` 6% | `taxes[]` 55% | `specialNotes` 100% | — | — | — |
| `detail_tax_percentage` | `str` | Tax rate as a percent | `tax_percentage` 100% | `taxes[].taxPercent` 54% | — | — | — | — |

> **Every detail column carries SOURCE TAGS.** Where more than one place supplies a
> concept, all are kept and labelled — `[API]` / `[DESCRIPTION]` / `[BOOKING NOTES]` /
> `[ADDITIONAL INFO]` / `[TERMS]`, `[API]` first, **always tagged even when there is
> only one block**. Nothing merged, nothing de-duplicated.
>
> **The front end MUST strip the tags before display** — one regex on
> `^\[[A-Z ]+\]\s*`. This is a required integration step, not optional.
>
> Rezdy columns marked `tags[]` are fed by its prefix split — `ACCESSIBILITY:`
> (1,042 tags) and `AGE:` (1,833) route to their own columns rather than to
> `product_tags`.


## 6. Media — 2

| Column | Type | Holds | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|---|---|
| `product_images` | `str` (JSON) | All images, cover flagged `is_main`. | `images[]` 96% | `images[]` 94% | `images[]` 99% | — | `images[]` 100% | — |
| `product_videos` | `str` (JSON) | Videos with platform. | — | `videos[]` 14% | — | — | — | — |

> **Image object:** `source_image_id` · `url` · `is_main` · `thumbnail_url` ·
> `medium_url` · `large_url` · `width` · `height` · `file_size` · `mime_type`.
>
> **The cover is sometimes a photo found nowhere in `images[]`** — 35 of 600
> Fareharbor products (~1,000 at full scale). It is **added to the list** at
> position 0 with `is_main: true`.
>
> **`is_main` means two things:** the supplier's own choice on Fareharbor, our
> convention (first in list) elsewhere — no other source has a cover field.
> **Tell the web team: find `is_main == true`, do not take the first entry.**


## 7. Provenance — 2

| Column | Type | Holds | Fareharbor | Rezdy | Livn | CustomLinc | Ventus | Ingresso |
|---|---|---|---|---|---|---|---|---|
| `compound_key` | `str` | `{product_id}` + `{source}` — the primary key | — | — | — | — | — | — |
| `extractions_present` | `str` | Which extractions ran, so "supplier wrote nothing" is distinguishable from "we lost it" | — | — | — | — | — | — |

---

## Held for a later decision — NOT in the schema

Real supplied data, deliberately parked. All recoverable from the raw API.

| Fields | Source | Why held |
|---|---|---|
| 10 supplier fields — website, email, phone, logo, description, address, city, state, postcode, country | Livn 100% (phone 85%) | `meta_*` is internal; `id` + `name` is enough for now |
| 6 ratings fields — Google rating & count, TripAdvisor rating, reviews, ranking, badge URL | Fareharbor 26.3% / 13.1% | **No Figma section for ratings**, and Fareharbor-only |
| `extras[].image` (4 sizes) | Rezdy 33.1% | No Figma design for a priced add-on with a picture |

## Dropped, by decision

| Group | Count | Why |
|---|---|---|
| Booking-engine plumbing | ~60 | Browse-only portal — checkout forms, availability logic, fare rules |
| `_safe_html` / `_html` twins | 9 | Same words as the plain field, `<p>` tags only |
| Ingresso `*_code` where `*_desc` is kept | 2 | `source_code` is the exception — it is `meta_supplier_id` |
| `no_singles_cost_range` | 12 | Repeats `cost_range`; 14 of 15 values identical |
| Metadata API `duration` | — | 38% of values under 1 hour, corrupt and correct indistinguishable |
| CustomLinc `duration` | — | `durationLong` minus the unit word — 24/24 |
| Commission (`maxCommissionPercent`, `agentPaymentType`) | 2 | **D7 — not carried** |
| Not agent-facing (`productSeoTags`, `isA`, `event_subdata`, `opcName`) | 4 | Supplier internals |
| Fareharbor `images[].gallery` | 1 | Single-valued, `"carousel"` 1,719/1,719 |

## The five rules the schema follows

1. **Source tags** — several sources feeding one column are all kept and labelled.
2. **Generate nothing** — a blank is an acceptable answer.
3. **"Only one source has it" is not a reason to drop it.**
4. **Nothing removed, only redirected** — every drop above is a recorded decision.
5. **Topic headings get no column** — supplier section names that are not field names stay in `detail_description`.

---

---

# DECISIONS REGISTER

*16 decisions, all taken 2026-08-19, in document order. Each has a dated
block in the section named, stating the evidence it rests on.*

| # | Decision | Section |
|---|---|---|
| 1 | Identity — ids, headline, the CustomLinc filename trap | 1. IDENTITY |
| 2 | `meta_operator_info` — one JSON column for the Figma Operator panel | 2. SUPPLIER |
| 3 | Supplier — two columns, Rezdy uses `supplierAlias` | 2. SUPPLIER |
| 4 | D5 price unit · D6 fees outside the price | 3. PRICE |
| 5 | Quantity limits — `product_min_quantity` / `product_max_quantity` | 3. PRICE |
| 6 | Location — read `locations[]`, not `primary_location` | 4. LOCATION |
| 7 | **THE SOURCE-TAG RULE** — governs every text column | 5. DESCRIPTION AND DETAIL |
| 8 | Livn itinerary · Livn `specialNotes` split · thin columns | 5. DESCRIPTION AND DETAIL |
| 9 | Products with no description are included, left blank | 5. DESCRIPTION AND DETAIL |
| 10 | Media — image JSON, `is_main`, the missing cover | 6. MEDIA |
| 11 | Extras — `[API]`-tagged text, no longer blocked on design | 6. MEDIA |
| 12 | Schedule & duration — generate nothing | 7. SCHEDULE AND DURATION |
| 13 | Tags & category — split Rezdy by prefix, no Metadata API | 8. TAGS AND CATEGORY |
| 14 | Scope — commission, non-agent-facing fields, Metadata API | 9. FIELDS ONLY ONE SOURCE HAS |
| 15 | 10a additions · 10d leftovers · ratings held | 10. UNMAPPED FIELDS — everything the sections above do NOT carry |
| 16 | 10b/10c — ~100 drops approved | 10. UNMAPPED FIELDS — everything the sections above do NOT carry |

## The rules every decision follows

| Rule | Where it was set |
|---|---|
| **Source tags** — several sources feeding one column are all kept, each labelled `[API]` / `[DESCRIPTION]` / `[BOOKING NOTES]` / `[ADDITIONAL INFO]` / `[TERMS]`. `[API]` leads. Always tagged, even a single block. | §5 |
| **Generate nothing.** A blank is an acceptable answer; never invent or derive a value. | §7 |
| **"Only one source has it" is not a reason to drop it.** Keep the fullest structure; blank where a supplier gives less. | §6 |
| **Nothing is removed, only redirected.** A field may change column; it may not silently vanish. | throughout |
| **Topic headings get no column.** Supplier section names that are not field names stay in `detail_description`. | §5, §8 |

## Corrections made during this work

Recorded because each was a judgement that looked right and was not. All were
caught by re-reading the raw data rather than by reviewing the reasoning.

| # | Claim | What was actually true |
|---|---|---|
| 1 | CustomLinc has no price | It has prices in `fareTypes[]` on 24/24. `lowestPrice` is an unpopulated summary field. |
| 2 | Livn supplies commission | The field is present on 167/167 and its value is `0` on every one. |
| 3 | Livn image metadata is a droppable duplicate | Already kept by the §6 decision; the list predated it. |
| 4 | Ingresso `source_code` is a redundant code | It is `meta_supplier_id`. |
| 5 | Fareharbor cover == `images[0]` | Different on 35 of 600; on those the cover appears nowhere else in the gallery. |
| 6 | Switching Fareharbor location gains ~6,000 products | The ETL already read `locations[]`. Only CLAUDE.md's mapping table was wrong. |
| 7 | Supplier data is internal and never displayed | The Figma prototype has an Operator Information section. Ten Livn fields were held on this premise and now ship. |
| 8 | D5 affects 1,460 products (16%) | 1,004 (10.7%), counting `Rider` and `Kayaker` as people. |

