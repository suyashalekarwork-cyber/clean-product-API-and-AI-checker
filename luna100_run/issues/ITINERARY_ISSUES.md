# Itinerary — Issue List

**Field:** `redo_desc_itinerary`, description side only
**Current run:** V4.8.1, gpt-5.6-luna, 100 products, 166/166 responses, 0 failures
**Result:** 13 products have an itinerary. **9 correct, 4 with defects.**

**Definition (FINAL):** an itinerary is

> **day-wise** or **time-wise**, describing what happens during the experience.

Extracted **whole** — wordy rows and description lines included. Post-processing
converts it into a display-ready panel later; the job now is to get the right
*blocks* into the right field, not to make them pretty.

An activity list with **no day and no time marker** is **Highlights**, not an
itinerary.

---

## Decision log — settled, do not re-litigate

| # | Decision | Date |
|---|---|---|
| D1 | ~~Itinerary = day/time + place, short rows only~~ **superseded by D11** | 2026-08-10 |
| D2 | Minimum 2 marked entries, not 3 | 2026-08-10 |
| D3 | 24-hour times (`16h00`, `14:30`) count as clock times | 2026-08-10 |
| D4 | No time-format conversion — breaks the VERBATIM RULE. Code pass later if wanted | 2026-08-10 |
| D5 | Non-English products extracted as-is, flagged only. Translation out of scope | 2026-08-10 |
| D6 | Rejected text goes to `redo_desc_about` **whole and untrimmed**. Never deleted | 2026-08-10 |
| D7 | ~~No trimming: a long row sends the whole field to About~~ **REVERSED by D11** | 2026-08-10 |
| D8 | Booking side (`redo_booking_itinerary`) out of scope this round | 2026-08-10 |
| D9 | ~~709572 rejected as narrative~~ **REVERSED by D11 — it is day-wise, keep it** | 2026-08-10 |
| D10 | 559785 (Heli) — correctly emptied. Raw source shows it under `Operating from:` — an operating-hours block | 2026-08-10 |
| D11 | Itinerary = day-wise or time-wise. Extract WHOLE, no length test, no trimming | 2026-08-10 |
| D12 | A short label before the time still counts — `Boarding: 11:30 am Parsley Bay` is a time-wise row | 2026-08-10 |
| **D16** | **550275 has NO itinerary.** Its raw text is a cruise ad -- price, boarding/disembarking times, nearest train station, buffet contents, group discounts. `Boarding: 11:30 am / Disembarking: 2:00pm` is departure/return info, not a route. V4.8.3 emptying it is CORRECT, not a regression. **Narrows D12** -- a labelled time is not automatically an itinerary row | 2026-08-10 |
| D13 | A numbered sequence IS an itinerary. It does NOT have to name a venue on every row. 453100 and 585533 are both correct. **Narrowed by D14** | 2026-08-10 |
| **D14** | **A numbered list whose rows are the SAME wording differing only by a counter (`cellar door 1..4`) is a placeholder, not an itinerary.** Rows must be distinct from one another. 675102 → About. Does NOT affect 453100 or 585533, whose rows are distinct | 2026-08-10 |

**What D13 settles:** "with places" in D11 was never a requirement that each row
name a venue. The real test is whether the rows form an **ordered sequence of what
happens during the experience**. A numbered list qualifies; a bulleted list of
adjectives does not.

---

## REVIEWER VERDICTS — from `section_review.xlsx`, 2026-08-10

Marked by Suyash against the raw text, on the V4.8.2 run.

| Product | Verdict | Comment |
|---|---|---|
| 382277 | **fail** | — (agrees with ISSUE-2) |
| 675102 | **fail** | *"fail to extract"* |

FAQ is tracked separately in `FAQ_ISSUE.md` — not an itinerary issue.

---

### ISSUE-11 · Placeholder "cellar door 1..4" is not a real itinerary · NEW

**Product:** 675102 (marlboroughjadetours) · **Type:** Prompt · **Priority:** HIGH
**Raised by:** Suyash, reviewer verdict `fail — "fail to extract"`

