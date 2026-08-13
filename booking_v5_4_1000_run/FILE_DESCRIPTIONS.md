# File descriptions — `booking_v5_4_1000_run/`

What each file is, and which one to open for which question.

---

## The three to review

| File | What it is |
|---|---|
| **`booking_v5_4_1000_audit.xlsx`** | All **1,000** products, one row each: retention, columns filled, headings found, a count per finding type, and the collapse measure. Sorted worst-first with a filter on. Sheets: `Summary`, `All_Products`, `Collapse`. **The verdict column is deliberately BLANK** — nobody has hand-read these, and pre-filling it would read as 1,000 clearances nobody gave. **Start here.** |
| **`reports/booking_v5_4_1000_audit.txt`** | The **177 products with a finding**, each showing the raw booking notes beside all 25 extracted columns, with blank VERDICT/COMMENT lines. Not all 1,000 — 823 products have nothing flagged and a file of them helps nobody. |
| **`booking_v5_4_1000_data.xlsx`** | The DATA rather than the audit: one row per product, the raw booking notes plus the 25 extracted columns, plus the three post-processing columns (`recovered_content`, `reworded_content`, `duplicate_content`) side by side. This is the closest thing to what a downstream consumer receives. |

---

## The prompt

| File | What it is |
|---|---|
| `prompts/SYSTEM_PROMPT_FH_BOOKING_V5_4.txt` | The prompt that produced everything else. Read it to judge whether an output is a defect or the rules working as written — particularly RULE 8 (URLs) and STEP 1E (the outer heading wins). |

## Input

| File | What it is |
|---|---|
| `input/booking1000_products.json` | Which 1,000 products were selected, the seed, the pool size, and the **observed** regime mix (70% heading-rich, 21% short-no-heading, 7.5% long-no-heading, 1% inline-label-only). That mix is measured, not imposed — it is what the catalogue actually looks like. |
| `input/booking_v5_4_1000_output.jsonl` | The raw Batch API replies, 2.4 MB. |

**Not shipped: the raw supplier data and the batch INPUT file.** The Fareharbor
raw JSON is 11,236 files, and the batch input is 31 MB because the 29 KB system
prompt is repeated in all 1,000 requests — ~97% of it is the same string.
**Ask Huadong for the data as a zip.** With it the input rebuilds exactly via
`scripts/build_booking_v5_4_1000_batch.py`.

---

## Scripts

Run in this order:

| Script | Does |
|---|---|
| `select_booking_1000.py` | Picks 1,000 uniform-random products (seed 42) from all 8,244 with booking notes, excluding the 600 already run. Asserts zero overlap. Deliberately NOT stratified — this run has to be representative or its rate cannot be quoted. |
| `build_booking_v5_4_1000_batch.py` | Writes the batch input. Refuses to run unless the V5.4 image rules are actually present in the extracted prompt — otherwise it would silently be a second V5.3 run. |
| `run_booking_v5_4_1000_batch.py` | Submits and polls. **Writes the batch id to disk BEFORE polling** — a long batch does not survive a session restart, and without the id there is no way to reattach to a run already paid for. Resumable; a failed batch is reported loudly rather than grouped with completed. |
| `score_booking_v5_3.py` | All the checks. Despite the name it is version-agnostic — it scores whatever output file it is given. Carries the collapse measure and the calibration that stops the content-loss detector over-reporting. |
| `booking_common.py` | Heading detection and `parse_booking_json` (repairs two malformed-JSON shapes gpt-5.6-luna emits intermittently — one product needed it here). |
| `booking_postprocess.py` | The two report-only passes. **May only ADD or REPORT, never DELETE** — a dedup pass trialled earlier would have emptied 9 booking fields across 8 products. |
| `build_booking_v5_4_prompt.py` | How V5.4 was built from V5.3: one surgical 13-line insert, with the "nothing else changed" claim proved by diff. Refuses to write if more than one region differs. |
| `build_booking_v5_4_1000_audit_txt.py` / `_workbook.py` | Build the three review files. |

---

## Which file answers which question

| Question | Open |
|---|---|
| How did the catalogue actually do? | `README.md` — and read *products at 100%*, not the mean |
| How did *this* product do? | `booking_v5_4_1000_audit.xlsx`, filter on `product_id` |
| Which products have problems, and what? | `reports/booking_v5_4_1000_audit.txt` |
| What did the extraction actually produce? | `booking_v5_4_1000_data.xlsx` |
| Is this a defect or the rules working? | `prompts/SYSTEM_PROMPT_FH_BOOKING_V5_4.txt` |
| Why is retention lower than the hardest-500? | `README.md` → *The one number that reads worse* |
| Are these 177 products defects? | **No.** They are a review queue — see the README's last section |
