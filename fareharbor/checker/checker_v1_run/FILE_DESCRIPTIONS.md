# File descriptions — `checker_v1_run/`

What each file is, and which one to open for which question.

---

## The three to review

| File | What it is |
|---|---|
| **`review_v1_random1000.xlsx`** | The checker's output on 1,000 products. Four sheets: `Summary`, `Findings` (167 individual faults), `Per_Product` (all 1,000 with a score and tray), `Validation_73`. **Start here.** |
| **`review_v1_validation73.xlsx`** | The proving run. 73 tours a human had already judged, with the checker's verdict beside the human's. This is the test the checker had to pass before it was allowed near the 1,000. |
| **`reports/review_v1_random1000.txt`** | The same 1,000 products in plain text — readable end to end without Excel. |

---

## The prompts

| File | What it is |
|---|---|
| `prompts/SYSTEM_PROMPT_FH_REVIEW_V3.txt` | The first marker. Reads the supplier's original next to all 22 boxes and reports the four fault types. |
| `prompts/SYSTEM_PROMPT_FH_REVIEW_VERIFY_V3.txt` | The second marker. Assumes the extraction was correct and tries to knock each fault down. Only faults that survive are counted — this is what takes false alarms from about 42% to 4%. |

## Scripts

| Script | Does |
|---|---|
| `review_contract.py` | Slices the column rules **live** out of the extraction prompt. This is why the marker cannot drift from the extractor — they read the same words. Earlier checkers went stale because someone hand-copied the rules and the copy was never updated. |
| `build_review_batch.py` | Builds the first-pass Batch API input |
| `run_review_batch.py` | Uploads, polls, downloads |
| `build_review_verify_batch.py` | Builds the second pass — over flagged findings only, not everything |
| `score_review.py` | The scoring. **Plain code, not the AI** — points come off per surviving fault and each tour lands in one of three trays |
| `validate_review_vs_human.py` | The 73-product test. Measures the checker against verdicts a human already gave |
| `build_review_1000_txt.py` · `build_review_1000_workbook.py` | Build the deliverables |

## Reports

| File | What it is |
|---|---|
| `reports/review_v1_random1000.txt` | Full per-product output on the 1,000 |
| `reports/review_v1_validation73.txt` | The validation run in full, including where the checker disagreed with the human |

**Not shipped: the raw source data.** The Fareharbor raw JSON and the Batch API
input files are too large — the system prompt repeats on every request, so most
of the file is the same string over and over. **Ask Huadong for the data as a
zip.**

---

## Which file answers which question

| Question | Open |
|---|---|
| What faults were found, and where? | `Findings` sheet in `review_v1_random1000.xlsx` |
| How did this tour score, and which tray is it in? | `Per_Product` sheet |
| Can the checker be trusted at all? | `review_v1_validation73.xlsx` — its answers beside a human's |
| What is it actually looking for? | `prompts/SYSTEM_PROMPT_FH_REVIEW_V3.txt`, or the seven steps in `README.md` |
| Why doesn't it drift from the extractor? | `scripts/review_contract.py` |
| How is the score calculated? | `scripts/score_review.py` — it is code, not a model judgement |

---

## Provenance

The checker was built and validated in a **separate working session** from the
extraction work in `fareharbor/description/v5_3_500_run/`,
`fareharbor/description/v5_3_1000_run/` and `fareharbor/booking/booking_v5_3_run/`.
The headline figures in `README.md` — 42 versus 2, and 42% → 4% — come from that
session's own validation run.