```
1. Pickup at 12:30 pm
2. Visit and tasting at cellar door 1
3. Visit and tasting at cellar door 2
4. Visit and tasting at cellar door 3
5. Visit and tasting at cellar door 4
6. Return between 4:00-4:30 pm
```

The supplier labelled this `itinerary:` and it is correctly numbered, so every
structural rule passes it. But rows 2-5 are **the same row repeated four times
with a counter**, and no winery is ever named. It carries no information a
customer can use — "cellar door 1" is a placeholder, not a destination.

**This REVERSES D13 for this shape.** D13 settled that a numbered sequence need
not name a venue on every row — that was decided on 453100
(`1. Oyster Tasting / 2. Farm Cruise`) and 585533 (`3. Mt Tokatea Wero /
4. Return trip to Coromandel Town`), both of which name *distinct activities or
places* per row. 675102 is different: the rows are not distinct from each other.

**The distinction to encode:**

| | |
|---|---|
| ✅ Keep — rows differ from one another | `1. Oyster Tasting - 30 minutes` / `2. Farm Cruise - 1 hour` |
| ✅ Keep — rows name real places | `3. Mt Tokatea Wero` / `4. Return trip to Coromandel Town` |
| ❌ Reject — rows are one row with a counter | `2. Visit and tasting at cellar door 1` … `5. …cellar door 4` |

**Proposed rule:** if the middle rows are the same wording differing only by a
number, the list is a placeholder and not an itinerary. Send it to
`redo_desc_about`.

**Watch for:** this is a narrow rule and must not catch 453100 or 585533, which
Suyash has confirmed are correct. Verify both on the next run.

---

## OPEN DEFECTS — 4 products

### ISSUE-2 · Booking admin extracted as an itinerary

**Product:** 382277 (executivecarservice) · **Type:** Prompt · **Priority:** HIGH
**Regression:** V4.8 rejected this correctly; V4.8.1 let it back in.

```
1. Park your vehicle in our dedicated valet car parks, located at the back left
   in the rental car park.
2. Drop your keys in the last-minute key drop sandwich board located at the
   departure gates.
3. Your car will be parked in our secure indoor storage facility at 77 Airport Ave.
4. We will bring your vehicle to the drop-off zone when your flight lands.
```

Airport parking instructions, not a tour. Confirmed by Suyash: *"this is not real
itinerary, its good that 4.8.1 has not extracted"* — the intent is agreed even
though the run shows the opposite.

**Cause:** the CONTENT TEST (*"parking, key drop-off … are NOT an itinerary"*) sits
**below** the qualifying rules in the V4.8.1 prompt. Rule (b) — "2+ entries start
with `1.` `2.`" — fires first and wins.

**Fix:** move the CONTENT TEST **above** the qualifying rules so it gates them.

---

### ISSUE-3 · Raw `itinerary:` label leaked into the value

**Product:** 691267 (reptileencounters) · **Type:** Prompt · **Priority:** HIGH
**New in V4.8.1.**

```
V4.8    "1. Arrival at HQ in Burwood (2 Leslie Ct) at 9:30 AM."
V4.8.1  "itinerary: 1. Arrival at HQ in Burwood (2 Leslie Ct) at 9:30 AM."
         ^^^^^^^^^^ structural syntax, would print literally on the page
```

**Cause:** the new `COPY THE BLOCK WHOLE` instruction. The model read "whole" as
including the source label.

Same defect class as the manager review's Defect 10 (`min_age:` appearing inside
Requirements).

**Fix:** *"The `itinerary:` label itself is not content. Emit only what follows it."*

---

### ISSUE-7 · Departure timetable extracted as an itinerary

**Product:** 678270 (railcars) · **Type:** Prompt · **Priority:** HIGH
**Raised by Suyash.**

```
Railcar Departs Napier
- 9:30am
- 10:35am
- 12:10pm
- 1:15pm
- 2:20pm
```

