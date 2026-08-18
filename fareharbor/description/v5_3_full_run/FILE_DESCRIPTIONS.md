# File descriptions — `v5_3_full_run/`

What each file is, and which one to open for which question.

---

## The three to review

| File | What it is |
|---|---|
| **`v5_3_full_summary.md`** | Run integrity, the findings table, and — importantly — which numbers were checked and which are upper bounds. Two flags were sampled before publishing; the rest are not verified and say so. **Start here.** |
| **`v5_3_full_scores.xlsx`** | All **11,069** products, one row each: retention, fields filled, headings found, and a count per finding type. Sorted worst-first with a filter on. This is where you look up a specific product id. |
| **`reports/v5_3_full_findings.txt`** | The **2,619 products that have a finding**, with the raw description beside the extracted columns. Deliberately not all 11,069 — 8,450 products have nothing wrong and a 35 MB file of them helps nobody. |

---

## The prompt

| File | What it is |
|---|---|
| `prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt` | The prompt that produced everything else — the heading gate, the 22-field contract, six worked examples. Read this to judge whether an output is a defect or the rules working as written. |

## Input

| File | What it is |
|---|---|
| `input/v5_3_full_products.json` | Which products were selected (every one with a non-empty description), how many were skipped, and how the batch was chunked. |
| `input/v5_3_full_output_01..04.jsonl` | The raw Batch API replies, ~28 MB across four files. **Four files rather than one because the run had to be chunked** — 345 MB of batch input exceeds the API's 200 MB per-file limit. |

**Not shipped: the raw source data and the batch INPUT files.** The Fareharbor
raw JSON is 11,236 files, and the batch input is 345 MB — the 28 KB system prompt
is repeated in all 11,069 requests, so ~97% of it is the same string.
**Ask Huadong for the data as a zip.** With it, the input rebuilds exactly via
`scripts/build_v5_3_full_batch.py`.

---

## Scripts

Run in this order:

| Script | Does |
|---|---|
| `build_v5_3_full_batch.py` | Selects every product with a description and writes the batch input **in chunks** of 3,500 (~109 MB each). Refuses to write a chunk over the 200 MB API limit. |
| `run_v5_3_full_batch.py` | Submits chunks **one at a time** and polls each to completion. Sequential because submitting all four at once exceeded the org's 40M enqueued-token cap and two were rejected. Resumable: batch ids are saved on submission and chunks with output already on disk are skipped, so a restart never re-pays for completed work. A failed batch is reported loudly with its error code. |
| `score_v5_3.py` | Retention, duplication, invention, and the V5.3 rule checks. Carries the calibration that stops a content-loss detector over-reporting ~3× — lead-ins, bare labels, inline `Label: value` pairs and abbreviation splits are all excluded. |
| `booking_common.py` | Imported for `parse_booking_json`, the JSON repair. Despite the name it is generic: it fixed the one malformed response in this run (`737956`, an orphaned string where a key should be). Without it that product would have been dropped from every analysis and read as empty. |
| `build_v5_3_full_deliverables.py` | Builds the summary, the findings txt and the workbook. |

---

## Which file answers which question

| Question | Open |
|---|---|
| How did the full catalogue do? | `v5_3_full_summary.md` |
| How did *this* product do? | `v5_3_full_scores.xlsx`, filter on `product_id` |
| Which products have problems, and what? | `reports/v5_3_full_findings.txt` |
| Which numbers can I trust? | `v5_3_full_summary.md` → *What was verified* — two flags were sampled, the rest are upper bounds |
| Is this a defect or the rules working? | `prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt` |
| How do I re-run it without paying twice? | `scripts/run_v5_3_full_batch.py` — it resumes |
