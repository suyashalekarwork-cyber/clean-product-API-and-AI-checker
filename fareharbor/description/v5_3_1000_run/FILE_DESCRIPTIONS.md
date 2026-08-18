# File descriptions — `v5_3_1000_run/`

What each file is, and which one to open for which question.

---

## The two to review

| File | What it is |
|---|---|
| **`reports/v5_3_random1000_audit.txt`** | The full per-product audit — 3.2 MB, 1,000 products, findings first then the clean ones. Each entry: verdict, comment, retention, the raw description, and every filled column. **Start here.** It opens with a method note explaining exactly how much of the 1,000 was hand-read and how much was detector-checked. |
| **`prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt`** | The prompt that produced everything else. The heading gate, the 22-field contract, and six worked examples. Read this to judge whether a given output is a defect or the rules working as written. |

No workbook for this run — the txt is the deliverable.

---

## Input

| File | What it is |
|---|---|
| `input/random1000_products.json` | Which 1,000 products, the seed (42), the pool size (10,570), and the rule: a uniform random draw from the products the 500-run never touched. Reproducible. |

**Not shipped: the raw source data and the Batch API files.** The Fareharbor raw
JSON (11,236 files) and the batch input/output are too large — the 28 KB system
prompt is repeated in every one of the 1,000 requests, so ~97% of the input file
is the same string. **Ask Huadong for the data as a zip.** With it, the batch
rebuilds exactly via `scripts/build_v5_3_random1000_batch.py`.

---

## Scripts

Run in this order to reproduce:

| Script | Does |
|---|---|
| `select_1000_random.py` | Picks the 1,000 — uniform random, seed 42, excluding the 500 already run, skipping products with no description |
| `build_v5_3_random1000_batch.py` | Builds the Batch API input from the prompt + the product list |
| `run_v5_3_random1000_batch.py` | Uploads, polls until done, downloads the output |
| `score_v5_3.py` | Retention, duplication, invention, and the V5.3 rule checks. Carries the calibration that stops a content-loss detector over-reporting ~3× — lead-in lines, bare labels, inline `Label: value` pairs, and sentence splits on abbreviations are all excluded |
| `detect_v5_3_issues.py` | The defect-class detectors, each derived from the 100-product hand audit and checked back against those 100 where the answers are known |
| `audit_v5_3_random1000_comments.py` | The hand-written verdict and comment for each of the 34 flagged products — including the 9 overturned as detector artifacts |
| `build_v5_3_random1000_txt.py` | Builds the audit txt |

Scripts import shared helpers (`strip_html`, `find_raw_file`) from
`build_model_comparison_batches.py`, which is not in this folder — see the repo
root.

---

## Which file answers which question

| Question | Open |
|---|---|
| What's wrong, and with which products? | `reports/v5_3_random1000_audit.txt`, findings are first |
| Why was *this* product judged that way? | search the product ID in the audit txt |
| Is this output a defect, or the rules working? | `prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt` |
| How much of the 1,000 was actually read by a person? | the method note at the top of the audit txt |
| How were these 1,000 chosen? | `input/random1000_products.json`, or `scripts/select_1000_random.py` |
| How does this compare with the hardest products? | `README.md` → *What the two sample types show* |
