# The AI Checker — V1 on 1,000 products

An independent marker that reads the supplier's original text next to the
extracted boxes and reports what went wrong.

---

## Check these three first

| File | What it is |
|---|---|
| **`review_v1_random1000.xlsx`** | The checker's output on 1,000 products. Sheets: `Summary`, `Findings` (167), `Per_Product` (1,000), `Validation_73`. **Start here.** |
| **`review_v1_validation73.xlsx`** | The proving run — 73 tours a human had already judged, used to test the checker before it was trusted. |
| **`reports/review_v1_random1000.txt`** | The full per-product output in plain text. |

---

## How the checker works

**1. It gets the same rulebook as the extractor.** The rules for which text belongs in which box are cut straight out of the extractor's own instructions. Same words, so the marker can't be judging by different standards.

**2. It sees one tour at a time — the original plus all 22 boxes.** Including the empty ones. You can't notice a box that _should_ have been filled if you're only shown the filled ones.

**3. It looks for exactly four faults, nothing else:**

- text that vanished
- text in the wrong box
- a label stripped off its value
- a heading the supplier wrote, with an empty box behind it

**4. It labels each fault "ours" or "the supplier's."** If the supplier's own bad heading caused it, it doesn't count against us.

**5. A second marker then argues back.** It assumes the extraction was correct and tries to knock each fault down. Only the ones that survive count. This cuts false alarms from about 42% to 4%.

**6. Ordinary code does the scoring — not the AI.** Points come off per surviving fault. Each tour ends up in one of three trays: _ship as-is_, _spot-check_, or _needs a person_.

**7. It had to pass a test before being trusted.** 73 tours a human had already judged. It failed twice, was fixed, then passed — and only then ran on the 1,000.

---

### The same seven steps on a real tour (product 178949)

1. **Supplier wrote:** `##Schedule` then `10:30am - 1:00pm`
2. **Extractor produced:** `10:30am - 1:00pm` sitting in _about_, between "Bookings essential" and "Lake Karapiro is perfect for beginners"
3. **The fault:** the word _Schedule_ is gone — the time now floats with nothing saying what it is
4. **Owner:** ours
5. **Second marker:** tried to reject it, couldn't — upheld
6. **Score:** 15 points off → 85 → _ship as-is_
7. —

**The key point:** every character of value survived. Nothing is missing. That's why every earlier tool called this tour clean — they compared the boxes against themselves and found no gap. This one compares them against the supplier's original.

Found **42** of these in 1,000 tours. The old method found **2**.

---

## Files

| File | What it is |
|---|---|
| `review_v1_random1000.xlsx` | Checker output on the 1,000-product run — Summary / Findings (167) / Per_Product (1,000) / Validation_73 |
| `review_v1_validation73.xlsx` | The 73 known-answer products, with the checker's verdict beside the human's |
| `reports/review_v1_random1000.txt` | Full per-product output, plain text |
| `reports/review_v1_validation73.txt` | The validation run in full |
| `prompts/SYSTEM_PROMPT_FH_REVIEW_V3.txt` | The checker prompt — the first marker |
| `prompts/SYSTEM_PROMPT_FH_REVIEW_VERIFY_V3.txt` | The second marker, which argues back |
| `scripts/review_contract.py` | Slices the column rules **live** out of the extraction prompt, so the marker cannot drift from the extractor |
| `scripts/build_review_batch.py` · `run_review_batch.py` | Build and run the first pass |
| `scripts/build_review_verify_batch.py` | Builds the second pass, over flagged findings only |
| `scripts/score_review.py` | The scoring — plain code, not the AI |
| `scripts/validate_review_vs_human.py` | The 73-product test that had to pass first |
| `scripts/build_review_1000_txt.py` · `build_review_1000_workbook.py` | Build the deliverables |

**Not shipped: the raw source data.** The Fareharbor raw JSON and the Batch API
input files are too large — the system prompt repeats on every request, so most
of the file is the same string over and over. **Ask Huadong for the data as a
zip.**

---

## Note on provenance

The checker was built and validated in a separate working session from the
extraction work in `v5_3_500_run/`, `v5_3_1000_run/` and `booking_v5_3_run/`.
The figures on this page — the 42-versus-2 comparison and the 42% → 4%
false-alarm reduction — come from that session's own validation run, recorded in
`review_v1_validation73.xlsx`.
