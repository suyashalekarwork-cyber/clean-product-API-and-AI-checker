# V5.3 — heading-gated extraction, 500 products

Prompt `SYSTEM_PROMPT_FH_DESC_V5_3` run on the 500 hardest Fareharbor products
via `gpt-5.6-luna`. **499/499 completed, 0 failed, 0 truncated, 0 unparseable.**

**Result: 474 of 499 products (95.0%) show no known issue.**

| | Products | Rate |
|---|---|---|
| No known issue | 474 | 95.0% |
| **Our extraction defects** | **11** | **2.2%** |
| — of which cost the customer information | 5 | 1.0% |
| Supplier data, reproduced faithfully | 14 | 2.8% |

The 5 that cost anything are 3 content losses and 2 difficulty ratings filed as
restrictions. The other 6 are cosmetic — labels stripped from values that
survived, and marketing lines in a list column.

---

## What V5.3 does differently

Earlier versions let the model decide which section a *sentence* belonged to.
Measured on a 329-failure sample, **294 (89.4%) were real text filed under the
wrong heading** — and a wrong section is worse than an empty one, because the
portal shows it to a travel agent as fact.

V5.3 extracts a section **only when the supplier wrote a heading for it**. No
heading → the field stays empty and the text stays in About. An empty field is a
correct answer.

---

## Priority matrix

Same rows as the `Priority_Matrix` sheet in `v5_3_500_audit.xlsx`, generated
from one source so they cannot drift apart.

### P1 — the customer loses information or is misled

| Issue | Products | IDs | Impact | Fix | Whose |
|---|---|---|---|---|---|
| **Content loss** | 3 (0.6%) | `371805` `535701` `293135` | Facts gone from the page entirely | Deterministic post-check, **not** a prompt rule — see Repeatability | ours |
| **`what_to_bring` misleads** | 3 (0.6%) | `327258` `156525` `500245` | Box lists things the customer does *not* need to bring | Extend the line test to `what_to_bring` as the third point-wise column | supplier — we could override |

`327258` is the clearest case in the run: its entire What-to-Bring section reads
*"Salt Spray Surf School provides all surfboards needed for these days, wetsuits
are provided if need be."*

### P2 — visibly wrong, but nothing lost

| Issue | Products | IDs | Impact | Fix | Whose |
|---|---|---|---|---|---|
| Difficulty filed as a restriction | 2 (0.4%) | `466438` `491113` | Restrictions box reads `Moderate` / `Level: Hard` | Two lines of prompt: difficulty names no column → about | ours |
| Content overrode the heading | 1 (0.2%) | `251713` | Answer is arguably *better*, but the gate was bypassed | Watch only — do not fix yet | ours, debatable |

### P3 — cosmetic

| Issue | Products | IDs | Impact | Whose |
|---|---|---|---|---|
| Inline label stripped | 3 (0.6%) | `713497` `324361` `697755` | Every value survived; the section has no title | ours |
| Marketing in a list column | 2 (0.4%) | `198064` `501920` | One line reads oddly | ours |

### P4 — supplier data, not ours to fix

| Issue | Products | IDs | What to do |
|---|---|---|---|
| Raw repeats itself | 9 (1.8%) | `509794` `203555` `249729` `330482` `279178` `444088` `397465` `319096` `171361` | De-duplicate at **render time**; do not change extraction |
| Field name pasted into the description | 1 | `266189` — raw is literally `meeting_point: Te Anau` | Nothing to do |
| Headings with no content under them | 1 | `680927` | Correct behaviour; exclude from scoring |

Fixing P4 would mean inventing a reason to drop text the supplier deliberately
wrote twice. Out of scope for extraction.

---

## Repeatability — the most important finding

The 500 re-ran all 100 products from the previous run on the **identical**
prompt, so the two are directly comparable. **Most defects did not reproduce:**

| Product | Run 1 (100) | Run 2 (500) | |
|---|---|---|---|
| `457336` | lost 3 sentences | **lost 0** | vanished |
| `676702` | lost 1 sentence | **lost 0** | vanished |
| `135308` | duplicated | **clean** | vanished |
| `417608` | duplicated | **clean** | vanished |
| `371805` | lost 1 sentence | lost 1 | **repeatable** |
| `509794` | duplicated | duplicated | **repeatable** |

Four of six were sampling noise, not a rule the model gets wrong.

