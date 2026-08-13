# One product, end to end — product 480934

*Built 2026-08-13. Real values, produced by actually running the merge rule from
`FAREHARBOR_500_COLUMN_INVENTORY.md` §5. Nothing here is hand-written.*

**"Learn to Dive: SSI Open Water Diver"** — Gold Coast Dive Centre.
Chosen because it is the richest product in the 500: **37 of 42 columns filled**,
and **4 fields where description and booking both fired**, so it exercises the merge.

---

## The row dev would receive

| Unified column | Value | Came from |
|---|---|---|
| `compound_key` | `480934\|Fareharbor` | api |
| `product_id` | `480934` | api |
| `source` | `Fareharbor` | api |
| `product_name` | Learn to Dive: SSI Open Water Diver | api |
| `product_headline` | *(empty)* | — |
| `product_price` | `540.91` | api |
| `product_price_incl_tax` | `595.0` | api |
| `product_currency` | `AUD` | api |
| `product_price_options` | SSI Student: $540.91 | api |
| `product_duration` | Duration: 3 Days (Friday–Sunday typical schedule) | **desc** — API had none |
| `product_duration_minutes` | *(empty)* | — |
| `product_main_image` | `cdn.filestackcontent.com/i87Tcy…` | api |
| `product_images` | 2 URLs | api |
| `product_category` | Water Activities | api |
| `location_street` | 54 Paradise Avenue | api |
| `location_city` | Miami | api |
| `location_state` | Queensland | api |
| `location_country` | AU | api |
| `location_postcode` | 4220 | api |
| `location_latitude` | -28.064749 | api |
| `location_longitude` | 153.433683 | api |
| `detail_description` | "SSI Open Water Diver: start scuba diving now! Become a certified scuba diver and unlock a lifetime of underwater adventure…" | desc |
| `detail_highlights` | *(empty)* | — |
| `detail_what_is_included` | see below | **desc + booking** |
| `detail_what_is_not_included` | *(empty)* | — |
| `detail_itinerary` | see below | **desc + booking** |
| `detail_important_info` | "This course runs with a minimum of 4 students — you can book individually. Semi-Private (2 students): $840 pp…" | desc |
| `detail_booking_notes` | "Here's your discount code for a free double dive at Cook Island…" | booking |
| `detail_meeting_point` | see below | **desc + booking** |
| `detail_check_in` | "Arrive at your check-in time (e.g. 6:45 AM if stated). We open at check-in time…" | booking |
| `detail_before_arrival` | "Download the free MySSI app… Enter your full details, including your address. Upload a clear profile photo." | booking |
| `detail_what_to_bring` | "Swimwear, towel, and water bottle / Sunscreen, hat, sunglasses / Your own scuba gear (if you have it) / Snacks" | booking |
| `detail_what_not_to_bring` | *(empty)* | — |
| `detail_accessibility` | *(empty)* | — |
| `detail_restrictions` | see below | **desc + booking** |
| `detail_special_requirements` | "If you answer Yes to any question on the medical form, you must provide medical clearance from a diving doctor…" | booking |
| `detail_health_safety` | *(empty)* | — |
| `detail_group_size` | *(empty)* | — |
| `detail_faqs` | "Q: Questions? A: We're here to help…" | booking |
| `detail_extras` | *(empty)* | — |
| `detail_disclaimers` | "Gold Coast Dive Centre is not responsible for any personal items brought to the premises…" | booking |
| `detail_cancellation_policy` | "Dive courses require reserved instructor time… Course fees are non-refundable once booked…" | **api** (beats both extractions, Rule #10) |
| `detail_cancellation_hours` | `24.0` | api |
| `detail_tax_percentage` | `10` | api |
| `detail_pricing_notes` | *(empty)* | — |
| `detail_pickup_available` | `False` | api |
| `meta_supplier_name` | goldcoastdivecentre | api |
| `detail_operator_contact` | *(empty)* | — |

**Where the content came from:** 23 fields from the API, 3 description-only,
10 booking-only, 4 merged, 5 empty. Booking notes contributed more than three times
what the description did on the detail fields — consistent with the 500-product picture.

---

## The 4 merges in full

### 1. `detail_restrictions` — score 47, DIFFERENT → keep both ✅

```
To meet course requirements, you'll need to demonstrate basic swimming ability:
200m swim (no time limit, any stroke)
10-minute survival float

Be at least 10 years old
Be able to swim 200m and float for 10 minutes
If you're over 45 or have any pre-existing medical conditions, you'll need an
AS4005.1 dive medical (valid for one year)
Students younger than 15 will be certified as a Junior Open Water Diver.
```

Working exactly as intended. The description gives the swim test; booking adds the
**minimum age of 10**, the **dive medical requirement over 45**, and the **Junior
certification rule for under-15s**. Three facts a travel agent needs that the
description never mentions. Picking one side would have lost them.

### 2. `detail_meeting_point` — score 64, DIFFERENT → keep both ✅

```
Gold Coast Dive Centre
2/54–56 Paradise Ave, Miami QLD
We have limited 2-hour customer parking onsite.
Free all-day street parking is available on Paradise Ave.
Due to light rail construction and ongoing roadworks on the Gold Coast Highway,
parking may be limited on busy days. We recommend allowing some extra time.

Location: Gold and Tweed Coast
```

Booking gives the actual address and the parking situation; description only gives the
region. Correct to keep both, though the trailing "Location: Gold and Tweed Coast" adds
little — a display could reasonably show only the first block.

### 3. `detail_itinerary` — score 83, REWORDED → flagged ⚠️

```
Before Day 1 | Complete 5–6 hours of online learning.
Day 1 | Classroom review, final exam, and pool session
Day 2 | Two Open Water Dives (max depth 12 metres)
Day 3 | Two Open Water Dives (max depth 18 metres)

Day 1 | Approx 6:45 AM - 4:30 PM (Full day)
Day 2 | Two Open Water Dives (max depth 12 metres)
Day 3 | Two Open Water Dives (max depth 18 metres)
```

**Day 2 and Day 3 are printed twice, word for word.** Only Day 1 differs — description
says what happens, booking says the times. This is the flagged band doing its job by
catching it, but the output is still wrong to ship.

### 4. `detail_what_is_included` — score 79, DIFFERENT → keep both ❌

```
Access to SSI online training materials
3 days training with an SSI Instructor
Pool training before open water dives
4 open water dives
All required scuba gear
Internationally recognized SSI digital certification

Access to SSI online training materials          <- duplicate
SSI Professional Instructor                      <- same fact, reworded
Full day of pool training                        <- same fact, reworded
Four Open Water Dives around the Gold Coast & Tweed Coast   <- adds the location
All required scuba gear (if needed)              <- duplicate + a qualifier
Globally recognised SSI certification card       <- same fact, reworded
```

**This one is a genuine miss.** Score 79 fell one point below the 80 threshold, so it
was treated as "different" and both lists were kept — but they're the same six
inclusions written twice. A traveller would see a 12-item list where 6 items are real.

---

## What this example changes about the rule

The two failures above are both **bullet lists**, and both failed the same way:
whole-text similarity scoring is the wrong tool for a list.

Two lists that share four bullets and reword two will score in the 70s–80s — too low
to be "the same", too high to be genuinely different — while the *right* answer is
neither "keep one" nor "keep both", but **merge line by line**: keep every distinct
bullet, drop exact-duplicate bullets, and flag near-duplicate bullets.

This is already the pattern the project uses elsewhere — CLAUDE.md records that line
tests apply to `itinerary` and `what_included` specifically, while prose fields move as
a block. The merge rule needs the same split:

| Field type | Fields | Merge method |
|---|---|---|
| **List-structured** | `what_is_included`, `what_is_not_included`, `itinerary`, `what_to_bring`, `what_not_to_bring`, `highlights` | Line-by-line. Exact-duplicate lines dropped, near-duplicates flagged. |
| **Prose** | everything else | Whole-text, three bands as in §5. |

Applied to the two cases above, that gives:

- **`itinerary`** → 5 lines instead of 7. Day 2 and Day 3 appear once; Day 1 keeps both
  the activity and the time.
- **`what_is_included`** → 6 lines instead of 12, keeping the more specific wording of
  each ("Four Open Water Dives around the Gold Coast & Tweed Coast" over "4 open water
  dives") and the "(if needed)" qualifier on the gear.

**One caution.** Choosing which wording of a near-duplicate bullet to keep is a
judgement about meaning, and that's the decision CLAUDE.md's F2 blocker warns about —
made in code where nobody can see it. Safer version: keep the longer of two duplicate
bullets, and record the dropped one in the internal file so it stays recoverable.

---

## What I'd want your decision on

1. **Split prose vs list merging?** My recommendation is yes — this product alone
   produced two bad outputs without it.
2. **Line-level dedup drops text.** The originals are untouched either way, but the
   unified column would no longer contain everything both sides said. Acceptable?
3. **`detail_important_info` here came from the description only** even though the
   booking side is usually stronger. Nothing to fix — booking just had nothing under
   that heading for this product. Worth knowing the field flips source per product.

---

*Produced by `scratchpad/build_one_example.py`; full row in `scratchpad/example_row.json`.*
