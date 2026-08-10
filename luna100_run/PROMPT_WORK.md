# Prompt work — Itinerary, FAQ, What's Included

*Follow-on from the V4.7 run described in `README.md`. That run established the
baseline; this one reworked three fields and re-ran the same 100 products four
times to measure the effect.*

Prompt work on the description-side extraction, tested on a fixed 100-product
sample. Three fields were reworked: **Itinerary**, **FAQ**, **What's Included**.

Everything here is self-contained. Clone, add an API key, and run.

---

## Quick start

```bash
pip install openai python-dotenv pandas openpyxl

cp ../.env.example ../.env        # then put your key in it: OPENAI_API_KEY=sk-...

cd code
python run_extraction.py --build  # build the request file only — free, no API call
python run_extraction.py          # submit + wait + download   (~$0.42, 3-4 min)
python review_output.py           # check the result against the raw supplier text
```

`review_output.py` writes **`reports/section_review.xlsx`** — that is the file to
open and review.

You do not have to re-run the extraction. Four completed runs are already in
`output/`, so `python review_output.py` works immediately on the existing data.

---

## What is in each folder

### `prompts/` — the system prompts

One file per version, each extractable and runnable on its own.

| File | Lines | What it does |
|---|---|---|
| `SYSTEM_PROMPT_FH_DESC_V4_8.txt` | 180 | Itinerary: replaced "time signals" with a row-level structural test |
| `SYSTEM_PROMPT_FH_DESC_V4_8_1.txt` | 186 | Itinerary: day-wise or time-wise, extracted whole, no trimming |
| `SYSTEM_PROMPT_FH_DESC_V4_8_2.txt` | 200 | **Added the `redo_desc_faqs` field** (schema 15 → 16) + 3 itinerary fixes |
| `SYSTEM_PROMPT_FH_DESC_V4_8_3.txt` | 214 | **What's Included heading-gating** — the current version |
| `SYSTEM_PROMPT_FH_BOOKING_V4_7.txt` | 108 | Booking side. **Unchanged throughout** — held constant so description-side changes stay attributable |

Run an older one with `python run_extraction.py --version 4.8.1`.

⚠️ V4.8.2 added a 16th output field. Rolling back to V4.8.1 or earlier drops
`redo_desc_faqs` from the output.

### `issues/` — findings and decisions

| File | What is inside |
|---|---|
| **`SESSION_REPORT.md`** | **Start here.** What was done, what improved, what is still open |
| `PROMPT_VERSION_LOG.md` | Every version: what it changed, what it fixed, **what it broke**, and how to roll back |
| `ITINERARY_ISSUES.md` | Itinerary findings, plus a 16-entry decision log with the product that prompted each decision |
| `FAQ_ISSUE.md` | The FAQ block scattered across six fields, and the fix |
| `WHAT_INCLUDED_ISSUES.md` | Rules WI-R1..R6, the heading-synonym list, and what was checked |
| `SECTION_STATUS.md` | Scorecard: one row per known issue, PASS/FAIL |
| `V4_8_3_REVIEW.md` | The most recent run reviewed in detail |

The decision logs matter more than they look. Several decisions were reversed as
better counter-examples appeared, and without the log the same points were
re-argued more than once.

### `output/` — completed runs

| File | Prompt used |
|---|---|
| `luna100_v4_8_output.jsonl` | V4.8 |
| `luna100_v4_8_1_output.jsonl` | V4.8.1 |
| `luna100_v4_8_2_output.jsonl` | V4.8.2 |
| `luna100_v4_8_3_output.jsonl` | V4.8.3 — current |

Raw OpenAI Batch API output, one JSON object per line. Each line's `custom_id` is
`{product_id}|gpt-5.6-luna|{desc|booking}`. 166 requests per run — 100
descriptions plus 66 booking-notes; 34 products have no booking text.

New runs also write `batch_input_*.jsonl` and `batch_id_*.json` here. The batch id
is saved the moment a job is submitted, so an interrupted run resumes the same
job rather than paying for a second one.

### `data/` — inputs

