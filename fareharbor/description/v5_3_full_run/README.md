# Description — V5.3 on the FULL catalogue

Every Fareharbor product that has a description: **11,069**. Not a sample.

---

## Check these three first

| File | What it is |
|---|---|
| **`v5_3_full_summary.md`** | The numbers, with what was verified marked as verified and what was not marked as an upper bound. **Start here.** |
| **`v5_3_full_scores.xlsx`** | All 11,069 products, one row each, sorted worst-first and filterable. Look up any product id here. |
| **`reports/v5_3_full_findings.txt`** | Per-product detail for the 2,619 products with a finding — raw description beside the extracted columns. Not all 11,069; a 35 MB file of mostly-clean products is not one anybody opens. |

---

## Results

| | |
|---|---|
| Products | **11,069** (167 have no description, skipped) |
| Responses parsed | **11,069 of 11,069** |
| Truncated | **0** |
| Wrong key count | **0** |
| **Mean content retention** | **99.37%** |
| Products at 100% retention | **10,853** (98.0%) |
| **Products with no finding at all** | **8,450** (76.3%) |

Retention is **higher at full scale** than on the random-1,000 (99.17%) or the
hardest-500. Every earlier set was difficulty-selected, so those figures are the
pessimistic end rather than the typical case.

## What was verified before publishing

Two flags were sampled (40 products each, seeded) because the equivalent
checks on the booking run turned out to be the scorer's own fault — there,
`filled with no heading` went from 245 to 0 once the heading mapper was fixed.

**Here they hold up. About 90% of each is real.**

| Flag | Count | Sampled verdict |
|---|---|---|
| filled with no heading | 3,422 across 2,372 products | **~90% real gate leaks** |
| itinerary lines without a signal | 1,929 across 241 products | **~90% real line-test failures** |

Example: product `529030` filled `cancellation` when its only headings are
`Duration`, `Ticket Prices:` and `About`. Nothing licensed that column.

**That the gate leaks more here than on the curated runs is expected.** Every
earlier sample was heading-rich by selection; the full catalogue contains
thousands of products with sparse or absent headings, and that is where a
heading gate has least to grip.

**Everything else in the findings table is NOT verified** and should be read as
an upper bound. Across this project roughly a quarter of what any detector
reports has turned out to be the detector rather than the model.

## Two problems hit during the run

**1. Enqueued token limit.** The first attempt submitted all four chunks at once
and two were rejected instantly:

```
token_limit_exceeded — Enqueued token limit reached for gpt-5.6-luna.
Limit: 40,000,000 enqueued tokens.
```

Each 3,500-product chunk is ~26M enqueued tokens, so two exceed the cap. Nothing
was charged — they failed before processing a request — but 7,000 products
silently did not run. **The runner now submits one chunk at a time.**

**2. The runner reported a failed batch as done.** It grouped
`failed`/`expired`/`cancelled` with `completed`, printed `02:done 03:done`, and
finished with "ALL DONE" while 63% of the catalogue had not run. Now a failed
batch is reported loudly with its error code, and the script re-checks recorded
batch ids rather than assuming they are live.

Both fixes are in `scripts/run_v5_3_full_batch.py`, which is resumable — it skips
chunks that already have output on disk, so a restart costs nothing.

## Known issues carried forward

- **Duplication** — the one hard gate that fails. Three prompt versions failed to
  fix this on smaller runs; it needs the deterministic post-processing pass, not
  more prompt wording.
- **Difficulty ratings** (`Difficulty: Hard`) wrongly fill `restrictions`.
  Reproducible across runs, and a two-line prompt fix.
- **Content loss does not shrink with easier products.** The
  `recovered_content` pass built for the booking side (see `booking_v5_3_run/`)
  should be applied here too — it records what was missed **and which heading it
  belonged under**, which is what makes a loss fixable rather than merely
  counted.

See `FILE_DESCRIPTIONS.md` for what every file is.
