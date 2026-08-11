# File descriptions — `booking_v5_3_run/`

What each file is, and which one to open for which question.

---

## The three to review

| File | What it is |
|---|---|
| **`booking_v5_3_data.xlsx`** | **The data.** One row per product, 30 columns: `product_id`, `product_name`, the 25 extracted columns, then `recovered_content`, `reworded_content` and `duplicate_content`. The last three are produced by code, never by the AI — they say what the extraction missed and **which heading it belonged under**. This is the only file where "what we got" and "what we missed" can be read together. **Start here.** |
| **`booking_v5_3_audit.xlsx`** | The review workbook. Four sheets: `Summary` (headline gates and verdict counts), `Findings` (27 individual findings with the offending text), `All_Products` (all 100 with a verdict, a written comment, retention and counts), `Per_Product` (each product's raw booking notes beside all 25 columns). |
| **`reports/booking_v5_3_hard100_audit.txt`** | The full per-product audit in plain text — 1.2 MB, findings first, clean products last. Each entry: what changed versus the previous prompt, the automated findings, the three post-processing sections, the raw booking notes, and every filled column. Use it to read a product end to end without Excel. |

---

## The prompt

| File | What it is |
|---|---|
| `prompts/SYSTEM_PROMPT_FH_BOOKING_V5_3.txt` | The prompt that produced everything else. 28.5 KB — the heading gate, the seven rules, the 25-column contract, and four worked examples. Read this to judge whether a given output is a defect or the rules working as written. The examples deliberately use invented names (`Sample Wharf`, `Acme Parking`, `example.test`) so that any of those strings appearing in real output proves the model copied from the prompt. |

## How the columns were decided

| File | What it is |
|---|---|
| `reports/booking_column_definitions.md` | **The source document the prompt was written from.** Per column: what it holds, the real supplier headings that route to it with counts, what does NOT belong, and the Figma section. Also records the decisions taken and rejected — why `operations` is not a column, why `what_not_to_bring` was kept at only 7 suppliers, why greetings go to `flags`. |
| `reports/booking_heading_census.md` | The census. Every distinct heading suppliers wrote across all 8,244 products that have booking notes, with counts and coverage curves. |
| `reports/booking_headings_with_counts.md` | The same census in plain language, grouped by meaning, with all 3,729 headings listed. Open this to see how many different ways suppliers write the same idea — "What to Bring" is written at least eight ways, totalling ~2,664 appearances. |
| `reports/booking_column_map.md` | Every heading assigned to a column, with **two** numbers each: how often it appears, and how many *different suppliers* use it. The second number is the one that matters — 48 uses by one supplier is that operator's template, not a shared concept. |
| `reports/booking_v5_to_v5_3_diff.md` | What changed between the previous prompt and this one, product by product and column by column, on the same 100 products. Shows where content moved when the 10 new columns were added. |

## Input

| File | What it is |
|---|---|
| `input/booking100_products.json` | Which 100 products were chosen, and why — stratified across the four measured booking-notes regimes (heading-rich, long-with-no-heading, majority-bullet, inline-label-only) rather than a plain "hardest" sort, because a length-ranked list would only return the first of them. |
| `input/booking_v5_3_100_output.jsonl` | The raw Batch API replies, one JSON line per product. The source of truth everything else is derived from. |

**Not shipped: the raw source data.** The Fareharbor raw JSON (11,236 files) and
the Batch API **input** JSONL are too large to include — the 28 KB system prompt
is repeated in every request, so 100 products is ~3.5 MB of which ~97% is the
same string. **Ask Huadong for the data as a zip.** With it, the input JSONL
rebuilds exactly via `scripts/build_booking_v5_3_batch.py`.

---

## Scripts

Run in this order to reproduce the whole thing:

| Script | Does |
|---|---|
| `select_booking_100.py` | Picks the 100 products, stratified across the four regimes → `booking100_products.json` |
| `build_booking_v5_3_prompt.py` | Composes and appends the prompt. Asserts 25 keys present, zero description field names leaked, every named rule present, and all pre-existing prompt blocks intact — and refuses to write if any check fails |
| `build_booking_v5_3_batch.py` | Builds the Batch API input from the prompt + the product list |
| `run_booking_v5_3_batch.py` | Uploads, polls, downloads. Also checks every response returned exactly the 25 expected keys |
| `booking_common.py` | Shared heading detection. **The reason this is booking-specific:** the description-era detector returns the packing list as headings (`sunscreen` 834, `towel` 430), because booking notes are list-dominated where descriptions are prose-dominated |
| `booking_postprocess.py` | The two report-only passes — `recovered_content` and `duplicate_content`. **Neither deletes anything** |
| `score_booking_v5_3.py` | All the gates: contamination, URL integrity, invention, mid-sentence starts, line tests, plus the post-processing passes |
| `audit_booking_v5_3_comments.py` | The hand-written verdict and comment for every flagged product, including the ones overturned as detector artifacts |
| `build_booking_v5_3_audit_txt.py` | Builds the plain-text audit |
| `build_booking_v5_3_workbook.py` | Builds both workbooks |
| `build_booking_v5_to_v5_3_diff.py` | Builds the version diff |

Scripts import `strip_html` / `find_raw_file` / `make_request` from
`build_model_comparison_batches.py`, which is not in this folder — see the repo
root.

---

## Which file answers which question

| Question | Open |
|---|---|
| What did we extract for this product, and what did we miss? | `booking_v5_3_data.xlsx` |
| What's wrong, and with which products? | `README.md`, or `Findings` in the audit workbook |
| Why was *this* product judged that way? | `All_Products` sheet, or search the product ID in the audit txt |
| Is this output a defect, or the rules working? | `prompts/SYSTEM_PROMPT_FH_BOOKING_V5_3.txt` |
| Why does this column exist at all? | `reports/booking_column_definitions.md` |
| How do suppliers actually write this heading? | `reports/booking_headings_with_counts.md` |
| What changed from the previous prompt? | `reports/booking_v5_to_v5_3_diff.md` |
| How do I re-run this? | the Scripts table above |
