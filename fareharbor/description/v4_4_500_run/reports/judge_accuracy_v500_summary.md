# AI Placement-Accuracy Checker — v500 (500 products)

Scope: **placement only** — does each extracted field's text belong under
that field name? This does NOT check faithfulness to the raw text and does
NOT look for content dropped entirely, so the score below is a placement
accuracy figure, not an overall extraction-quality score.

Judge: single model `gpt-5.5-pro` — its verdict stands alone (no vote, so no DISPUTED category and no cross-check on outliers).

## Human-review bands (per product)

| band | score | action | products | % | fields |
|---|---|---|---|---|---|
| **NO_HUMAN_NEEDED** | 80-100 | No human needed — ship as-is | 281 | 56.2% | 2093 |
| **MAYBE_REVIEW** | 70-79.9 | Maybe — spot-check | 97 | 19.4% | 1002 |
| **HIGHLY_RECOMMENDED** | 0-69.9 | Human review highly recommended | 122 | 24.4% | 1038 |

- Fields judged: **4133** across 500 products
- Placement accuracy: **77.5%** (3203 CORRECT)
- WRONG_FIELD: 923
- GARBLED: 7
- DISPUTED (no majority): 0
- NO_VOTE (no model returned a verdict): 0

## Most-flagged fields

| field | flagged | judged | flag rate |
|---|---|---|---|
| `redo_booking_other` | 120 | 177 | 68% |
| `redo_desc_about` | 116 | 491 | 24% |
| `redo_desc_check_in` | 87 | 128 | 68% |
| `redo_booking_check_in` | 83 | 120 | 69% |
| `redo_desc_requirements` | 65 | 221 | 29% |
| `redo_booking_important_info` | 62 | 101 | 61% |
| `redo_desc_other` | 61 | 235 | 26% |
| `redo_desc_what_included` | 58 | 314 | 18% |
| `redo_desc_itinerary` | 46 | 122 | 38% |
| `redo_booking_inclusions` | 28 | 92 | 30% |
| `redo_desc_what_excluded` | 25 | 134 | 19% |
| `redo_booking_what_to_bring` | 25 | 192 | 13% |
| `redo_desc_what_to_bring` | 24 | 161 | 15% |
| `redo_booking_contact` | 19 | 94 | 20% |
| `redo_booking_before_arrival` | 15 | 51 | 29% |
| `redo_desc_highlights` | 12 | 128 | 9% |
| `redo_booking_departure_info` | 12 | 117 | 10% |
| `redo_booking_location` | 11 | 117 | 9% |
| `redo_min_age` | 10 | 134 | 7% |
| `redo_desc_duration_text` | 10 | 431 | 2% |
| `redo_meeting_point` | 9 | 251 | 4% |
| `redo_desc_cancellation` | 7 | 80 | 9% |
| `redo_booking_itinerary` | 6 | 15 | 40% |
| `redo_booking_what_not_to_bring` | 6 | 29 | 21% |
| `redo_max_age` | 5 | 41 | 12% |
| `redo_booking_cancellation` | 5 | 29 | 17% |
| `redo_group_size` | 2 | 127 | 2% |
| `redo_booking_faqs` | 1 | 1 | 100% |

## Model agreement with the majority

| model | verdicts | matched majority | parse failures | flag rate |
|---|---|---|---|---|
| gpt-5.5-pro | 4133 | 100.0% | 0 | 22.5% |
