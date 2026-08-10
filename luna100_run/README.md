# 100-Product Extraction Run — gpt-5.6-luna

**For review. Start with `worked_example.xlsx` to see the shape, then
`luna100_manager_review.xlsx` for the real results.**

100 Fareharbor products run through the chosen extraction model. Unlike earlier
runs, these products were **randomly sampled to match the real catalogue mix**
of short and long descriptions — so these numbers reflect normal performance,
not a stress test.

---

## Results

| Measure | Result | What it means |
|---|---|---|
| **Text kept** | **99.4%** | Almost none of the supplier's writing is lost |
| **Size ratio** | **0.939** | Wrote 94% as many words as the supplier — no padding |
| **Invented content** | **0 fields** | Nothing appears that wasn't in the source |
| **Repeated sentences** | **5** across 100 products | Same sentence in two fields; would render twice on the page |
| Fields filled | 8.4 of 28 on average | See "empty is correct" below |
| Technical failures | 0 | 166 of 166 requests returned clean |

**Cost:** $0.42 for these 100. **$49 to process all 23,034 products.**

### How this compares to the earlier hard-product run

| | This run (normal products) | Earlier run (hardest products) |
|---|---|---|
| Text kept | **99.4%** | 98.96% |
| Repeated sentences | **5** | 16 |

Earlier runs deliberately used products already flagged as problematic, which
understated normal performance. This is the honest baseline.

---

## Empty fields are correct

**8.4 of 28 fields filled on average.** That is expected, not a shortfall.

Most tours have no itinerary, no FAQ and no cancellation policy written into
their description. When the supplier never wrote one, the correct output is a
blank — an invented itinerary is worse than none.

`worked_example.xlsx` shows this directly: 15 of 28 fields are empty, and every
one of them is right.

---

## The one real problem found

**The Itinerary field is unreliable.**

36 products had an Itinerary filled in. **22 of them (61%) contain ordinary
description text** — no clock times, no numbered stops. One example filled it
with a narrative about Sydney's convict history.

The cause is in the instructions, not the model. `prompts/fareharbor_prompts_v4_7.txt`
defines the itinerary field as:

> *"Must contain time signals (e.g. "9am", "Day 1", **"then", "next",
> "first...then...finally"**)"*

Those last three are ordering *words*, not structure — and every story contains
a "then". The fix is to require a clock time or a numbered step, which is what
`fareharbor_extraction_mapping_rules.md` already specifies.

**This is a prompt change, not a model change**, and it is exactly what
`fareharbor_extraction_mapping_rules.md` specifies. Full per-product detail is
in the `Itinerary_Check` sheet.

*Found by reading products by hand. The automated checks scored all 22 as fine
— they measure whether text survived, not whether it landed in the right place.*

---

## Files

| File | What it is |
|---|---|
| **`worked_example.xlsx`** | **One invented product showing every column.** Read this first — it shows the output shape in 5 minutes |
| **`luna100_manager_review.xlsx`** | The real results. 5 sheets, 100 products |
| `Fareharbor_328656_Reference_Extraction.docx` | A **real** product hand-extracted by a person — the gold standard to measure the AI against |
| **`prompts/fareharbor_prompts_v4_7.txt`** | **The exact instructions given to the AI for this run** |
| `fareharbor_extraction_mapping_rules.md` | The rules: which supplier heading goes to which field, and why |
| `luna100_products.json` | The 100 product IDs and how they were chosen |
| `scripts/` | The full pipeline, reproducible |

### `prompts/fareharbor_prompts_v4_7.txt` — the instructions used

Two prompts: one for the description text (169 lines), one for the booking
notes (108 lines). This is what every one of the 166 requests in this run
received — **verified byte-for-byte against the submitted batch file**, not
reconstructed afterwards.

Version 4.7 is version 4.4 plus two rules, and nothing else was changed:

| Rule added | Why |
|---|---|
| **NO DUPLICATION** | Says explicitly that pulling text into a field *removes* it from the general description. Without that sentence, a model could leave a copy behind and the same paragraph would render twice on the page. |
| **NO INVENTION** | Every word must already exist in the supplier's text. Also forbids placeholder prose like *"No content found for this field"* — an empty field must be genuinely empty. |

`scripts/build_v47_prompts.py` shows exactly how V4.7 was produced from V4.4
and fails if any V4.4 line is lost, so the change is auditable rather than
described.

**These are not the same as `fareharbor_extraction_mapping_rules.md`.** The
prompt is the current working instructions; the mapping rules document is the
heading-gated design being moved toward. The itinerary problem in this run is
precisely where the two differ — see below.

### `Fareharbor_328656_Reference_Extraction.docx`

Product 328656, *"Costal Views Safari"* (~840 words), extracted **by hand**
into all 28 fields. Not model output — this is what a careful person produces,
so the AI can be measured against it rather than against opinion.