Five **departure times for the same service** — a timetable telling you when you
can catch the railcar. Not five stops on one journey. A customer reading the
Cruise Route panel would think the tour visits five places.

Same category as 559785's operating-hours block (D10), in list form.

**Cause:** every row starts with a clock time, so it passes rule (a) cleanly.
Structure alone cannot tell a *timetable* from a *schedule*.

**Fix:** a list of **bare times with no event on the row** is a timetable, not an
itinerary. An itinerary row pairs a time with *what happens at that time*.
678270 is the only product in the sample with bare-time rows, so this test is
precise and low-risk.

---

### ISSUE-9 · Merged row no longer split

**Product:** 585533 (matarikitours) · **Type:** Prompt · **Priority:** LOW
**Regression from V4.8.**

```
V4.8    3. Mt Tokatea Wero, Powhiri, Kaikorero, Presentation
        4. Return trip to Coromandel Town                        <- 4 rows, correct
V4.8.1  3. Mt Tokatea Wero, Powhiri, Kaikorero, Presentation 4. Return trip to
        Coromandel Town                                          <- 3 rows, merged
```

The supplier's own text is missing a line break. V4.8 fixed it; V4.8.1 undid the
fix because `COPY THE BLOCK WHOLE` told it not to alter anything.

**Arguably correct under D11** — post-processing can split on `N.` markers.
Low priority. The product itself is confirmed an itinerary under D13.

---

## JUDGEMENT CALL — 1 product

### ISSUE-10 · Single-venue event programme

**Product:** 659457 (splittersfarm) · **Type:** Decision

```
5:30pm - Pumpkin Toss/games & attractions
6pm - LIVE music Abby Skye & The Batman
7pm - Red Carpet Best Dressed
7:45pm-10pm LIVE music Abby Skye & The Batman
```

A real timed schedule — time + what happens on every row — but it is an **event
programme at one venue**, with no travel between places. Is that a "route" for the
Cruise Route panel, or a schedule of a single-location event?

Currently **kept**. Passes D11 as time-wise. No action unless you want it out.

---

## CODE — no prompt can fix these

### ISSUE-5 · Itinerary duplicated into About

**Products:** 675102 (63% overlap), 666061 (64%) · **Priority:** Medium

The same route stored in both `redo_desc_itinerary` and `redo_desc_about`, so the
page prints it twice.

**Confirmed not fixable by tightening the itinerary definition** — both qualify via
rules (a)/(b). The NO DUPLICATION RULE already exists and is being disobeyed;
hard30 §4 measured luna producing 16 duplicate sentences with that rule active, 10
involving `desc_about`. A V4.8.1 reminder line was added and did not fix it.

