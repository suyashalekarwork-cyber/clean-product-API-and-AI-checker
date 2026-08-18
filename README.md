# Clean Product API & AI Checker

Snapshot of the supplier field-extraction pipeline plus an AI-based accuracy
checker that audits the extraction output.

Everything is filed under the **supplier** it belongs to, then the **stage** of
the pipeline it belongs to:

```
fareharbor/          the supplier this work started on
  model-choice/      which model should run the extraction
  description/       extracting the description side
  booking/           extracting the booking-notes side
  checker/           the independent AI checker over the output
  unified/           both extractions joined into one table
rezdy/               the second supplier, same rule applied
  description/       extracting the description side
```

**Current prompts:**
`fareharbor/description/v5_3_1000_run/prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt`
(description side) and
`fareharbor/booking/booking_v5_4_1000_run/prompts/SYSTEM_PROMPT_FH_BOOKING_V5_4.txt`
(booking side).

**Both sides are heading-gated** — a field fills only when the supplier wrote a
heading naming it. No heading, no fill. An empty field is a correct answer.

**Where to start:** `fareharbor/description/v5_3_full_run/` — the whole
catalogue, all 11,069 products, 99.37% retention ·
`fareharbor/booking/booking_v5_4_1000_run/` for the booking side, the first
booking run that is representative rather than difficulty-selected ·
`fareharbor/checker/checker_v1_run/` for the independent AI checker that audits
the output against the supplier's original ·
`rezdy/description/rezdy_desc_100_run/` for the same rule applied to a second
supplier.

---

## fareharbor/model-choice/ — picking the model

| Folder | Contents |
|---|---|
| `model_selection/` | Which *model* should run the extraction? 13 models on 10 identical products, prompt V4.4 unchanged, plus an LLM judge and human review. Consolidated in `MODEL_DECISION_REPORT.md`. **Superseded by `hard30_run/`.** |
| `hard30_run/` | How `gpt-5.6-luna` was chosen: 3 models on 30 hard-selected products using prompt V4.7, raw output only, with 38 hand-written review verdicts. Also records what V4.7 fixed, what it did not, and suggested wording for the next prompt version. |

## fareharbor/description/ — the description side

Runs are listed oldest first, so the table reads as the actual sequence of work.

| Folder | Contents |
|---|---|
| `v4_4_500_run/` | **The first run**, on 500 products with prompt V4.4 — everything it produced, in one folder. `prompts/` the V4.4 system prompt that splits raw supplier text into 28 named fields · `scripts/` select candidates → build batch → run batch → screen for missing content → fix → rescreen → build workbook (see `scripts/v500_summary.md` for cost, coverage and failure counts) · `data/` the 500 products' final fields plus their raw source text, and the raw Batch API replies · `reports/` the result workbooks · `checker/` the first placement judge, which asks an LLM whether each non-empty field's content belongs under that field name. |
| `luna50_run/` | The chosen model's first 50-product outing. |
| `luna100_run/` | **The chosen model on 100 representative products — 99.4% of supplier text kept, nothing invented.** Includes `worked_example.xlsx` (one invented product showing every column), the manager review workbook, and the heading-mapping rules. Prompt work since — Itinerary, FAQ and What's Included, four versions through V4.8.3 — is in `PROMPT_WORK.md` and `issues/SESSION_REPORT.md`. V4.8.3 in `prompts/` is the last meaning-based version, superseded by the heading gate. |
| `v5_3_500_run/` | **Prompt V5.3 — heading-gated extraction — on the 500 HARDEST products. 95.0% of products show no known issue; our extraction defects are 11 products (2.2%), of which 5 (1.0%) cost the customer information.** V5.3 fills a section ONLY when the supplier wrote a heading for it, replacing the meaning-based classification that put 89.4% of a failure sample under the wrong heading. Contains the priority matrix, the full per-product audit, the two-phase delivery plan, and the finding that most defects do not reproduce between runs. |
| `v5_3_1000_run/` | **The representative description run — V5.3 on 1,000 RANDOM products. 99.17% retention, 977 of 1,000 products at 100%, 97.5% with no known defect.** Every earlier set was ordered hardest-first, so every rate quoted before this one came from the worst corner of the catalogue. Our defects here are 1.2% against 2.6% on the hardest-500 — roughly 2× apart, same prompt. The gap between the two is the honest error bar for a full-catalogue run. |
| `v5_3_full_run/` | **The FULL catalogue — V5.3 on all 11,069 products with a description. 99.37% content retention, 10,853 products at 100%, 8,450 (76.3%) with no finding at all.** Not a sample. Two flags were sampled and verified before publishing (~90% of each is real); the rest are marked as upper bounds. Also records the two things that went wrong on the way: the org's 40M enqueued-token cap rejecting two of four chunks, and a runner bug that reported a failed batch as done. |

## fareharbor/booking/ — the booking-notes side