| File | What it is |
|---|---|
| `luna100_products.json` | The 100 product ids and the expected request count |
| `luna100_screen_results.json` | Raw supplier text per product — the source of truth for every check |
| `model_compatibility_final.json` | Per-model API parameter sets |

### `code/` — two scripts

| Script | What it does |
|---|---|
| `run_extraction.py` | Builds the batch, submits it, waits, downloads the result |
| `review_output.py` | Checks a run against the raw text and writes the review workbook |

### `reports/` — generated, not committed

`review_output.py` writes `section_review.xlsx` and `SECTION_STATUS.md` here.

---

## The review workbook

`reports/section_review.xlsx`, 7 sheets:

| Sheet | |
|---|---|
| `Read_Me` | What each field means |
| `Summary` | Counts, parse failures, checks passing |
| **`Checks`** | **14 known issues, each PASS/FAIL with the failing product ids** |
| `Itinerary` · `FAQ` · `Whats_Included` | Per product: extracted value, **raw source in the same row**, verdict |
| `All_Products` | Source-word retention and any invented words, all 100 |

Rows with an issue sort to the top. Every section sheet has blank **YOUR VERDICT**
and **YOUR COMMENT** columns.

**The raw text sits in the row on purpose.** Every finding in this work was
checked against the supplier's own text, and several early findings were wrong
until that check was applied.

---

## What the three fields mean

**Itinerary** — a day-wise or time-wise plan of what happens during the
experience, extracted whole. An activity list with no day and no time marker is
Highlights, not an itinerary. A list of departure times for the same service is a
timetable, not a route.

**FAQ** — questions with their answers, kept together in source order. A question
is never routed to another field by topic.

**What's Included** — filled only when the supplier gave a heading announcing
inclusions, counting synonyms (`provided`, `we supply`, `Buffet Includes:`,
`##Package Inclusions:`) and a sentence ending in a colon that introduces a list.
Conditional availability — *"we can supply X if you do not have your own"* — is
not an inclusion.

---

## Results

| Field | Before | Now |
|---|---|---|
| Itinerary | 30 filled, roughly half holding the wrong content | **12** |
| FAQ | field did not exist | **new field, 2 products** |
| What's Included | 58 filled, 21 inferred with no supplier heading | **41** |

**No content was deleted in any change.** Every value removed from a field was
verified present elsewhere in the output. **Zero invented content** across all
four runs, and zero technical failures in 664 requests.

**11 of 14 checks currently pass.** The three failures are known and listed in
`SESSION_REPORT.md`.

---

## Known issues

**Needs a prompt change — 3 products**

- `382277` — airport parking instructions still extracted as a tour itinerary
- `252851` — What's Included filled with no supplier heading
- `675102` — itinerary rows read `cellar door 1, 2, 3, 4`, a placeholder list

**Needs code, not wording**

- The same sentence stored in two fields, so a page prints it twice — **26
  products**. Three prompt versions have tried and failed; the rule exists and is
  being ignored. This is now the largest quality problem on the description side.
- The same itinerary in both the description and booking sections, sometimes in
  opposite order — 5 products.
- The model intermittently closes its JSON with a stray `,"` before the brace —
  1–2 products per run, different ones each time. `review_output.py` repairs this
  on load and reports which products were affected. Left unrepaired, those
  products vanish from every report without warning.

**Not yet reviewed:** Highlights · What's NOT Included · Cancellation policy ·
Check-in and meeting point · Duration, age and group size · the booking-notes
side.

---

## Method

Each change followed the same loop: agree what the field means, change **one**
field, re-run the same 100 products, check the output against the **raw supplier
text** — not against the previous run.

That last point matters. A prompt version can look like an improvement purely
because the earlier one was worse, and the earlier one was often measurably wrong.

Three checks run every time:

1. **Nothing deleted** — text removed from one field must appear in another
2. **Nothing invented** — every word must trace back to the raw source
3. **Untouched fields must not move** — changing one field's definition should
   leave the others alone

The third check earned its place: changing one field's wording has twice shifted
behaviour in a field that was not edited.

Each `build_*.py` in the main project also asserts that nothing outside the
intended edit changed, and refuses to write the new prompt otherwise.
