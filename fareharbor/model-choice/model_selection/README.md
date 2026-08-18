# Model Selection — Which Model Should Run the Extraction?

The rest of this repo measures how well **gpt-4o-mini** extracts with the V4.4
prompt: 77.5% placement accuracy over 500 products. This folder asks a
different question — **is gpt-4o-mini the right model at all?**

13 models, 10 identical products, V4.4 prompt unchanged, so the model is the
only variable. Two independent measurements:

1. **Content survival** — did the supplier's words reach the output?
2. **Placement** — did they land in the *right field*?

They turn out to be nearly uncorrelated, and only the second decides whether
the data is usable.

---

> ### ⚠️ CONCLUSION REVISED — read `MODEL_DECISION_REPORT.md` first
>
> This folder recommends **gpt-5.4-nano**. That has since changed.
>
> A third measurement — **human review** — found gpt-5.4-nano emits **1.32x the
> source words on 8 of 10 products**, inventing and duplicating content rather
> than losing it. Coverage cannot detect this: a word counted twice still counts
> as present, so duplication *raises* the coverage score.
>
> An LLM judge was also run (`judge_top4.xlsx`) and ranked gpt-5.4-nano **last**
> of four on placement — though its absolute scores are unreliable, because it
> grades against its own notion of correct placement rather than V4.4's label
> map, penalising models for obeying the prompt.
>
> **Current recommendation: `gpt-5.6-terra` ($487)**, or gpt-5.4-nano ($50)
> behind a de-duplication pass. `MODEL_DECISION_REPORT.md` consolidates all
> three evidence sources and is the authoritative version.
>
> Everything below remains accurate **as a content-survival measurement** and is
> kept for the audit trail.

---

## Result

**gpt-5.4-nano.** Best on both measurements, $50 for all 23,034 products.

| Model | Coverage | MISSING | Placement HIGH / MED | Cost 23,034 |
|---|---|---|---|---|
| **gpt-5.4-nano** | **99.75%** | **0** | **1 / 4** | **$50** |
| gpt-5.5-pro | 99.24% | 1 | 4 / 19 | $7,309 |
| gpt-5-mini | 99.16% | 1 | 1 / 17 | $75 |
| gpt-5.6-terra | 99.13% | 1 | 3 / 18 | $487 |
| gpt-4o-mini *(current)* | 89.38% | 26 | 2 / 8 | $28 |

Nine further models were tested — full ranking in `best_model_13_summary.md`.

**Against the incumbent:** +10.4 coverage points, 26 missing units → 0, for
**$22 more** across the entire catalogue. Strictly better on both axes.

**gpt-5.4-nano beats gpt-5.5-pro at 1/146th the cost** — including on
placement, where gpt-5.5-pro ranks *last* of the five audited despite ranking
2nd on coverage. A model can preserve every word and still file half of them
wrong.

---

## Why coverage alone is not enough

Product 451390: every model scored 99–100% coverage. Two of them filed
**"a COMPLIMENTARY shuttle bus"** under `redo_desc_what_excluded` — *"what is
NOT included"*. The words all survived, so coverage saw nothing wrong, while
the output told the customer the opposite of what the supplier wrote.

That is the same class of defect this repo's `checker/` measures at scale
(923 wrong-field vs only 7 garbled across 500 products): **content is rarely
lost — it is misfiled.**

`enchanted_forest_field_mapping.txt` walks that product through field by field.

---

## Files

| File | What it is |
|---|---|
| `best_model_13_summary.md` | Full 13-model ranking, cost, reliability, recommendation |
| `best_model_13.xlsx` | 7 sheets (see below) |
| `best_model_13_review.txt` | Raw source + every model's output, readable without Excel |
| `placement_audit_10_report.txt` | Placement audit — verdict, evidence, all 126 findings by product |
| `enchanted_forest_field_mapping.txt` | Product 451390 walked through field by field |

### `best_model_13.xlsx`