| Folder | Contents |
|---|---|
| `booking_v5_3_run/` | **V5.3 on 100 products — the first booking output anyone has ever read.** The QA screener had discarded the booking half of every previous run. 15 columns → 25, derived from a census of all 8,244 products with booking notes (17,212 headings, 3,729 distinct wordings). URL loss dropped from 72 to 6; text copied out of the prompt's own examples from 1 product to 0. Includes the two report-only passes that record what extraction missed **and which heading it belonged under**. **Note: 100 products, where the description runs are 500 and 1,000 — thinner evidence.** |
| `booking_v5_4_1000_run/` | **The booking side at catalogue scale — V5.4 on 1,000 RANDOM products, and the first booking run that is representative.** Every earlier booking set was chosen for difficulty, so every booking rate published before this one was the pessimistic end. **83.7% of products have nothing flagged, against 65.2% on the hardest-500. Zero invented text in 1,000 products. Duplication — the gate that failed three prompt versions — drops from 9.4% to 0.4%.** Mean retention reads *lower* (96.5% vs 97.9%) purely because random products are short: 85.4% are at 100%. V5.4's one change from V5.3 is that image markdown keeps its URLs. |

## fareharbor/checker/ — auditing the output

| Folder | Contents |
|---|---|
| `checker_v1_run/` | **The independent AI checker.** Reads the supplier's original next to all 22 extracted boxes — including the empty ones — and reports four fault types, each labelled ours or the supplier's. A second marker then argues each fault down; only survivors count, which cuts false alarms from ~42% to 4%. Scoring is plain code, not the model. It had to pass 73 human-judged products before being trusted, and found **42** label-loss faults in 1,000 tours where the old method found **2**. |

The earlier, narrower judge — placement accuracy only — lives with the run it
scored, at `fareharbor/description/v4_4_500_run/checker/`.

## fareharbor/unified/ — joining it together

| Folder | Contents |
|---|---|
| `fareharbor_unified_500/` | **The unified table — the API's own fields plus BOTH extractions in one row per product, 500 products, 48 columns.** The first time the three inputs have been combined. Key finding: the description and booking extractions are not duplicates — booking finds packing lists 222 times against 61, check-in 96 against 9, FAQs 66 against 3. Includes the full column-by-column design document, ten random products laid out for manual checking, and one product traced end to end. |

## rezdy/description/ — the same rule on a second supplier

| Folder | Contents |
|---|---|
| `rezdy_desc_100_run/` | **The first heading-gated run on Rezdy — 100 products, the hardest in the catalogue, read by hand.** Rezdy's fields were previously filled by guessing what the text was about: of 329 sampled failures, 294 (89%) were text filed under the *wrong* field, not missing. Applying the heading gate takes supplier words kept from **71.8% to 98.6%**, with 98 of 100 products at ≥95% and fields available going from 9 to 21. The headline finding is that the old method was silently dropping more than a quarter of every supplier's text and nothing in its output showed it. Structurally clean: 100/100 parsed, 0 truncated, 0 wrong key sets, 0 prompt contamination. |

---

## Headline numbers from the first run (500 products, 4,133 fields checked)

These come from `fareharbor/description/v4_4_500_run/` and are kept for
comparison — they are the **starting point**, not the current state.

- **Placement accuracy: 77.5%** (3,203 correct / 923 wrong-field / 7 garbled)
- **Review bands:** 281 products (56%) need no human review, 97 (19%) worth a
  spot-check, 122 (24%) flagged for review — see
  `fareharbor/description/v4_4_500_run/reports/judge_accuracy_v500.xlsx`,
  sheet `Review_Bands` / `Needs_Human`.
- Biggest recurring defect: timing text ("15 minutes before departure") is
  frequently misfiled into check-in fields (arrival *actions*), not the
  departure-timing field it belongs in.

## Running it yourself

These scripts are copied out of a larger internal pipeline and reference
relative paths (`../data/Fareharbor/*.json` raw supplier JSON, a shared
`config/fareharbor_prompts.txt`) that exist in that pipeline's own repo, not
this one. This repo is a **snapshot for review**, not a standalone runnable
project — rewire `PROJECT_ROOT`/`RAW_DIR`/`PROMPT_PATH` in each script to your
own layout if you want to re-execute a step.

To run the first-run placement checker against the included dataset:

```bash
cp .env.example .env   # then fill in your real OPENAI_API_KEY
cd fareharbor/description/v4_4_500_run
python checker/build_judge_batches.py   # needs the V4.4-derived JUDGE_V1 prompt
python checker/run_judge_batches.py
python checker/score_judge_verdicts.py
```

Note: `build_judge_batches.py` reads the judge prompt from
`config/fareharbor_prompts.txt` in the original repo (not included here in
full — only the V4.4 extraction prompt is under
`fareharbor/description/v4_4_500_run/prompts/`). To run standalone, port the
`SYSTEM_PROMPT_FH_JUDGE_V1` block into a local prompt file and update
`PROMPT_PATH`.

## Scope of that first checker

It judges **placement only** — does each field's text belong under that field
name? It does **not** check whether extracted text was invented (vs. faithful to
the raw source) and does **not** check for content dropped entirely during
extraction. Read `placement_accuracy_pct` as exactly that, not as an overall
extraction-quality score. The later checker in `fareharbor/checker/` is the one
that covers content loss and label loss.
