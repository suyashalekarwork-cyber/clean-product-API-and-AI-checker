# Section Status — current run vs RAW

Checked against the **raw supplier text** only. No prompt-version comparison.

**Run:** `luna100_v4_8_3_output.jsonl` · 100 products · 0 parse failure(s)

## Scorecard

| Section | Check | Status | Failing | Products |
|---|---|---|---|---|
| ITINERARY | Prose accepted via 'then'/'next' | ❌ FAIL | 1 | 559785 |
| ITINERARY | Selling-point list accepted | ✅ PASS | 0 |  |
| ITINERARY | Booking admin accepted | ❌ FAIL | 1 | 382277 |
| ITINERARY | Bare-time timetable accepted | ✅ PASS | 0 |  |
| ITINERARY | Opening hours inside the field | ✅ PASS | 0 |  |
| ITINERARY | Raw label emitted as content | ✅ PASS | 0 |  |
| ITINERARY | Two numbered steps merged | ✅ PASS | 0 |  |
| ITINERARY | Real plan missed | ❌ FAIL | 1 | 550275 |
| ITINERARY | Invention | ✅ PASS | 0 |  |
| FAQ | FAQ block not captured | ✅ PASS | 0 |  |
| FAQ | Question dropped | ✅ PASS | 0 |  |
| FAQ | Question scattered to another field | ✅ PASS | 0 |  |
| FAQ | Invention | ✅ PASS | 0 |  |

## Section totals

| Section | Reviewed | Clean | With an issue |
|---|---|---|---|
| Itinerary | 13 | 10 | 3 |
| FAQ | 2 | 2 | 0 |

## Open issues

- **382277** (ITINERARY) — booking admin, not the experience
- **550275** (ITINERARY) — raw looks like it HAS a day/time plan - check for a miss
- **559785** (ITINERARY) — no day/time marker on 2+ rows

## Next sections to work through

- [ ] Highlights
- [ ] What's Included / What's NOT Included
- [ ] Cancellation policy
- [ ] Check-in / meeting point
- [ ] Duration / age / group size

_Add a section here as it is picked up; the Checks sheet grows with it._