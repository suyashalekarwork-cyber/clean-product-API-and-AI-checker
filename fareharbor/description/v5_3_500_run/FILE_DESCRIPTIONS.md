# File descriptions — `v5_3_500_run/`

What each file in this folder is, and which one to open for which question.

---

## The three to review

| File | What it is |
|---|---|
| **`v5_3_500_audit.xlsx`** | The review workbook. Four sheets: `Priority_Matrix` (every issue by severity, with product IDs), `Issues_Only` (the 33 flagged products), `All_Products` (all 499 with a verdict and a written comment), `Per_Product` (each product's raw description beside all 22 extracted columns). **Start here** — filterable, and it holds the verdicts. |
| **`prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt`** | The prompt that produced everything else. The rules the extraction actually followed, the 22-field output schema, and 6 worked examples. Read this to judge whether a given output is a defect or the rules working as written. |
| **`reports/v5_3_hard500_audit.txt`** | The full per-product audit in plain text — 1.5 MB, issues first, clean products last. Each entry: verdict, comment, retention, the raw description, and every filled column. Use it to read a product end to end without opening Excel. |

---

## Everything else

| File | What it is |
|---|---|
| `README.md` | The findings: severity matrix, totals, the two-phase delivery plan, the repeatability evidence, and what is not fixed. |
| `reports/v5_3_no_heading_review.txt` | The 254 products (51% of the run) where the supplier wrote **no heading naming a column**, split into three groups. This is the strongest evidence the heading gate holds — 229 of 254 had zero issues. |
| `input/v5_3_hard500_output.jsonl` | Raw Batch API replies, one JSON line per product. The source of truth everything else is derived from. |
| `input/hard500_products.json` | Which 500 products were chosen and the rule that ordered them (flagged for review → lowest coverage → longest input). |

**Not shipped:** the Batch API input JSONL. It was 15 MB because the 28 KB system
prompt is repeated in all 499 requests — ~97% of the file is the same string.
Rebuild it exactly with `scripts/build_v5_3_hard500_batch.py`.

---

## Scripts

Run in this order to reproduce the whole thing:

| Script | Does |
|---|---|
| `scripts/select_500_hardest.py` | Picks the 500 products → `hard500_products.json` |
| `scripts/build_v5_3_hard500_batch.py` | Builds the Batch API input from the prompt + product list |
| `scripts/score_v5_3.py` | Retention, duplication, invention, and the V5.3 rule checks |
| `scripts/detect_v5_3_issues.py` | Flags the known defect classes across every product |
| `scripts/scan_supplier_data_issues.py` | Finds problems in the **raw** text — repeats, placeholders, control characters, missing descriptions |
| `scripts/audit_v5_3_500_comments.py` | The hand-written verdict and comment per flagged product |
| `scripts/build_v5_3_500_audit_txt.py` | Builds the plain-text audit |
| `scripts/build_v5_3_500_workbook.py` | Builds the Excel workbook |
| `scripts/build_no_heading_review_txt.py` | Builds `v5_3_no_heading_review.txt` — the 254 no-heading products |

Scripts expect `find_raw_file` / `strip_html` from
`build_model_comparison_batches.py` and the raw Fareharbor JSON, neither of which
ships here — see the repo root for the dataset.

---

## Which file answers which question

| Question | Open |
|---|---|
| What's wrong, and with which products? | `README.md`, or `Priority_Matrix` in the workbook |
| Why was *this* product judged that way? | `All_Products` sheet, or search the product ID in the audit txt |
| What did the model actually output for a product? | `Per_Product` sheet, or the audit txt |
| Is this output a defect, or the rules working? | `prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt` |
| Does the heading gate hold when there's no heading? | `reports/v5_3_no_heading_review.txt` |
| How do I re-run this? | `README.md` → *Reproducing* |
