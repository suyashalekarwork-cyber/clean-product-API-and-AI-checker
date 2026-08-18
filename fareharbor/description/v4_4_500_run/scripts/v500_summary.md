# ESAR Pipeline — 500 Brand-New Products, Batch API, Unchanged Pipeline Logic

## 1. Per-band selection counts (requested vs actual)

| Band | Requested | Actual |
|---|---|---|
| 0-200 | 200 | 200 |
| 201-350 | 150 | 150 |
| 351-500 | 90 | 90 |
| 501-650 | 60 | 60 |

No shortfalls — every band had enough previously-unused, ≤650-word candidates
after excluding all 112 prior-round product IDs (32 explicit + 30 from the
30-set + 50 from the 50-set). Selected via `pandas.sample(random_state=42)`
per band from a 9,255-candidate pool.

## 2. Batch job

**One Batch API job, 1,000 requests (500 products x desc + booking).**

- Completed: 1,000/1,000, **0 failed**
- Wall-clock: 364s (uploaded → validating → in_progress → finalizing → completed)
- Tokens: 3,425,958 prompt + 257,134 completion = **3,683,092 total**
- **Cost: $0.3341** (Batch API 50%-discount rate: $0.075/$0.30 per 1M prompt/completion tokens)

## 3. Products dropped due to failures

**None.** All 1,000 calls succeeded and were parseable; `v500_failures.csv` is
empty and no product was excluded at the screen stage.

## 4. Products with missing content / sentences pasted

**Products with at least one MISSING unit:** counted via the pre-fix
snapshot — **416 total MISSING units** found across the 500 products.
**All 416 processed: 413 pasted, 3 skipped as already-present duplicates.**
467 PARTIAL units recorded (not touched), per the flagging rule.

## 5. Re-screen: missing before vs after

**416 → 0.** Average word coverage rose from **93.41% to 98.11%**.

## 6. Assertion results — ALL CLEAR

- **Content preserved**: PASS, 0 violations across 500 products.
- **Verbatim paste**: PASS, all 413 pasted sentences confirmed verbatim in raw text.
- **No fragments (≥4 words)**: PASS, every pasted line is a complete sentence.

No violations of any kind at 500-product scale — the same clean result as
the 30- and 50-product rounds, now validated on a sample 10-16x larger.

## 7. Products flagged for human review (4+ sentences pasted)

**37 of 500 (7.4%)**:
97611, 103636, 119985, 135308, 149054, 190906, 234331, 268950, 268963,
302171, 328673, 371805, 430823, 436916, 439149, 457323, 457336, 483868,
492734, 493744, 525721, 535706, 551344, 553713, 565015, 579517, 584942,
593334, 649958, 659135, 659138, 659145, 685398, 702580, 712976, 719471,
724383.

Full detail (raw text + pasted sentences by home bucket) in the
`Review_Queue` sheet.

## 8. Bucket counts

| Status | Count |
|---|---|
| complete | 500 |
| needs_review | 0 |

Every product reached `missing_after == 0` — no product needed further
paste intervention beyond what the code-only fix already applied. (The
37 flagged-for-review products are still `complete` by the missing-count
definition; the review flag is a separate volume-based signal, not a
completeness failure.)

## 9. Coverage by length band — does the 201-500 middle band remain weakest?

| Band | n | Avg coverage before | Avg coverage after | Total MISSING before |
|---|---|---|---|---|
| 0-200 | 200 | 94.58% | 98.79% | 65 |
| 201-350 | 150 | 92.52% | 97.98% | 131 |
| 351-500 | 90 | 93.71% | 97.90% | 100 |
| 501-650 | 60 | 91.26% | 96.45% | 120 |

At 500-product scale, coverage now declines **roughly monotonically with
length** — 0-200 is cleanest (94.58%), 501-650 is worst (91.26%) — a
cleaner length-correlated trend than the 50-product round showed (where
351-500, not 501-650, was the worst band). The n=50 result was likely
sample-composition noise from small per-band counts (only 6-9 products);
at n=500 (60-200 per band) the longer-text-loses-more-content pattern
holds more consistently, though 351-500 still sits slightly better than
201-350 rather than continuing to decline in strict order — the trend is
directional, not perfectly linear.

## 10. Total cost

**$0.3341** for the entire 500-product extraction (1,000 Batch API calls).
No AI cost anywhere else in this run (code-only fix, no QA bot, no
adjudicator, no retry).

## 11. Conclusion

**The pipeline holds at 500 products with zero pipeline logic changes and
zero failures**: 1,000/1,000 Batch API calls succeeded, the code-only
paste-to-home-bucket fix eliminated all 416 MISSING units with zero
assertion violations across a 10x larger sample than the last round, every
product reached complete (missing_after=0), and only 7.4% needed a
human-review flag for pasted-sentence volume — the system scales cleanly
from 30 to 500 products with consistent, predictable behavior.
