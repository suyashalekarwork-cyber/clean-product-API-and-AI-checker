# Clean Product API & AI Checker

Snapshot of the Fareharbor field-extraction pipeline plus an AI-based accuracy
checker that audits the extraction output.

**Current prompts:**
`v5_3_1000_run/prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt` (description side) and
`booking_v5_3_run/prompts/SYSTEM_PROMPT_FH_BOOKING_V5_3.txt` (booking side).

**Both sides are now heading-gated.** The booking side moved from V4.7 straight
to V5.3 — its first heading-gated prompt, and the first time booking output has
been checked at all.

**Where to start:** `v5_3_1000_run/` for the representative description run
(1,000 random products, 99.17% retention) · `booking_v5_3_run/` for the booking
side · `checker_v1_run/` for the independent AI checker that audits the output
against the supplier's original.

Earlier versions kept for reference: V4.8.3 in `luna100_run/prompts/` (the last
meaning-based version, superseded by the heading gate) and V4.4 in `prompts/`
(the original 500-product run's version).

## What's here

| Folder | Contents |
|---|---|
| `prompts/` | The V4.4 extraction prompt (`fareharbor_prompts_v4_4.txt`) — the exact system prompt used to split raw supplier text into 28 named fields. |
| `extraction/` | The scripts that ran the 500-product extraction: select candidates → build batch → run batch → screen for missing content → fix → rescreen → build workbook. See `v500_summary.md` for the run's own report (cost, coverage, failure counts). |
| `dataset/` | `v500_post_fix_state.json` — the 500 products' final extracted fields plus the raw source text per product. `v500_output.jsonl` — the raw Batch API replies. |
| `checker/` | The AI accuracy checker: for every non-empty extracted field, asks an LLM judge whether that content actually belongs under that field name (placement accuracy only — not a completeness or hallucination check). |
| `results/` | `judge_accuracy_v500.xlsx` — the checker's output on the 500-product dataset, with human-review triage bands. `v500_products.xlsx` — the extraction run's own summary workbook. |
| `model_selection/` | Which *model* should run the extraction? 13 models on 10 identical products, V4.4 unchanged, plus an LLM judge and human review. Consolidated in `model_selection/MODEL_DECISION_REPORT.md`. **Superseded by `hard30_run/`.** |
| `hard30_run/` | How `gpt-5.6-luna` was chosen: 3 models on 30 hard-selected products using prompt V4.7, raw output only, with 38 hand-written review verdicts. Also records what V4.7 fixed, what it did not, and suggested wording for the next prompt version. |
| `luna100_run/` | **The chosen model on 100 representative products — 99.4% of supplier text kept, nothing invented.** Includes `worked_example.xlsx` (one invented product showing every column), the manager review workbook, and the heading-mapping rules. **Start here.** Prompt work since then — Itinerary, FAQ and What's Included, four versions through V4.8.3 — is in `luna100_run/PROMPT_WORK.md` and `luna100_run/issues/SESSION_REPORT.md`. |
| `v5_3_1000_run/` | **The representative description run — V5.3 on 1,000 RANDOM products. 99.17% retention, 977 of 1,000 products at 100%, 97.5% with no known defect.** Every earlier set was ordered hardest-first, so every rate quoted before this one came from the worst corner of the catalogue. Our defects here are 1.2% against 2.6% on the hardest-500 — roughly 2× apart, same prompt. The gap between the two is the honest error bar for a full-catalogue run. |
| `booking_v5_3_run/` | **The booking side — V5.3 on 100 products, and the first booking output anyone has ever read.** The QA screener had discarded the booking half of every previous run. 15 columns → 25, derived from a census of all 8,244 products with booking notes (17,212 headings, 3,729 distinct wordings). URL loss dropped from 72 to 6; text copied out of the prompt's own examples from 1 product to 0. Includes the two report-only passes that record what extraction missed **and which heading it belonged under**. **Note: 100 products, where the description runs are 500 and 1,000 — thinner evidence.** |
| `checker_v1_run/` | **The independent AI checker.** Reads the supplier's original next to all 22 extracted boxes — including the empty ones — and reports four fault types, each labelled ours or the supplier's. A second marker then argues each fault down; only survivors count, which cuts false alarms from ~42% to 4%. Scoring is plain code, not the model. It had to pass 73 human-judged products before being trusted, and found **42** label-loss faults in 1,000 tours where the old method found **2**. |
| `v5_3_500_run/` | **Prompt V5.3 — heading-gated extraction — on the 500 HARDEST products. 95.0% of products show no known issue; our extraction defects are 11 products (2.2%), of which 5 (1.0%) cost the customer information.** V5.3 fills a section ONLY when the supplier wrote a heading for it, replacing the meaning-based classification that put 89.4% of a failure sample under the wrong heading. Contains the priority matrix, the full per-product audit, the two-phase delivery plan (Phase 1 ships to the web dev team now; Phase 2 routes content line-by-line), and the finding that most defects do not reproduce between runs. |

## Headline numbers (500 products, 4,133 fields checked)

- **Placement accuracy: 77.5%** (3,203 correct / 923 wrong-field / 7 garbled)
- **Review bands:** 281 products (56%) need no human review, 97 (19%) worth a
  spot-check, 122 (24%) flagged for review — see `results/judge_accuracy_v500.xlsx`,
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

To run the checker specifically (`checker/`) against the included dataset:

```bash
cp .env.example .env   # then fill in your real OPENAI_API_KEY
python checker/build_judge_batches.py   # needs the V4.4-derived JUDGE_V1 prompt
python checker/run_judge_batches.py
python checker/score_judge_verdicts.py
```

Note: `build_judge_batches.py` reads the judge prompt from
`config/fareharbor_prompts.txt` in the original repo (not included here in
full — only the V4.4 extraction prompt is under `prompts/`). To run standalone,
port the `SYSTEM_PROMPT_FH_JUDGE_V1` block into a local prompt file and update
`PROMPT_PATH`.

## Scope of the checker

The checker judges **placement only** — does each field's text belong under
that field name? It does **not** check whether extracted text was invented
(vs. faithful to the raw source) and does **not** check for content dropped
entirely during extraction. Read `placement_accuracy_pct` as exactly that,
not as an overall extraction-quality score.
