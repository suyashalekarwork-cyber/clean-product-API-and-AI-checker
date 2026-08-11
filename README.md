# Clean Product API & AI Checker

Snapshot of the Fareharbor field-extraction pipeline plus an AI-based accuracy
checker that audits the extraction output.

**Current prompt: `v5_3_500_run/prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt`**
(description side) and `SYSTEM_PROMPT_FH_BOOKING_V4_7.txt` (booking side).
See `v5_3_500_run/README.md` for the latest state — V5.3 on 500 products.

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
| `v5_3_500_run/` | **Latest. Prompt V5.3 — heading-gated extraction — on 500 products. 95.0% of products show no known issue; our extraction defects are 11 products (2.2%), of which 5 (1.0%) cost the customer information.** V5.3 fills a section ONLY when the supplier wrote a heading for it, replacing the meaning-based classification that put 89.4% of a failure sample under the wrong heading. Contains the priority matrix, the full per-product audit, and the finding that most defects do not reproduce between runs. |

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
