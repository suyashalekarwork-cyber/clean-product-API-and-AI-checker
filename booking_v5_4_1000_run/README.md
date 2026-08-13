# Booking notes — V5.4 on 1,000 RANDOM products

**The first booking run that is representative.** Every earlier booking set —
the 100 and the 500 — was chosen for difficulty, so every rate the booking side
has published so far is the pessimistic end of the catalogue rather than the
typical case. These 1,000 are uniform random (seed 42) from all 8,244 products
that have booking notes, excluding the 600 already run.

---

## Check these three first

| File | What it is |
|---|---|
| **`booking_v5_4_1000_audit.xlsx`** | All 1,000 products, one row each, sorted worst-first with a filter on, and a **blank verdict column** for a reviewer. **Start here.** |
| **`reports/booking_v5_4_1000_audit.txt`** | The **177 products with a finding**, raw supplier text beside the extracted columns. Deliberately not all 1,000. |
| **`booking_v5_4_1000_data.xlsx`** | The data itself — the 25 columns beside the raw, plus what post-processing recovered. Closest thing to what a downstream consumer receives. |

---

## Results

| | |
|---|---|
| Products | **1,000** |
| Responses parsed | **1,000 of 1,000** |
| Truncated | **0** |
| **Products with nothing flagged at all** | **837 (83.7%)** |
| Products at 100% content retention | **854 (85.4%)** |
| Mean content retention | **96.5%** |

## Against the hardest-500, same prompt

| | 500 hardest | **1,000 random** |
|---|---|---|
| Nothing flagged at all | 65.2% | **83.7%** |
| At 100% retention | 73.2% | **85.4%** |
| **Invented text** | 4 products | **0** |
| URLs lost | 15 (3.0%) | **5 (0.5%)** |
| Same sentence in 2 columns | 47 (9.4%) | **4 (0.4%)** |
| Text present but reworded | 68 (13.6%) | **17 (1.7%)** |
| Gate leak | 12 (2.4%) | **4 (0.4%)** |
| Whole product in one column (≥3 headings) | 3.2% | **2.1%** |

Every category fell, most of them several-fold. **Duplication — the gate that
has failed every version and resisted three prompt fixes — drops from 9.4% to
0.4%.** On ordinary products it barely happens.

**Zero invented text in 1,000 products.** The `(required)` insertion bug (RULE 9,
still unfixed) did not fire once: it needs bold-heavy formatting to trigger and
most products do not have it.

## The one number that reads worse

**Mean retention is 96.5%, BELOW the hardest-500's 97.9%.** That is arithmetic,
not a regression.

Random products are short — median **76 words** against several hundred in the
stratified sets, and median **1 heading** against 8. One dropped sentence in a
76-word product costs several percent; the same sentence in a 900-word product
costs a fraction of one.

**85.4% of products are at 100%.** The mean is pulled down by a small number of
short products, not by widespread loss. Read the *products-at-100%* figure, not
the mean.

## Why "one column" is usually correct here

530 of 1,000 products put 100% of their words in a single column. That is **not**
530 collapses:

| Headings in the raw | Products | |
|---|---|---|
| 0 | 267 | one column is the only correct answer |
| 1 | 210 | one heading, one column |
| 2 | 32 | |
| **3 or more** | **21** | **the real collapse cases — 2.1%** |

Only the last row is the outer-heading rule swallowing a product that had
structure to work with. Against 3.2% on the hardest-500.

## What changed in V5.4

One change from V5.3, 13 lines, inside RULE 8: image markdown now keeps its
URLs. `![alt](url)` and the nested `[![alt](img)](dest)` shape were previously
dropped whole. On the 500-product A/B, 25 of the 31 URLs V5.3 lost came back,
and the remaining 6 were verified as the checker's own regex fault rather than
real losses.

The rule also states that `![...]` alt text is the **supplier's** words —
`Description of image` is Fareharbor's default alt text, present 148 times in
500 products, and must not be rewritten.

## Known and not fixed

- **RULE 9 `(required)` insertions** — the prompt tells the model to append the
  literal word "(required)" wherever the raw uses bold, and it cannot tell
  emphasis from a required-marker. 3 confirmed cases in the 500; **0 here**. Fix
  identified, not applied.
- **`group_size` never fires** — 0 of 500, 0 of 1,000. Define it or drop it.
- **`478478`** (in the 500) — three tour variants differing only by departure
  time, one survived. The only finding on this project that actively misleads a
  customer.

## A failure mode worth recording

**5 of 1,000 responses returned a mangled column name** — `redo_bookingwhat_excluded`
(missing underscore) and `redo_booking_excluded`. All five were **empty**, so
nothing was lost. But had the typo landed on a filled column the content would
have disappeared silently. The key-set check caught it only because it was
looking for exactly this.

## How to read the findings

**177 products have a finding, and that is not 177 defects.** On the 100-product
run, of the flags that were read against the raw, **13 of 18 turned out to be the
detector rather than the model** — two whole categories came out 100% false.

146 of the 177 are in *text reaching no column*, historically the noisiest
category (mostly sign-offs, lead-in lines and label-joining). The genuinely
interesting rows — lost URLs, gate leaks, itinerary-test failures — are **fewer
than 20 products**.

**No LLM checker numbers appear anywhere in this run.** The booking checker
exists but fails its own accuracy gate (it accuses known-clean products and
misses label loss entirely), so its output is not used here as findings.

See `FILE_DESCRIPTIONS.md` for what every file is.
