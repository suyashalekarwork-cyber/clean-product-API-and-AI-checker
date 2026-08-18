# Issues to review

Everything still open, in one list. Checked against the raw supplier text on the
V4.8.3 run (`output/luna100_v4_8_3_output.jsonl`).

**11 of 14 automated checks pass.** What follows is the other 3, plus the things
no automated check covers.

**How to see any of these yourself:** open
[`reports/section_review.xlsx`](reports/section_review.xlsx), go to the sheet
named in the table, and filter `product_id`. The raw supplier text sits in the
same row.

---

## Needs a decision from you — 2

### D-1 · 659457 — a timed schedule at a single venue

**Sheet:** `Itinerary` · **Currently:** kept

```
5:30pm - Pumpkin Toss/games & attractions
6pm - LIVE music Abby Skye & The Batman
7pm - Red Carpet Best Dressed
7:45pm-10pm LIVE music Abby Skye & The Batman
```

Every row has a time and an event, so it passes every rule. But it is an **event
programme at one venue** — nothing travels anywhere. Is that an itinerary for the
Cruise Route panel, or a schedule of a single-location event?

**If you say it is not an itinerary,** the rule needs to require movement between
places, which would also affect any future single-venue product.

### D-2 · 559785 — two boarding times, no route

**Sheet:** `Itinerary` · **Currently:** kept, and this reverses an earlier call

```
Heli boarding at 10.15am.
Heli departure at 11.30am.
```

In the raw text this sits under **`Operating from: Saturday November 9, 2024 to
Monday April 21, 2025`** — an operating-hours block. It was correctly emptied in
earlier versions and came back in V4.8.3.

Two time-marked entries, so it meets the two-entry minimum. The question is
whether boarding + departure times constitute an itinerary at all.

*(This is the same shape as 550275, which you confirmed is **not** an itinerary —
so the answer is probably no, but it was decided the other way once already and
is worth stating explicitly.)*

---

## Needs a prompt change — 3 products

### P-1 · 382277 — airport parking published as a tour route

**Sheet:** `Itinerary` · **Priority: HIGH**

```
1. Park your vehicle in our dedicated valet car parks
2. Drop your keys in the last-minute key drop sandwich board
3. Your car will be parked in our secure indoor storage facility
4. We will bring your vehicle to the drop-off zone when your flight lands
```

Airport parking instructions, not a tour. The rule that should catch this exists —
*"parking, key drop-off and other booking admin are NOT an itinerary"* — but it
sits **below** the rule that lets numbered lists through, so the numbered-list
rule wins.

**Fix:** move the content test above the qualifying rules. One-line reorder.

### P-2 · 675102 — placeholder rows

**Sheet:** `Itinerary` · **Priority: MEDIUM**

```
1. Pickup at 12:30 pm
2. Visit and tasting at cellar door 1
3. Visit and tasting at cellar door 2
4. Visit and tasting at cellar door 3
5. Visit and tasting at cellar door 4
6. Return between 4:00-4:30 pm
```

Rows 2–5 are one row repeated four times with a counter. No winery is ever named,
so it carries nothing a customer can use.

**Fix:** if the middle rows are identical apart from a number, treat the list as a
placeholder. **Must not catch** 453100 or 585533, which you confirmed are correct.

### P-3 · 252851 — What's Included filled with no supplier heading

**Sheet:** `Whats_Included` · **Priority: MEDIUM**

Value is `Local English-speaking guide`, and the raw text has **no inclusions
heading anywhere**. The rule says no heading means no extraction. This is the one
gating miss in 100 products.

---

## Needs code, not prompt wording — cannot be fixed by editing the prompt

### C-1 · The same sentence stored in two fields — 26 products

**Priority: HIGH — this is the largest remaining defect on the description side.**

The page prints the same sentence twice. Worst cases:

| Product | Overlap | Fields |
|---|---|---|
| 529363 | 100% | About ↔ What's Included |
| 509794 | 100% | What's Included ↔ Duration |
| 458669 | 92% | About ↔ What's Included |
| 639308 | 90% | What's NOT Included ↔ What to Bring |
| 678270 | 90% | About ↔ What's Included |

All 26: `382277, 453100, 458669, 509794, 510317, 529363, 574647, 625744, 639308,
663995, 666061, 675102, 678270, 691267, 709179, 709572, 710027, 714769, 716074,
719421, 737911, 738691`

**Three prompt versions have tried and failed.** The rule exists — *"extracting is
moving text, not copying it"* — and is being ignored. Needs a de-duplication pass
after extraction.

### C-2 · Same itinerary in the description and booking sections — 5 products

```
453100   Itinerary:          1. Oyster Tasting   2. Farm Cruise
         Booking: Itinerary: 1. Farm Cruise      2. Oyster Tasting
```

Same tour, **opposite order**, one page. `288725, 382277, 453100, 556466, 675102`.

The two sections are filled by two separate API calls that never see each other's
output, so no wording can reach this.

### C-3 · Occasionally malformed output — 1–2 products per run

The model sometimes closes its JSON with a stray `,"` before the brace:

```
..."redo_desc_other":"If you book Launch and Retrieve.","}
                                                       ^^^ invalid
```

Different products each run — V4.8.1 hit 459312; V4.8.3 hit 493762 and 317691.
A sampling artefact, not a prompt defect.

`review_output.py` and `export_extracted.py` repair this on load and report which
products were affected. **Left unrepaired those products vanish from every report
with no warning** — that is how one correct extraction was briefly mis-reported
as data loss.

---

## Not yet reviewed — no work done on these fields

Only three fields have been worked through. These have never been checked against
the raw text:

- Highlights
- What's NOT Included
- Cancellation policy
- Check-in / Meeting point
- Duration / Min age / Max age / Group size
- **The entire booking-notes side** (13 fields)

The booking prompt has been unchanged since V4.7, held constant on purpose so
description-side changes stayed attributable.

---

## One larger question behind several of these

**Should a field be filled when the supplier never wrote a heading for it?**

Settled for What's Included — heading required. Not settled anywhere else. Two
documents in the wider project still say opposite things:

| Says | |
|---|---|
| The prompt | *"Split it line by line and route each line to its correct field"* |
| The mapping-rules doc | *"Extract a section only when the supplier gave it a heading"* |

It affects roughly a quarter of all filled fields. Worth settling before the
remaining sections are worked through, or the same argument will repeat for each
one.

---

## Summary

| Type | Count | Who |
|---|---|---|
| Needs your decision | 2 products | You |
| Needs a prompt change | 3 products | Prompt edit, one run to verify |
| Needs code | 3 issues, 26+ products | Python, post-processing |
| Fields not yet reviewed | 6 areas | Next sessions |

**Suggested order:** settle the two decisions, ship one prompt version covering
all three prompt fixes, then the de-duplication pass — it affects more products
than everything else combined.
