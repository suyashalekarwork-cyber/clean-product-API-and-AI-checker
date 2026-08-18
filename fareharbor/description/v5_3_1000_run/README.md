# Description — V5.3 on 1,000 random products

The representative run. Every earlier set was chosen for difficulty; this one is
a uniform random draw, so it shows what the catalogue actually looks like rather
than its worst corner.

---

## Check these two first

| File | What it is |
|---|---|
| **`reports/v5_3_random1000_audit.txt`** | The full per-product audit — 3.2 MB, 1,000 products, findings first. **Start here.** |
| **`prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt`** | The prompt that produced it. Read this to judge whether an output is a defect or the rules working. |

There is no workbook for this run — the txt is the deliverable.

---

## Why a random sample

Every prior set — the 50, the 100, the 500 — was ordered hardest-first: flagged
for review, then lowest coverage, then longest input. That is the right way to
hunt for defects, but it means every rate quoted from those runs comes from the
worst products in the catalogue.

These 1,000 are a uniform random draw from the 10,570 products the 500-run never
touched, seeded so the selection is reproducible. **The gap between this run and
the hardest-500 is the honest error bar for a full-catalogue run.**

## Results

| | |
|---|---|
| Products | 1,000 |
| Mean retention | **99.17%** |
| Products at 100% retention | **977** |
| Products with no known defect | **97.5%** |

Hand verdicts on the 34 products the detectors flagged:

| Verdict | Count |
|---|---|
| Supplier's own data problem | 13 |
| Content loss | 7 |
| Overturned — flagged but correct | 9 |
| Misclassification | 3 |
| Label loss | 2 |

### What the two sample types show

| | Hardest 500 | Random 1,000 |
|---|---|---|
| Our defects | 2.6% | **1.2%** |

Same prompt, roughly **2× apart**. Every figure quoted before this run came from
a difficulty-selected set, so those are the pessimistic end, not the typical case.

## What the hand audit found

**Content loss is the one class that does not shrink with easier products** —
0.6% on the hardest set, 0.7% here. That is the evidence that it cannot be fixed
by prompt wording: re-running identical products on an identical prompt made 4 of
6 defects vanish. It needs a deterministic post-extraction check, which is what
the `recovered_content` pass in `fareharbor/booking/booking_v5_3_run/` does.

**Difficulty ratings wrongly fill `restrictions`** — `Difficulty: Hard`,
`Level: Moderate`. Confirmed in both the 500 and the 1,000, so unlike most
defects this one **is** reproducible and is a two-line prompt fix.

**Method note, stated in the report itself:** 1,000 products cannot be read line
by line. Every defect class found in the 100-product hand audit was turned into a
detector, checked back against those 100 where the answers are known, then run
over all 1,000. Every flagged product was then opened and read against its raw
text. So the flagged products are hand-verified; the rest mean "none of the known
defect classes fired", which is weaker than "read and confirmed correct".

---

## Files

| File | What it is |
|---|---|
| `reports/v5_3_random1000_audit.txt` | The audit — per product: verdict, comment, retention, raw description, every filled column |
| `prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt` | The extraction prompt |
| `input/random1000_products.json` | Which 1,000 products, the seed, and the rule that selected them |
| `scripts/select_1000_random.py` | The selection — uniform random, seed 42, excluding the 500 already run |
| `scripts/build_v5_3_random1000_batch.py` · `run_v5_3_random1000_batch.py` | Build and run the batch |
| `scripts/score_v5_3.py` | Retention, duplication, invention and the V5.3 rule checks |
| `scripts/detect_v5_3_issues.py` | The defect-class detectors, derived from the 100-product hand audit |
| `scripts/audit_v5_3_random1000_comments.py` | The hand-written verdict per flagged product |
| `scripts/build_v5_3_random1000_txt.py` | Builds the audit txt |

**Not shipped: the raw source data and the Batch API output.** Too large — the
28 KB system prompt repeats on every request. **Ask Huadong for the data as a
zip.**

See `fareharbor/description/v5_3_500_run/` for the hardest-500 run and its priority matrix.