It is worth reading for the four problems it documents in the source data
itself, which no extraction rule can fix:

- **The booking notes duplicate the description.** Nine of ten booking-note
  paragraphs reappear inside the description under their own heading.
- **The two copies contradict each other.** One set of directions says two
  white fridges and a gate; the other says one fridge and a driveway. The
  supplier updated one copy and not the other. **No extraction rule can
  resolve this** — the source is simply wrong in one place.
- **A typo survives verbatim extraction.** The description says *"you should
  miss us"* where the supplier meant *"shouldn't"*. Because the rule is
  verbatim copying, the typo carries through — correctly.
- **Non-standard headings.** `##Duration:`, `##About`, `## What to bring` —
  inconsistent spacing after the hashes, which is why heading detection cannot
  be a simple exact match.

Note this product is **not** one of the 100 in this run, so the hand extraction
is independent of the model output published here.

### `luna100_manager_review.xlsx`

| Sheet | Contents |
|---|---|
| `Summary` | The numbers, in plain English, and what they do *not* prove |
| `Products` | 100 rows. Supplier's raw text in yellow, then every extracted field. Read left to right to check any product |
| `Per_Field_Fill` | How often each field gets filled, with a real example |
| `Itinerary_Check` | All 36 itineraries, marked real or questionable |
| `Needs_Attention` | The 19 products worth a second look |

`Products` and `Needs_Attention` have blank **pass/fail** and **comment**
columns for review notes.

### `worked_example.xlsx`

An **invented** product — a fictional Sydney harbour cruise. No real supplier
is involved, but the field names, headings and rules are the real ones.

It deliberately includes four cases that are easy to get wrong:

1. **Supplier headings vary.** This one wrote *"Tour Includes"* and *"What
   You'll Need"*; both map to standard fields.
2. **A fact with no heading is left alone.** The description says the cruise
   *"runs for about 3 hours"* — Duration is taken from the supplier's own field
   instead. Pulling facts out of prose is how *"be ready 10 minutes before
   departure"* ends up setting Duration to 10 minutes.
3. **Schedule is not an Itinerary.** *"Departures run Thursday to Sunday at
   5:30pm"* is when the tour runs, not what happens during it. It stays in
   About.
4. **15 of 28 fields are empty**, and every one is correct.

---

## Reproducing it

```bash
python scripts/select_100_representative.py   # pick the products
python scripts/run_luna100.py                 # build, submit, download
python scripts/screen_luna100.py              # measure
python scripts/build_luna100_workbook.py      # build the workbook
```

Like the rest of this repo, these reference paths from the larger internal
pipeline and are a **snapshot for review**, not a standalone runnable project.
`run_luna100.py` reads `OPENAI_API_KEY` from the environment; no key is stored
here.

---

## What this does and does not show

**Does:** whether the supplier's text survives extraction, whether the model
invents anything, and how often each field gets populated on a normal spread of
products.

**Does not:** whether each piece of text landed in the *right* field. The
measurements check survival, not placement. No independent AI judge was run on
these 100.

That distinction matters: the automated checks gave all 22 questionable
itineraries a clean score. Reading products by hand is what found them, and it
is the check that has repeatedly caught what the automated measures missed.

**Sample size:** 100 of 11,236 Fareharbor products.

---

## Follow-on work: prompt changes since this run

The run described above used **V4.7**. Three fields have since been reworked —
**Itinerary**, **FAQ** and **What's Included** — across four prompt versions,
each re-run on these same 100 products.

**Current prompt: [`prompts/SYSTEM_PROMPT_FH_DESC_V4_8_3.txt`](prompts/SYSTEM_PROMPT_FH_DESC_V4_8_3.txt)**
(booking side is still `SYSTEM_PROMPT_FH_BOOKING_V4_7.txt`).

- **[`issues/SESSION_REPORT.md`](issues/SESSION_REPORT.md)** — what was done, what
  improved, what is still open. Start here.
- **[`extracted/luna100_v4_8_3_extracted.xlsx`](extracted/)** — the extracted data
  itself, 100 products x 29 fields, with the raw supplier text beside each row
- [`reports/section_review.xlsx`](reports/) — the same run checked against the raw text
- [`PROMPT_WORK.md`](PROMPT_WORK.md) — the folder guide and how to run it yourself
- [`prompts/WHICH_PROMPT_TO_USE.md`](prompts/WHICH_PROMPT_TO_USE.md) — if in doubt

| Field | V4.7 (this run) | V4.8.3 (now) |
|---|---|---|
| Itinerary | 30 filled, roughly half holding the wrong content | **12** |
| FAQ | field did not exist | **new `redo_desc_faqs` field** |
| What's Included | 58 filled, 21 with no supplier heading | **41** |

The "5 repeated sentences" figure above is also revised there: the screening
script excluded cross-request duplicates by design, and the real count across
all fields is higher.
