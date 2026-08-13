# Fareharbor — every column we have, and what to do with each

*Built 2026-08-13. Every number computed from the actual files.*

**The 500 products** = the IDs in `booking_v5_4_500_output.jsonl`. All 500 also have
description extraction (from the full-catalogue `v5_3_full_output.jsonl`) and a row
in `exports/fareharbor_etl_v2.csv`. Nothing missing, nothing failed to parse.

**116 columns today** — 22 description + 25 booking + 69 API/ETL.
**Proposal below: 48 columns for the dev team, + 8 in a separate internal file.**

---

## How to read the two new columns

**`Unified column`** — the NEW name. We are **copying, not renaming**. Every original
column stays exactly where it is; the unified column is an additional column built
from it. Nothing in `fareharbor_etl_v2.csv` or the extraction JSON is touched.

**`Do`** — my recommendation, for you to overrule:

| Mark | Meaning |
|---|---|
| **KEEP** | Becomes a unified column on its own. |
| **MERGE** | Combines with other columns into one unified column. |
| **FALLBACK** | Only used when the higher-priority source is empty (Rule #10). |
| **DELETE** | Don't carry it forward. Original file untouched — just not copied. |
| **DECIDE** | I have a recommendation but it's genuinely your call. |

**MERGE does not mean "glue both together" — see Section 5.** An earlier version of
this document said it did, based on exact string matching that showed the two sides
were "almost never identical". Measured properly with fuzzy matching, **58% of
collisions are the same content twice**, and gluing them would print duplicate
paragraphs on the product page. The real rule is three-band and is set out in Section 5
with worked examples.

**Nothing is ever deleted.** The unified column is a new copy. `redo_desc_*` and
`redo_booking_*` stay exactly as they are, so any merge decision is reversible.

---

## Where each unified column lands on the Figma page

| Figma section | Unified column(s) |
|---|---|
| Title / subtitle | `product_name`, `product_headline` |
| Chip row | `product_duration`, `location_city`, `detail_accessibility`, `detail_cancellation_hours` |
| Gallery | `product_main_image`, `product_images` |
| About the Experience | `detail_description` |
| Tour Highlights | `detail_highlights` |
| What's Included | `detail_what_is_included` |
| **What's Not Included** *(not in Figma — proposed)* | `detail_what_is_not_included` |
| Cruise Route / Itinerary | `detail_itinerary` |
| Important Information → Know Before You Travel | `detail_important_info` |
| Important Information → Booking Notes | `detail_booking_notes` |
| Accessibility | `detail_accessibility` |
| Onboard Facilities chips | **no source — see Gap 3** |
| Cancellation Policy | `detail_cancellation_policy`, `detail_cancellation_hours` |
| Operator Information | `meta_supplier_name`, `detail_operator_contact` |
| Price box | `product_price`, `product_currency`, `product_price_options` |
| Meeting Point | `detail_meeting_point`, `location_*` |

---

## 1. Description — extracted columns (22)

| Column | What it holds | Fill % | Key insight | Unified column | Do |
|---|---|---|---|---|---|
| `redo_desc_about` | Main narrative. Default home for unheaded text. | **100%** | Only column that never empties. Everything unrouted lands here — nothing is lost, only unlabelled. | `detail_description` | **KEEP** — primary, no competition |
| `redo_desc_duration_text` | Duration as written. | 30.0% | Median 11 chars ("2 hours"). API `duration_text` covers 50.6%. | `product_duration` | **FALLBACK** — behind API |
| `redo_desc_what_included` | What the price covers. | 24.4% | Most-flagged field (35 flags) — least settled of the high-fill columns. | `detail_what_is_included` | **MERGE** + booking |
| `redo_desc_important_info` | Must-know items. | 22.8% | 67 products fill both sides, **0 identical**. | `detail_important_info` | **MERGE** + booking |
| `redo_desc_restrictions` | Age, health, fitness, weight. | 22.6% | Booking fills 115, this 113, only 58 overlap, **0 identical**. Also where age lives. | `detail_restrictions` | **MERGE** + booking |
| `redo_desc_pricing` | Price notes in the prose. | 17.6% | Median 45 chars — footnotes, never the price. | `detail_pricing_notes` | **MERGE** + booking |
| `redo_desc_what_to_bring` | Packing list. | 12.2% | Booking finds this **3.6× more often**. | `detail_what_to_bring` | **MERGE** — booking primary |
| `redo_flags` | Model's own uncertainty notes. | 11.2% | QA metadata. Concentrated on `what_included` (35), `itinerary` (20), `pricing` (10) — your defect-hunt order. | `meta_desc_flags` | **INTERNAL FILE** — not in dev's table |
| `redo_meeting_point` | Where to meet. | 10.0% | Booking finds 124 vs this 50. | `detail_meeting_point` | **MERGE** — booking primary |
| `redo_desc_accessibility` | Wheelchair / mobility. | 5.4% | 27 fills but **4 distinct values** — 21 are literally `"CLICK HERE for accessibility information"`. A link, not data. | `detail_accessibility` | **MERGE** + booking, **plus a rule that drops link-only values** |
| `redo_desc_disclaimers` | Liability text. | 5.0% | 25 fills, 5 distinct — 21 are one operator's allergen boilerplate. | `detail_disclaimers` | **MERGE** + booking (zero overlap) |
| `redo_desc_what_excluded` | Not covered by the price. | 4.4% | 22 fills, 9 distinct — 13 are the same "Fully licensed bar" line. | `detail_what_is_not_included` | **MERGE** + booking — Decision A: own section, hidden when empty |
| `redo_desc_cancellation` | Refund terms from prose. | 4.4% | API carries a real policy on 98%. | `detail_cancellation_policy` | **FALLBACK** — API wins |
| `redo_desc_highlights` | Selling points. | 4.2% | 21 products. Figma has a Highlights section — **it renders empty for ~94%**. | `detail_highlights` | **MERGE** + booking — Decision B: keep section, hide when empty |
| `redo_desc_extras` | Paid add-ons. | 3.4% | 17 fills, 6 distinct — 11 are one wetsuit line. | `detail_extras` | **MERGE** + booking |
| `redo_desc_itinerary` | Timed run-of-day. | 3.2% | Only 16, but 2nd most-flagged (20). Low volume, high uncertainty. | `detail_itinerary` | **MERGE** + booking |
| `redo_group_size` | Group size limits. | 2.2% | 11 products — **not dead**, unlike the booking side's 0. Fills a gap: FH's old `detail_group_size` was 100% empty. | `detail_group_size` | **KEEP** — only source |
| `redo_desc_check_in` | Check-in time / procedure. | 1.8% | 9 vs booking's 96. | `detail_check_in` | **MERGE** — booking primary |
| `redo_desc_faqs` | Q&A blocks. | 0.6% | 3 products, median **3,970 chars**. Rare and enormous. | `detail_faqs` | **MERGE** + booking |
| `redo_desc_special_requirements` | Dietary / access requests. | **0%** | Never fired. Booking fills it 17×. | `detail_special_requirements` | **DELETE** — booking is the only source |
| `redo_min_age` | Minimum age. | **0%** | Empty **by design** — age routes to `restrictions`. Not a defect. | — | **DELETE** — Decision C settled |
| `redo_max_age` | Maximum age. | **0%** | Same. | — | **DELETE** — Decision C settled |

---

## 2. Booking notes — extracted columns (25)

| Column | What it holds | Fill % | Key insight | Unified column | Do |
|---|---|---|---|---|---|
| `redo_booking_notes` | Catch-all for unheaded booking text. | **88.8%** | Booking's equivalent of `about`. Median 986 chars. High fill = most booking text still isn't routed — biggest remaining opportunity. | `detail_booking_notes` | **KEEP** — Figma "Booking Notes" |
| `redo_booking_flags` | Model uncertainty notes. | 75.8% | Dominated by omitted greetings/sign-offs (134+96+66+28+25) which are **correct** omissions. Filter those before reading as problems. | `meta_booking_flags` | **INTERNAL FILE** — not in dev's table |
| `redo_booking_what_to_bring` | Packing list. | **44.4%** | Most valuable booking-only column. 222 vs desc's 61, only 8 overlaps identical. | `detail_what_to_bring` | **MERGE** — primary |
| `redo_booking_important_info` | Must-know items. | 37.0% | 185 vs 114, 67 overlap, **0 identical**. | `detail_important_info` | **MERGE** — primary |
| `redo_booking_meeting_point` | Where to meet. | 24.8% | **2.5× the description.** Largely closes the known meeting-point gap. | `detail_meeting_point` | **MERGE** — primary |
| `redo_booking_restrictions` | Age / health / fitness. | 23.0% | 115 vs 113, only 58 overlap, none match. Two disjoint halves. | `detail_restrictions` | **MERGE** |
| `redo_booking_check_in` | Check-in time / desk. | 19.2% | 96 vs desc's 9. The old ETL misfiled exactly this class into `desc_booking_notes`. | `detail_check_in` | **MERGE** — primary |
| `redo_booking_what_included` | What the price covers. | 15.8% | 34 overlaps, **0 identical**. | `detail_what_is_included` | **MERGE** |
| `redo_booking_health_safety` | Safety / medical warnings. | 15.4% | Median 749 chars. **Beats the API's own `health_safety` (9.6%)** — AI outperforms the dedicated field. | `detail_health_safety` | **MERGE** — primary, API second |
| `redo_booking_disclaimers` | Liability text. | 13.4% | 67 vs 25, **zero overlap at all**. Completely disjoint. | `detail_disclaimers` | **MERGE** — primary |
| `redo_booking_faqs` | Q&A blocks. | 13.2% | 66 vs desc's 3 — **22×**. FAQs are a booking phenomenon. | `detail_faqs` | **MERGE** — primary |
| `redo_booking_before_arrival` | Forms, prep, advance steps. | 10.4% | Booking-only — no description counterpart exists. | `detail_before_arrival` | **KEEP** — new field, real value |
| `redo_booking_departure_info` | Departure point / timing. | 8.6% | Figma's Meeting Point block already carries departure text ("arrive 15–30 min before your departure time"). | `detail_departure_info` | **KEEP separate** — Decision D settled: not merged |
| `redo_booking_cancellation` | Refund terms. | 7.0% | API has a policy on 98%. | `detail_cancellation_policy` | **FALLBACK** |
| `redo_booking_accessibility` | Wheelchair / mobility. | 5.2% | 26 fills and **25 also fill the description** — the only near-total collision, yet only 2 identical. | `detail_accessibility` | **MERGE** — worth a manual look |
| `redo_booking_contact` | Phone, email, who to call. | 4.6% | Booking-only. Figma has a Contact Information block. | `detail_operator_contact` | **KEEP** — Decision E: ship as one text blob |
| `redo_booking_pricing` | Price notes. | 4.4% | Footnote role, never the price. | `detail_pricing_notes` | **MERGE** |
| `redo_booking_extras` | Paid add-ons. | 4.2% | 8 overlaps, none identical. | `detail_extras` | **MERGE** |
| `redo_booking_duration_text` | How long it runs. | 3.8% | 19 vs desc's 150. Duration is a description concept. | `product_duration` | **FALLBACK** — lowest priority |
| `redo_booking_special_requirements` | Dietary / access requests. | 3.4% | Description side is **0**. This column exists only because of booking. | `detail_special_requirements` | **KEEP** — only source |
| `redo_booking_itinerary` | Run-of-day. | 3.2% | 16, same as desc, only 4 overlap. Both thin. | `detail_itinerary` | **MERGE** |
| `redo_booking_what_excluded` | Not included. | 2.6% | 13 products. Thinnest useful column. | `detail_what_is_not_included` | **MERGE** |
| `redo_booking_highlights` | Selling points. | 2.2% | With desc's 21, Highlights has content for ~6% of products. | `detail_highlights` | **MERGE** — see Decision B |
| `redo_booking_what_not_to_bring` | Prohibited items. | 1.6% | 8 products. Booking-only. | `detail_what_not_to_bring` | **KEEP separate** — merging "bring" with "don't bring" would invert the meaning |
| `redo_booking_group_size` | Group size limits. | **0%** | **Never fired in 500.** Description side fires 11×. The booking heading rule is what's broken, not the concept. | — | **DELETE** from booking side |

---

## 3. API / ETL columns (69)

### 3a. Identity (4)

| Column | What it holds | Fill % | Key insight | Unified column | Do |
|---|---|---|---|---|---|
| `product_id` | Fareharbor product code. | 100% | Unique within Fareharbor, **not** across sources (Rule #2). | `product_id` | **KEEP** |
| `source` | Always `Fareharbor`. | 100% | 1 value. Earns its place once other sources join. | `source` | **KEEP** |
| `compound_key` | `product_id` + source. | 100% | The real primary key — already built, don't re-derive. | `compound_key` | **KEEP** — PK |
| `supplier_alias` | Operating company. | 100% | Only **138 suppliers** across 500 (3.6 products each) — which is why one operator's boilerplate can dominate a whole column. | `meta_supplier_name` | **KEEP** |

### 3b. Naming and pricing (8)

| Column | What it holds | Fill % | Key insight | Unified column | Do |
|---|---|---|---|---|---|
| `product_name` | Full tour name. | 100% | 496 distinct of 500. | `product_name` | **KEEP** |
| `product_headline` | Short tagline. | 97.0% | Capped at 100 chars. One of few Figma listing fields with near-full coverage. | `product_headline` | **KEEP** |
| `price` | Starting price, ex-tax. | 100% | Always present. | — | **DELETE** — Decision F: ex-tax dropped, derivable via `detail_tax_percentage` |
| `price_including_tax` | Price with tax. | 100% | Pairs with `tax_percentage`. | `product_price` | **KEEP** — Decision F: this is the one price column |
| `tax_percentage` | 10 / 15 / 0. | 100% | Tracks country: 10 = AU GST, 15 = NZ GST, 0 = 41 tax-free products. | `detail_tax_percentage` | **KEEP** |
| `currency` | AUD or NZD. | 100% | 379 AUD / 121 NZD. **The set is not Australia-only** — 24% is NZ. | `product_currency` | **KEEP** |
| `price_options_summary` | The fare table. | 100% | 417 distinct, up to 913 chars. Richest pricing field; Figma's "from $X" doesn't show it. | `product_price_options` | **KEEP** |
| `prototype_count` | Bookable variants. | 100% | Median 1, up to 22. **This detects the 478478 multi-variant problem** — high count means one flat row may not represent the product. | `meta_variant_count` | **INTERNAL FILE** — the safety check |

### 3c. Location (7)

| Column | What it holds | Fill % | Key insight | Unified column | Do |
|---|---|---|---|---|---|
| `location_street` | Street address. | 70.2% | Details-API-only (Rule #8) — no other source exists. | `location_street` | **KEEP** |
| `location_city` | City. | 72.4% | Best-covered location field; still 138 products with no city. | `location_city` | **KEEP** |
| `location_state` | State / region. | 70.8% | 38 distinct, unnormalised. | `location_state` | **KEEP** + normalise |
| `location_country` | AU or NZ. | 71.8% | **141 products have no country** — breaks any country filter. | `location_country` | **KEEP** |
| `location_postcode` | Postcode. | 71.0% | Read as string or pandas gives you `2000.0`. | `location_postcode` | **KEEP** |
| `location_lat` | GPS latitude. | 57.6% | Worst-covered location pair. | `location_latitude` | **KEEP** |
| `location_lng` | GPS longitude. | 57.6% | **42% of products cannot be mapped.** Figma has a map — see Gap 2. | `location_longitude` | **KEEP** |

### 3d. Media and tags (4)

| Column | What it holds | Fill % | Key insight | Unified column | Do |
|---|---|---|---|---|---|
| `images` | All image URLs. | 97.8% | 11 products have none. | `product_images` | **KEEP** |
| `main_image` | Cover image. | 99.6% | Only 2 lack one — safe for a listing card. | `product_main_image` | **KEEP** |
| `image_count` | How many. | 100% | Median 1, up to 18. A third have exactly one — the Figma gallery will look sparse. | — | **DELETE** — dev derives it from `product_images` |
| `tags` | Keywords. | 60.0% | Actually **category** data — "Water Activities" (665), "Boat Tour" (645), "Guided Tour" (357). **Not** the Figma chips. 200 products untagged. | `product_category` | **KEEP** — but see Gap 3 |

### 3e. Policy and operations, from the API (6)

| Column | What it holds | Fill % | Key insight | Unified column | Do |
|---|---|---|---|---|---|
| `cancellation_policy` | Full refund terms. | **98.0%** | Strongest field in the dataset for its concept. Rule #10 puts it above both extractions. | `detail_cancellation_policy` | **KEEP** — primary |
| `cancellation_type` | Always `hours-before-start`. | 100% | 1 distinct value. Carries no information. | — | **DELETE** — constant |
| `cancellation_hours` | Notice required. | 100% | 443 are 24h, 39 are 48h, 16 are 0h, 2 are 336h. Clean and structured — **this powers the green "Free cancellation up to 24 hours" box in Figma**. | `detail_cancellation_hours` | **KEEP** |
| `booking_notes` | **Raw booking text** the 25 booking columns come from. | 100% | Median 2,478 chars, max 10,631. The audit trail for every `redo_booking_*` value. | `meta_raw_booking_notes` | **INTERNAL FILE** — audit trail |
| `is_pickup_available` | Hotel pickup flag. | 100% | Only **19 of 500 True**. Near-constant — don't build a filter on it. | `detail_pickup_available` | **DECIDE** — keep as data, not as a filter |
| `health_safety` | Safety policy. | 9.6% | Booking extraction beats it (15.4%). | `detail_health_safety` | **FALLBACK** — behind booking |

### 3f. Legacy ETL description columns (10)

The original v2 ETL's section split, predating V5.

| Column | What it holds | Fill % | Key insight | Unified column | Do |
|---|---|---|---|---|---|
| `desc_about` | Main description text. | 100% | **The raw input** the description extraction reads. | `meta_raw_description` | **INTERNAL FILE** — audit trail |
| `desc_booking_notes` | Booking text, old split. | 100% | The catch-all that swallowed check-in instructions — V5.3 confirms it (96 check-ins recovered). | — | **DELETE** — superseded |
| `desc_cancellation` | Cancellation text. | 98.0% | Identical to `cancellation_policy` on only **114 of 500** — so they are *not* the same column despite matching fill rates. | — | **DELETE** — Decision G settled: differs by whitespace only |
| `desc_what_included` | Inclusions. | 47.6% | Fills **2× more** than V5's 24.4%. Expected: old ETL classified by meaning, V5 requires a heading. The extra 23% is the over-assignment V5 was built to stop. | — | **DELETE** |
| `desc_highlights` | Highlights. | 29.6% | vs V5's 4.2%. | — | **DELETE** |
| `desc_what_to_bring` | Packing list. | 28.0% | vs V5's 12.2%. | — | **DELETE** |
| `desc_itinerary` | Itinerary. | 21.2% | vs V5's 3.2% — widest old-vs-new gap, and why itinerary needed three prompt revisions. | — | **DELETE** |
| `desc_what_excluded` | Exclusions. | 20.4% | vs V5's 4.4%. | — | **DELETE** |
| `desc_other` | Everything else. | 31.6% | The old catch-all. | — | **DELETE** |
| `desc_extraction_method` | `direct_structured` / `direct_fallback`. | 100% | 446 / 54 — matches `has_structured_desc` exactly. One is redundant. | — | **DELETE** |

### 3g. Legacy regex/HTML parser output (20) — **DELETE ALL**

The pre-LLM pattern-matching attempt. CLAUDE.md records this approach at ~16% coverage vs the LLM's 48–76%.

| Column group | Fill % | Key insight | Do |
|---|---|---|---|
| `parsed_txt_about` | 100% | The only one that reliably fills. | **DELETE** |
| `parsed_txt_duration` | 78.0% | Median 116 chars — grabbing surrounding prose, not a clean duration. | **DELETE** |
| `parsed_txt_booking_notes`, `parsed_txt_what_to_bring` | 45–46% | Only other two above 40%. | **DELETE** |
| `parsed_txt_highlights/what_included/itinerary/other/cancellation` | 6–32% | Steadily worse than the LLM equivalents. | **DELETE** |
| `parsed_html_*` (10 columns) | 1–36% | Uniformly worse than their `_txt_` twins. | **DELETE** |
| `parsed_txt_what_excluded`, `parsed_html_what_excluded` | **0%** | **Dead — zero fills across 500.** | **DELETE** |

All 20 are superseded and are the single biggest source of confusing near-duplicate column names in the file.

### 3h. Pipeline bookkeeping (10)

| Column | What it holds | Fill % | Key insight | Unified column | Do |
|---|---|---|---|---|---|
| `duration_text` | Duration from the API. | 50.6% | Half have no API duration; extraction adds 150 more. | `product_duration` | **KEEP** — primary |
| `duration_minutes` | Duration as a number. | 24.4% | Only a quarter. **This is what powers the "1 Hour" chip and any sort-by-length** — at 24% the chip is missing three times out of four. | `product_duration_minutes` | **KEEP** — see Gap 1 |
| `has_structured_desc` | Did FH supply structure. | 100% | 446 True / 54 False. | `meta_has_structured_desc` | **INTERNAL FILE** — QA only |
| `needs_chatgpt` | Routed to AI extraction. | 100% | **382 of 500 (76%) flagged as needing it** — the number that justified the whole V5 programme. | — | **DELETE** — job done |
| `txt_sections_found` / `html_sections_found` | Regex matches. | 100% / 64.8% | Diagnostic only. | — | **DELETE** |
| `txt_sections_count` / `html_sections_count` | How many matched. | 100% | Median 4 and 1 — the HTML parser found almost nothing. | — | **DELETE** |
| `empty_sections_count` / `empty_sections_list` | Which came out empty. | 100% / 91.4% | **Only ever tracks 5 tokens** — never `other` or `duration`, so QA measured against it wrongly reads those two as out-of-scope. | — | **DELETE** |

---

## 4. The proposed unified schema — two separate tables

The dev team's table carries **no QA, audit or provenance columns**. Those exist for
the data team and go in a companion file keyed on `compound_key`.

### 4a. `fareharbor_unified.csv` — 48 columns, this is what dev receives

**Product (10):** `compound_key`, `product_id`, `source`, `product_name`,
`product_headline`, `product_price` *(tax-inclusive — Decision F)*, `product_currency`,
`product_price_options`, `product_duration`, `product_duration_minutes`

**Media & category (3):** `product_main_image`, `product_images`, `product_category`

**Location (7):** `location_street`, `location_city`, `location_state`,
`location_country`, `location_postcode`, `location_latitude`, `location_longitude`

**Detail — the Figma page (21):** `detail_description`, `detail_highlights`,
`detail_what_is_included`, `detail_what_is_not_included`, `detail_itinerary`,
`detail_important_info`, `detail_booking_notes`, `detail_meeting_point`,
`detail_check_in`, `detail_departure_info`, `detail_before_arrival`, `detail_what_to_bring`,
`detail_what_not_to_bring`, `detail_accessibility`, `detail_restrictions`,
`detail_special_requirements`, `detail_health_safety`, `detail_group_size`,
`detail_faqs`, `detail_extras`, `detail_disclaimers`

**Policy & commercial (5):** `detail_cancellation_policy`, `detail_cancellation_hours`,
`detail_tax_percentage`, `detail_pricing_notes`, `detail_pickup_available`

**Supplier (2):** `meta_supplier_name`, `detail_operator_contact`

*(`meta_supplier_name` keeps its `meta_` prefix only because that is the established
name in the existing unified database — it is customer-facing data, shown in Figma's
Operator Information block.)*

### 4b. `fareharbor_internal.csv` — 8 columns, data team only

Joined to the above on `compound_key`. **Not shipped to dev.**

| Column | Why it exists |
|---|---|
| `compound_key` | Join key. |
| `meta_raw_description` | The raw text V5.3 read. Audit trail for every `detail_*` value. |
| `meta_raw_booking_notes` | The raw text V5.4 read. Same. |
| `meta_desc_flags` | V5.3's own uncertainty notes. Defect-hunting order. |
| `meta_booking_flags` | V5.4's uncertainty notes. |
| `meta_variant_count` | Multi-variant detector — flags the 478478 class of product. |
| `meta_has_structured_desc` | Whether Fareharbor supplied structure. QA only. |
| `meta_field_sources` | One JSON blob per product: which source won each merged field, and which band it fell in (Rule #10). |

**116 → 48 for dev, + 8 internal.** *(price −1, departure_info +1 after Decisions D and F.)* The reduction is almost entirely the 30 legacy
columns (`parsed_*` ×20 and `desc_*` ×10) that V5 replaced.

**One open point:** Rule #10 requires tracking which source won. I've put that in
`meta_field_sources` on the internal side, so dev's table stays clean. If dev needs to
show "verified by operator" vs "extracted" badges, that decision has to move back into
their table — flag it if so.

---

## 5. How the merge actually works

### 5.1 Why "join both" is the wrong default

Where both sides fill the same field there are **295 collisions across the 500
products**. Graded by fuzzy similarity (the band rule already used elsewhere on this
project — ≥97 same, 80–96 reworded, <80 different):

| Band | Count | Share | What it means |
|---|---|---|---|
| **SAME** (≥97) | 113 | 38% | Same text twice. Joining prints it twice on the page. |
| **REWORDED / SUPERSET** (80–96) | 59 | 20% | Same facts, different words, or one side is the other plus a bit. |
| **DIFFERENT** (<80) | 123 | 42% | Genuinely different content. Both needed. |

**58% would produce visible duplication if concatenated.** Exact string matching
could not see this — for `what_included` it reported 0 identical pairs, yet 11 of the
34 are the same content. That is precisely the "present but REWORDED" blind spot
CLAUDE.md already warns about.

Per field, of the products where both sides fill:

| Field | Both | SAME | REWORDED | DIFFERENT |
|---|---|---|---|---|
| `important_info` | 67 | 5 | 9 | **53** |
| `restrictions` | 58 | 15 | 17 | **26** |
| `what_to_bring` | 40 | **21** | 8 | 11 |
| `what_included` | 34 | 11 | 10 | 13 |
| `meeting_point` | 26 | 12 | 6 | 8 |
| `accessibility` | 25 | **24** | 0 | 1 |
| `duration_text` | 12 | 10 | 0 | 2 |
| `extras` | 8 | **8** | 0 | 0 |
| `pricing` | 8 | 1 | 0 | 7 |
| `cancellation` | 7 | 3 | 4 | 0 |
| `itinerary` | 4 | 1 | 2 | 1 |
| `faqs` | 3 | 1 | 2 | 0 |
| `highlights` | 2 | 0 | 1 | 1 |
| `check_in` | 1 | 1 | 0 | 0 |

`important_info` is the one field where joining is almost always right (53 of 67).
`accessibility` and `extras` are the opposite — nearly every collision is the same
text, because both are dominated by one operator's boilerplate.

### 5.2 The rule

For each merged field, per product:

1. **Only one side filled** → use it. *(the majority — e.g. 203 of 243 for `what_to_bring`)*
2. **Both filled, score ≥ 97** → keep the longer one. Provably the same content.
3. **Both filled, score < 80** → keep both, joined with a blank line. Booking first
   where booking is the primary source, description first otherwise.
4. **Both filled, score 80–96** → **keep both, and flag for review.** Only 59
   products. See 5.4 for why this band cannot be automated.

### 5.3 Worked examples — `what_to_bring`

**Case 1 — SAME (score 100). Product 103731.**

```
desc    (461 chars): "Please remember the following items:
                      A packed lunch or money to buy lunch at the rec center...
                      Swimwear / Surfboard / Helmet and pads / Towel / Sunscreen..."
booking (461 chars):  identical, character for character
```
→ `detail_what_to_bring` = the 461-char text, **once**.
Joining would have printed the whole packing list twice.

**Case 2 — DIFFERENT (score 64). Product 103597.**

```
desc    (141): "Surfers need to wear a swimsuit or boardies and bring a towel and
                lots of sunscreen. Don't forget a camera to document the fun."
booking (164): "Come in your bathers or boardies and bring a towel and sunscreen.
                There are no bathrooms at this location. If you have your own
                full length wetsuit you can wear it."
```
→ `detail_what_to_bring` = both, joined:

```
Come in your bathers or boardies and bring a towel and sunscreen. There are no
bathrooms at this location. If you have your own full length wetsuit you can wear it.

Surfers need to wear a swimsuit or boardies and bring a towel and lots of sunscreen.
Don't forget a camera to document the fun you will have.
```
Overlapping on towel and sunscreen, but "no bathrooms at this location" and "bring a
camera" each exist on only one side. Dropping either loses a real fact.

### 5.4 Worked examples — `what_included`, including the case that breaks automation

**Case 3 — SAME (score 99). Product 103597.** Booking is the same paragraph plus one
extra sentence:

```
desc    (412): "All equipment is provided including surfboards suited to your
                abilities... Quality Rip Curl and Quiksilver wetsuits keep you warm
                and coloured GO Surf School rash vests identify you in the water."
booking (540): ...the same paragraph, then:
               "All our wetsuits are disinfected after use. However, due to Covid-19,
                as a precaution, we recommend you wear your own if you have one."
```
→ keep **booking** (540 chars). It contains everything desc has, plus the hygiene note.

**Case 4 — REWORDED (score 83). Product 128542, `what_to_bring`. This is why band 3
cannot be automated:**

```
desc    (207): "Drinks are always welcome as we do not have a bar on board. We prefer
                clients to bring their own small eskies and drinks. We can provide
                wine glasses..."
booking (195): "What to Bring: BYO drinks are always welcome as we do not have a bar
                on board. We prefer clients to bring their own small eskies. We
                provide wine glasses..."
```
Desc is **longer**, so a "keep the longer one" rule would pick it — and lose **"BYO"**,
which only booking states, and which changes what the traveller is being told. It also
flips "we *can* provide wine glasses" (conditional) to "we provide wine glasses"
(unconditional). Length is not a proxy for completeness.

**So the 80–96 band keeps both texts and gets flagged.** 59 products across all fields —
small enough to eyeball, and the flag lives in `meta_field_sources` on the internal
table, not in dev's.

### 5.5 What dev actually sees

For product 103597, `what_to_bring`:

| Column | Value |
|---|---|
| `detail_what_to_bring` | the joined text from Case 2 |

That's all — one clean field. The provenance (`booking+desc`, band `DIFFERENT`, score
64) sits in `meta_field_sources` in the internal file, and both original columns are
untouched in the extraction outputs.

---

## 6. Decisions — SETTLED 2026-08-13

**The governing display rule, from A and B:** *every section hides when empty.* Dev
never renders a heading with nothing under it. This is what makes thin fields safe to
ship — a field that fills 6% of the time costs nothing on the other 94%.

**A. `what_is_not_included` — its own section. ✅ SETTLED**
Keeps its own section beside What's Included, hidden when empty. Its content is *not*
folded into Important Information — the two stay separate columns so dev can place
them however the page needs.

**B. Highlights — keep the section, hide when empty. ✅ SETTLED**
No synthesised highlights. Nothing is generated from `detail_description`, so Rule #11
never comes into play here and no "generated" badge is needed.

**C. `min_age` / `max_age` — dropped. ✅ SETTLED**
The numeric fields do not exist in the unified schema. Age information lives in
`detail_restrictions` as prose, which is where the extraction puts it. CLAUDE.md lists
both as Figma fields — that mapping is now formally retired for Fareharbor.

**D. `departure_info` — kept separate. ✅ SETTLED**
`detail_departure_info` is its own column, not merged into `detail_meeting_point`.
Reason: departure info can be long, and the Meeting Point block on the first screen
can't carry it. Dev decides whether to show them together. *(This reverses my earlier
MERGE recommendation.)*

**E. `detail_operator_contact` — ship the blob. ✅ SETTLED**
One text field, as extracted. No parsing into `meta_supplier_phone` / `_email` /
`_website` for now. Figma's four labelled rows will need dev to split it, or the design
adjusts to a single contact block.

**F. One price column. ✅ SETTLED**
`product_price` = the **tax-inclusive** figure (Fareharbor's `price_including_tax`).
The ex-tax column is dropped. Reason: it's what the traveller actually pays and matches
Figma's "From AUD 99.00 per person". **Nothing is lost** — `detail_tax_percentage` is
still in the schema, so an agent or the API can back out the ex-tax figure exactly
(590.00 ÷ 1.10). Reversible in one line if agents turn out to want ex-tax.

**G. `desc_cancellation` — DELETE confirmed, and my concern was wrong. ✅ SETTLED**

I flagged this as needing a check. It's been checked, and there is nothing there.

386 products have both columns filled with text that isn't byte-identical. Graded by
similarity: **385 score ≥99 and the last scores 98. None differ in content at all.**
The difference is **whitespace only** — the API's `cancellation_policy` keeps blank
lines and trailing spaces, `desc_cancellation` has them stripped:

```
cancellation_policy:  "Over 14 days: 	Refund minus booking deposit"     <- tab, blank lines
desc_cancellation:    "Over 14 days: Refund minus booking deposit"       <- collapsed
```

So `desc_cancellation` is the same policy with cleaner formatting. Deleting it loses
nothing. My "it holds different text for 376 products" was an artefact of comparing
strings exactly — the same mistake that made me get the merge rule wrong in §5.

---

## 7. Three Figma gaps — all reviewed, all accepted 2026-08-13

None of these block the schema. Recorded so they aren't rediscovered later.

**Gap 1 — the chip row. ACCEPTED, build the first three only.**
Figma's chips are "1 Hour", "Circular Quay", "Wheelchair Accessible", "Complimentary
Tea & Coffee", "Live Commentary", "Instant Confirmation". The first three come from
`product_duration`, `location_city` and `detail_accessibility`. The last three have no
source field and would have to be inferred from `what_is_included` prose — classifying
by meaning, which is exactly what V5 was built to stop. **Not built.**

**Gap 2 — the map. ACCEPTED as-is, no geocoding.**
`location_latitude`/`longitude` fill 57.6%; **212 of 500 products cannot render a map.**
Investigated before accepting:

| Possible fix | Recovers | Verdict |
|---|---|---|
| Coords hiding in raw JSON, missed by the ETL | **2 products** | The data genuinely isn't in the API. Not an ETL bug. |
| Geocode from `location_street` + `location_city` | 64 products | Viable, needs an external geocoding service |
| Geocode a street address found inside `detail_meeting_point` text | 24 products | Viable — e.g. 379854 carries "146–148 Shore Street West, Cleveland QLD" |
| Geocode from city name alone | 14 products | **Rejected on principle** — a pin on a city centre when the meeting point is a wharf 8km away sends the traveller to the wrong place. A wrong pin is worse than no pin. |

Geocoding the 88 street-level cases would lift coverage to 73.8%. **Decision: not doing
it.** The map hides when coordinates are absent, same as every other empty section.
Of the 212 without a map, 81 still have usable meeting-point or address text to display;
91 have no location information at all.

*(If this is revisited, the recoverable set is street+city or a street address inside
the meeting-point text — no city-only geocoding.)*

**Gap 3 — Onboard Facilities chips. ACCEPTED, no data source exists.**
"Car Park", "Onboard Refreshments", "Restroom Facilities", "Family Friendly" have no
facilities or amenities field anywhere in the 69 API columns. `tags` is category data
("Water Activities" 665, "Boat Tour" 645, "Guided Tour" 357), not facilities. The
section needs either a new extraction field or removal from the design. **Neither is
being done now.**

---

## 8. Merge rule — SETTLED 2026-08-13

**No list-level merging. The rule in Section 5 stands unchanged, and duplicated
bullets are accepted for now.**

The question was whether list-structured fields (`what_is_included`,
`what_is_not_included`, `itinerary`, `what_to_bring`, `what_not_to_bring`,
`highlights`) should merge bullet-by-bullet instead of whole-text. Decision: **no.**

What this means in practice, using product 480934:

- `detail_what_is_included` ships as **12 bullets covering 6 real inclusions**, with
  "Access to SSI online training materials" appearing twice.
- `detail_itinerary` ships with **Day 2 and Day 3 printed twice**, word for word.

This is a known, accepted cosmetic defect, not an unknown risk. It is confined to the
six list fields, and only on products where both sides filled the same field.

**Why this is a safe place to stop:** no content is ever lost, and no code makes a
judgement about which wording is better. Everything both suppliers wrote reaches the
page. Cleaning it up later is purely additive — the line-level pass can be added
without re-deriving anything, and the analysis for it is in
`FAREHARBOR_UNIFIED_EXAMPLE_480934.md`.

**Unchanged from Section 5:** whole-text comparison still applies to every field. Where
both sides carry near-identical text (score ≥97 — 113 of the 295 collisions), one copy
is still kept. This decision only declines the *extra* bullet-level pass on top.

---

## 9. Status

Every open question is now closed. The schema is **48 columns for dev + 8 internal**,
the merge rule is fixed, and all seven design decisions and three Figma gaps are
settled and recorded above.

**Ready to build.** Per the sequence used for the other five sources, the builder is
written only after this report is confirmed — which it now is.

---

*Numbers produced by `scratchpad/build_500_column_stats.py` and `scratchpad/probe_500.py`.
Inputs: `booking_v5_4_500_output.jsonl`, `v5_3_full_output.jsonl`, `exports/fareharbor_etl_v2.csv`.*
