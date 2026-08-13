# Fareharbor Unified Table — 500 products

**One row per product, carrying the API's own fields plus everything both AI
extractions produced, arranged to match the website prototype.**

This is the first time the three inputs have been put in one table. Until now the
API data, the description extraction and the booking-notes extraction lived in three
separate files with three different shapes.

| | |
|---|---|
| Products | **500** |
| Columns for the web team | **48** |
| Columns kept back for the data team | **8** |
| Description extraction | V5.3 (from the full 11,069-product catalogue run) |
| Booking extraction | V5.4 |
| API source | `fareharbor_etl_v2.csv`, 69 columns |

**Start with `reports/fareharbor_unified_sample_10.txt`** — ten random products showing
the raw supplier text first, then every unified column built from it, so any value can
be checked back to its source by eye.

---

## What's here

| Path | Contents |
|---|---|
| `data/fareharbor_unified.csv` | **The deliverable.** 500 rows × 48 columns, for the web dev team. |
| `data/fareharbor_internal.csv` | 500 rows × 8 columns — raw source text, QA flags, and per-field provenance. **Data team only, not part of the dev handover.** |
| `fareharbor_unified.xlsx` | The same 48 columns as a workbook. |
| `reports/fareharbor_unified_sample_10.txt` | Ten random products (seed 42) laid out for manual checking: raw text, then the built row. |
| `reports/FAREHARBOR_500_COLUMN_INVENTORY.md` | The design document. Every one of the 116 source columns, what it holds, how full it is, and the decision made about it. |
| `reports/FAREHARBOR_UNIFIED_EXAMPLE_480934.md` | One product traced end to end, including the two merges that came out wrong and why. |
| `scripts/build_fareharbor_unified.py` | Builds both tables from the three inputs. |
| `scripts/build_fareharbor_unified_sample.py` | Builds the ten-product check file. |
| `input/booking_v5_4_500_output.jsonl` | The booking V5.4 replies for these 500 products. |

The description input is not duplicated here — it is the full-catalogue run already in
this repo at `v5_3_full_run/input/v5_3_full_output_0*.jsonl`.

---

## The three inputs, and why they had to be combined

Each product's information arrives from three places that only partly overlap.

**The API** gives structure — id, price, images, location, cancellation policy. Reliable
but sparse on descriptive content.

**The description extraction (22 fields)** reads the supplier's marketing description.

**The booking-notes extraction (25 fields)** reads a completely different block of text
that the supplier writes for people who have already booked.

The important finding is that **the two extractions are not duplicates of each other.**
Where both fill the same field, the texts are usually different content, and the booking
side is far stronger on practical detail:

| Field | Description finds | Booking finds |
|---|---|---|
| What to bring | 61 | **222** |
| Check-in | 9 | **96** |
| FAQs | 3 | **66** |
| Meeting point | 50 | **124** |

Meeting-point data was a known gap in this project. The booking side largely closes it.

---

## How a field gets filled

Priority follows the project's existing rule — dedicated API field first, extraction
second:

1. **A real API field exists** → it wins. `cancellation_policy` is present on 98% of
   products, so the extracted cancellation text is almost never needed.
2. **Only one extraction has content** → that content is used.
3. **Both have content** → compared, then handled in three bands:

| Similarity | What happens | Count |
|---|---|---|
| ≥ 97 — same content | One copy kept (the longer) | 110 |
| 80–96 — reworded | **Both kept**, flagged for review | 55 |
| < 80 — genuinely different | **Both kept**, joined by a blank line | 123 |

Nothing is ever discarded on a judgement call. Every merge decision is recorded per
field in `data/fareharbor_internal.csv`.

**A worked example** — product 480934, restrictions. The description gives the swim
test; the booking notes add the minimum age of 10, the dive-medical requirement over 45,
and the Junior certification rule for under-15s. Three facts a travel agent needs that
the description never mentions. Keeping only one side would have lost them.

---

## Known limitations

**Duplicated bullets in list fields.** Where both sides filled a bulleted field and the
wording differs, both lists are kept — so some items appear twice. Product 480934's
What's Included ships as 12 bullets covering 6 real inclusions. This was reviewed and
**accepted deliberately**: no content is lost, and no code makes a judgement about
which wording is better. De-duplicating line-by-line can be added later without
re-deriving anything; the analysis is in
`reports/FAREHARBOR_UNIFIED_EXAMPLE_480934.md`.

**An empty column is usually correct.** Both extractions are heading-gated — a field
fills only when the supplier wrote a heading naming it. Empty means "this supplier had
no such section", not "we missed it". Every section on the page hides when its field is
empty.

**42% of products cannot show a map.** Latitude and longitude fill 57.6%. This is not an
extraction fault: of the 212 products without coordinates, only **2** have coordinates
in the raw API response. Geocoding street addresses could lift coverage to 73.8% and was
considered, then deliberately skipped for now. City-only geocoding was rejected outright
— a pin on a city centre when the meeting point is a wharf 8km away sends the traveller
to the wrong place.

**Three prototype elements have no data behind them.** The "Complimentary Tea & Coffee",
"Live Commentary" and "Instant Confirmation" chips, and the whole Onboard Facilities
block, have no source field anywhere in the 69 API columns. Building them would mean
inferring facts from prose — the exact practice the heading-gated prompts were written
to stop. Not built.

**`detail_accessibility` looks fuller than it is.** It fills 28 times, but 21 of those
are the literal string "CLICK HERE for accessibility information" — a link, not
accessibility data. The value is kept rather than stripped, and flagged in the internal
file.

**`detail_operator_contact` is one text blob**, not split into phone / email / website.
The prototype shows four labelled rows; splitting it is a later job.

---

## Reproducing

```
python scripts/build_fareharbor_unified.py         # writes both tables
python scripts/build_fareharbor_unified_sample.py  # writes the 10-product check file
```

Paths in both scripts are relative to the working project. The build checksums all
three inputs before and after and fails if any changed, asserts there are no duplicate
column headers, and asserts the output matches the 48-column specification exactly.