| Sheet | Contents |
|---|---|
| `Ranking` | 13 models: coverage, MISSING, fields filled, cost, tokens |
| `Quality_vs_Cost` | Coverage against cost — where quality plateaus |
| `Per_Product` | 10 products x 13 models |
| `Side_By_Side` | Every field, all 13 models in adjacent columns |
| `Top_Models_Side_By_Side` | Top 3 + gpt-5.6-terra + incumbent, with raw source alongside |
| `Raw_Source` | Full raw text per product |
| `Content_By_Model` | All 28 fields per product per model |

### `scripts/`

| Script | Does |
|---|---|
| `build_best_model_batches.py` | One JSONL per model. Parameter sets read from `model_compatibility_final.json`, never guessed — gpt-4 family needs `max_tokens`+`temperature`, gpt-5/o-series need `max_completion_tokens` only, and the wrong one fails the whole batch |
| `run_best_model_batches.py` | One Batch job per model, polled concurrently. Truncation and unparseable JSON tracked separately from quality |
| `screen_best_models.py` | Scores content survival; merges 4 previously-measured models verbatim |
| `verify_best_models.py` | 6 integrity assertions |
| `build_best_model_workbook.py` | Workbook + review txt |
| `add_top4_sheet.py` | The narrowed side-by-side sheet |
| `audit_placement_10.py` | Placement audit — 7 detectors |
| `build_placement_report.py` | Renders the audit report |

Same caveat as the rest of this repo: these are copied from a larger internal
pipeline and import modules not included here — `loss_detector.py`,
`screen_model_comparison.py`, `build_model_comparison_batches.py`, and
`model_compatibility_final.json`. **A snapshot for review, not a standalone
runnable package.** `run_best_model_batches.py` reads `OPENAI_API_KEY` from the
environment; no key is stored in this repo.

---

## How much to trust this

**Verified.** Integrity assertions passed: state files match screen output (no
fix applied), extracted text traces back to raw source (no invented content),
and the 4 merged baselines are numerically unchanged. Prompts were confirmed
byte-identical to the original run.

**Reliability ≠ capability.** `gpt-5-nano`, `o4-mini` and `gpt-5` returned
truncated or unparseable output on some products. Scored naively they look
poor; measured only on responses that worked, all three reach ~99%. They are
unreliable, not weak — a distinction that only surfaced because bad JSON was
tracked separately from quality.

**Limits, stated plainly:**

- **10 products.** Small. Directionally useful, not statistically settled.
- **The placement audit is regex, and regex cannot do judgement.** Three
  detectors were confidently wrong on the first run and were corrected only by
  reading raw text: `D2` over-flagged paragraphs straddling two labels (29→12);
  `D1` flagged a rate card's free tier as a contradiction; `D4` flagged models
  for routing cancellation text somewhere *better* than the catch-all
  (downgraded to INFO). All published counts are post-correction. **The
  evidence is the result; the counts only sort it.**
- **No LLM judge has been run on these 13 models.** Rule-based detection finds
  what it was told to look for. Absence of a finding is not proof of correct
  placement. This repo's `checker/` is the right tool for that.
- **gpt-5.4-nano's coverage is slightly flattering** — on product 391584 it hit
  100% partly by duplicating content across two fields, and coverage rewards
  duplication.

---

## Next steps

1. **Strip markdown in code.** gpt-5.4-nano leaves `**`/`##` in 17 fields,
   worst of any model — cosmetic, trivially fixable, zero risk.
2. **Fix the 8 misfiled `extras:` rows in code, not the prompt.** Measured
   across all 11,231 Fareharbor rows, 862 have an `extras:` section and only 8
   (0.9%) are clearly misfiled. A V4.7 prompt bump is not worth a full re-run
   for that, and added narrowing rules are what caused the V4.6 regression.
3. **Run `checker/` on gpt-5.4-nano** and compare against the 77.5% baseline.
   That is the measurement that would settle this.