**This changes what a fix can achieve.** A prompt rule can only address the two
repeatable cases. For the random ones no wording is a guarantee — the only way
to make content loss structurally impossible is a deterministic check after
extraction that returns any unaccounted-for sentence to About.

It also means **a single run understates the true rate**: a different run loses
different sentences. Expect ~1% of products to have something wrong on any given
pass, but not the same 1%.

---

## The strongest evidence: products with no heading at all

51% of the run (254 products) has **no heading naming a column** — the exact
situation that produced the original 89% misclassification, because the model
has nothing to go on.

| Group | Products | Issues found |
|---|---|---|
| No headings at all — pure prose | 192 | **0** |
| Headings present, none maps to a column | 37 | **0** |
| Filled a column anyway | 23 | 1 real defect |

**229 of 254 with zero issues.** Of the 23 that filled something, 20 turned out
to be the model reading a heading the review script's regex could not see —
`Your Day in the Hunter Valley begins at:` (8 words, regex caps at 7),
`Cost: $79 per adult` (inline), `Accessebility` (supplier's typo, matched by
meaning). One was a supplier data accident, one debatable, one real (`491113`).

Detail in `reports/v5_3_no_heading_review.txt`.

---

## Files

| Path | What it is |
|---|---|
| `v5_3_500_audit.xlsx` | 4 sheets — `Priority_Matrix`, `Issues_Only` (25), `All_Products` (499 with verdict + comment), `Per_Product` (raw beside all 22 columns) |
| `reports/v5_3_hard500_audit.txt` | Full per-product audit, 1.5 MB. Issues first, clean products last. Each entry: verdict, comment, retention, raw, every filled column |
| `reports/v5_3_no_heading_review.txt` | The 254 no-heading products in the 3 groups above |
| *(batch input not shipped)* | The Batch API input was 15 MB — the 28 KB system prompt repeated in all 499 requests — so it is left out of the repo. Rebuild it exactly with `scripts/build_v5_3_hard500_batch.py`, which reads the prompt from `prompts/` and the product list from `input/hard500_products.json`. |
| `input/v5_3_hard500_output.jsonl` | Raw Batch API replies |
| `input/hard500_products.json` | The product selection and its ordering rule |
| `prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt` | The prompt itself |
| `scripts/` | Selection, batch build, scorer, issue detectors, audit comments, report/workbook builders |

---

## Method — read before trusting a clean verdict

500 products cannot be read line by line. Every defect class found in the
earlier **100-product hand audit** was turned into a detector
(`scripts/detect_v5_3_issues.py`), the detectors were checked back against those
100 where the answers are already known, then run over all 499. **Every product
they flagged was then opened and read** against its raw description — the
verdicts are that reading, not the detector output. Five detector hits were
overturned as false positives and are recorded with the reason.

So: the flagged products are hand-verified. The rest mean *"none of the known
defect classes fired"*, which is weaker than *"read and confirmed correct"*. A
defect class that never appeared in the first 100 would not be caught here.

**The scorer under-reports headings.** Its regex missed 20 real headings out of
23 in the no-heading group — inline labels, typos, 8-word phrases,
emoji-prefixed headers. When it reports `filled_but_no_heading`, treat that as a
prompt to look, not a verdict.

---

## What is not fixed

1. **Content loss (3 products).** Needs a deterministic post-check, not more
   prompt wording — three prompt versions running have each written a stronger
   content-loss rule and it keeps returning somewhere new. The repeatability
   data explains why: the loss is random.
2. **`what_to_bring` line test.** The third point-wise column, with an equally
   precise test. Needs a decision, because it means overriding a supplier's own
   heading a second time (`what_included` already rejects "available for
   purchase" under an `Inclusions:` heading).
3. **Difficulty ratings.** Two lines of prompt; no downside.

---

## Reproducing

```bash
python scripts/select_500_hardest.py        # -> hard500_products.json
python scripts/build_v5_3_hard500_batch.py  # -> v5_3_hard500_batch.jsonl
# submit to the OpenAI Batch API, download output
python scripts/score_v5_3.py v5_3_hard500_output.jsonl
python scripts/detect_v5_3_issues.py v5_3_hard500_output.jsonl
python scripts/build_v5_3_500_audit_txt.py
python scripts/build_v5_3_500_workbook.py
```

Scripts expect `find_raw_file` / `strip_html` from
`build_model_comparison_batches.py` and the raw Fareharbor JSON, neither of
which ships here — see the repo root for the dataset.