**Wider finding:** a full-output audit found **33 duplicate pairs across 26
products**, not just these two — worst cases 529363 (100% About ↔ What's Included),
509794 (100% What's Included ↔ Duration), 458669 (92%). Duplication is a bigger
quality problem than anything left in the itinerary field.

---

### ISSUE-6 · Same itinerary in the description and booking boxes

**Products:** 288725, 382277, 453100, 556466, 675102 · **Status:** out of scope (D8)

```
453100  Itinerary:          1. Oyster Tasting  2. Farm Cruise
        Booking: Itinerary: 1. Farm Cruise     2. Oyster Tasting
```

Same tour, **opposite order**, one page. Two separate API calls that never see each
other's output. Needs a dedup pass that also reconciles ordering conflicts.

---

## CLOSED

| Issue | Products | Resolution |
|---|---|---|
| **ISSUE-1** | 453100, 585533 | **Closed by D13** — numbered sequences are itineraries |
| **ISSUE-8** | 675102 | **Closed by D13** — `cellar door 1..4` is a numbered sequence; placeholder names do not disqualify it |
| **ISSUE-4** | 288725, 550275, 738691, 691267, 574647, 666061 | Closed by D11 — no field-length test |

---

## Product-by-product review — V4.8.1, all 13 with an itinerary

| # | Product | Supplier | Verdict |
|---|---|---|---|
| 1 | 659457 | splittersfarm | ⚠️ judgement — single-venue event programme (ISSUE-10) |
| 2 | 678270 | railcars | ❌ **timetable, not an itinerary** (ISSUE-7) |
| 3 | 550275 | thefloatingoysterwinebar | ✅ `Boarding: 11:30 am Parsley Bay Wharf / Disembarking: 2:00pm` |
| 4 | 738691 | izzytogo | ✅ 6 timed rows + descriptions, French, kept whole |
| 5 | 675102 | marlboroughjadetours | ✅ per D13 — but duplicated into About (ISSUE-5) |
| 6 | 382277 | executivecarservice | ❌ **airport parking admin** (ISSUE-2) |
| 7 | 691267 | reptileencounters | ❌ **`itinerary:` label leaked into value** (ISSUE-3) |
| 8 | 509794 | sydneyprincesscruises | ✅ `Embarkation: 10:15 am Eastern Pontoon / Disembarkation: 2.00 pm` |
| 9 | 288725 | cairnsaquarium | ✅ 3 timed rows, schedule line correctly stripped |
| 10 | 574647 | wavessurfschool-au | ✅ `Night 1 / Day 1 / Night 2 / Day 2` |
| 11 | 585533 | matarikitours | ⚠️ correct itinerary, rows 3–4 merged (ISSUE-9) |
| 12 | 453100 | pearlsofaustralia | ✅ per D13 |
| 13 | 709572 | onestepadventures | ✅ per D9/D11 — day-wise, kept whole |

### Correctly emptied — 4 products

| Product | What was removed | Why correct |
|---|---|---|
| 186343 | `Chill beach intro + simple ocean safety rundown` … | Activity list, no day/time marker |
| 709179 | `Safety briefing and trip overview` … | Activity list, no day/time marker |
| 714769 | `Meet your crew and receive a full safety briefing` … | Activity list, no day/time marker |
| 666061 | `Relaxed afternoon touring through Marlborough wine country` … | Activity list, no day/time marker |

---

## Verified clean across all 100 products

| Check | Result |
|---|---|
| **Invented content** | **0 cases**, all fields |
| **Text deleted** | **0 rows** — everything moved to About survives at 100% |
| **Content loss vs raw source** | 1 product (598043), 7 words |
| **Parse failures** | 1 product (459312) — truncated JSON, retry not a prompt change |

---

## V4.8.2 scope

| Fix | Issue | Products |
|---|---|---|
| Move CONTENT TEST **above** the qualifying rules | ISSUE-2 | 382277 |
| `itinerary:` label is not content | ISSUE-3 | 691267 |
| Bare-time list = timetable, not an itinerary | ISSUE-7 | 678270 |
| *(optional)* split a merged `N.` row | ISSUE-9 | 585533 |

**Expected:** 13 → 11 itineraries, with 691267 cleaned. All four are pattern rules,
not judgement calls.

**Not in scope:** ISSUE-5 and ISSUE-6 (code), ISSUE-10 (your decision).

### Verification for the V4.8.2 run
1. 382277 and 678270 empty, text present in About
2. 691267 starts `1. Arrival at HQ`, no `itinerary:` prefix
3. The other 10 itineraries unchanged — no collateral movement
4. Zero invented words, zero text lost

---

## Known tooling bug — fixed, but affects saved files

`itinerary_v4_8_1_review.xlsx` generated before this fix has **swapped column
headers**: the column labelled `V4.8.1 itinerary` holds V4.8's data and vice
versa. Caused by a rename collision (`V4.7 itinerary` → `V4.8 itinerary` where a
`V4.8 itinerary` column already existed). This produced two rounds of confusion
where a product appeared to regress when it had not.

**Use `itinerary_BEFORE_vs_AFTER.txt`** — built straight from the raw `.jsonl`
files, so the labels cannot be wrong. Regenerate the xlsx once Excel releases the
file lock.
