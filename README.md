# Clean Product API & AI Checker

Snapshot of the Fareharbor field-extraction pipeline (V4.4 prompt, 500-product
run) plus an AI-based accuracy checker that audits the extraction output.

## What's here

| Folder | Contents |
|---|---|
| `prompts/` | The V4.4 extraction prompt (`fareharbor_prompts_v4_4.txt`) — the exact system prompt used to split raw supplier text into 28 named fields. |
| `extraction/` | The scripts that ran the 500-product extraction: select candidates → build batch → run batch → screen for missing content → fix → rescreen → build workbook. See `v500_summary.md` for the run's own report (cost, coverage, failure counts). |
| `dataset/` | `v500_post_fix_state.json` — the 500 products' final extracted fields plus the raw source text per product. `v500_output.jsonl` — the raw Batch API replies. |
| `checker/` | The AI accuracy checker: for every non-empty extracted field, asks an LLM judge whether that content actually belongs under that field name (placement accuracy only — not a completeness or hallucination check). |
| `results/` | `judge_accuracy_v500.xlsx` — the checker's output on the 500-product dataset, with human-review triage bands. `v500_products.xlsx` — the extraction run's own summary workbook. |
| `model_selection/` | Which *model* should run the extraction? 13 models on 10 identical products, V4.4 unchanged, plus an LLM judge and human review. Consolidated in `model_selection/MODEL_DECISION_REPORT.md`. **Superseded by `hard30_run/`.** |
| `hard30_run/` | **The current decision: `gpt-5.6-luna` ($49 for all 23,034 products).** 3 models on 30 hard-selected products using a new prompt version (V4.7), raw output only, with 38 hand-written review verdicts. Also records what V4.7 fixed, what it did not, and concrete suggested wording for the next prompt version. **Start here.** |

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
