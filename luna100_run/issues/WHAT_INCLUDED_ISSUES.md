# What's Included — Rules and Issue List

**Field:** `redo_desc_what_included`, description side only
**Run checked:** V4.8.2 (`luna100_v4_8_2_output.jsonl`), 100 products
**Reference:** the RAW supplier text only. No prompt-version comparison.

---

## THE RULES — decided by Suyash, 2026-08-10

### WI-R1 · Heading-gated. No heading, no extraction.

Fill this field **only** when the raw text has a heading that announces an
inclusions list. With no such heading, the field stays **empty** and the text
stays in `redo_desc_about`.

### WI-R2 · A heading means the word OR any synonym

Not just the literal phrase "what is included". A heading qualifies if it
contains an inclusion word anywhere in the line:

> `include` · `included` · `includes` · `inclusions` · `inclusive` ·
> `provided` · `provides` · `we provide` · `we supply` · `supplied` ·
> `you get` · `comes with`

**All of these are real headings found in the data and all must count:**

| Form | Real example | Product |
|---|---|---|
| Embedded label | `what_is_included:` | 637564 |
| Markdown | `##Includes` · `##What's included:` · `##Inclusive` | 470304, 364822, 506018 |
| Extra words around the word | `##Swag package Inclusions:` · `###INCLUDED on ALL Fishing Charters` | 587626, 535701 |
| Noun before it | `Buffet Includes:` · `##Package Inclusions:` | 550275, 74565 |
| Bold | `**Price Include:**` | 270858 |
| Plain line, no markers | `What's Included` · `What's provided:` | 458669, 201040 |
| Sentence ending in a colon that announces a list | `We will provide you with the following when you arrive for your lesson:` | 317691 |

**A line ending in a colon that announces a list IS a heading.** Confirmed by
Suyash.

### WI-R3 · Check the content under the heading — do not take the block blindly

A supplier's inclusions heading often contains lines that are **not** inclusions.
Read each line and route it to its proper field. **Never delete it** — every line
goes somewhere.

### WI-R4 · Leftovers go to About

Anything under the heading that belongs to no specific field stays in
`redo_desc_about`. Nothing is dropped.

### WI-R5 · Extract only what is CLEARLY included

Decided by Suyash: *"this does not look like inclusion so for now lets just
extract what is clearly visible"*.

A line qualifies only if it states something the customer **definitely** gets.
**Conditional availability is not an inclusion** — `X is available`,
`we can supply X if you do not have your own`, `X if required`, `we have spare X`
describe what the operator *can* provide on request. Those go to
`redo_desc_about`.

This applies **row by row**, even inside a validly-headed list. 317691 keeps
`Stand Up Paddleboard / Paddle / Rash Shirt / Sunscreen / Professional
Instruction` and loses `PFD's are available` and `Wetsuit if required`.

### WI-R6 · Repetition in the source does not license repetition in the output

Approved by Suyash. Appended to the NO DUPLICATION RULE — see WI-3.

---

## Measured impact of WI-R1 + WI-R2

| | |
|---|---|
| Filled today | 56 of 100 |
| **Keep** — a heading or synonym is present | **41** |
| **Empty → text moves to About** | **15** |

Without the synonym list (WI-R2) the cut would have been 21 products. Six were
saved by synonyms alone: 587626, 74565, 535701, 201040, 550275, 317691.

---

## OPEN ISSUES

### WI-1 · Content under an inclusions heading that is not an inclusion
**Priority: MEDIUM** · **7 products** · raised by Suyash
**Do not remove the content — route it correctly.**

The model already handles most of these well. Recorded so the behaviour is
protected rather than accidentally broken by a future edit, and so the misses are
visible.

| Product | Heading | Line that is not an inclusion | Went to | OK? |
|---|---|---|---|---|
| 637762 | `what_is_included:` | prices, child rates, infant policy, sole-occupancy rates | `other`, `requirements` | ✅ |
| 659457 | `what_is_included:` | `5:30pm - Pumpkin Toss`, `6pm - LIVE music`, `7pm - Red Carpet` | `itinerary` | ✅ |
| 419095 | `what_is_included: ## We do Supply` | `Please arrive 15 minutes prior to the start` | `check_in` | ✅ |
| 364822 | `##What's included:` | `Wine tasting fees are payable on the day and not included` | `what_excluded` | ✅ |
| 550275 | `Buffet Includes:` | `Additional wine, spirits & cocktails can be purchased for...` | `what_excluded` | ✅ |
| 506018 | `##Inclusive` | `Private Events require a minimum 8 people.` | `requirements` | ✅ |
| 186343 | `Wetsuit and Surfboard provided!` | `2-Hour Surf Lesson – What You Can Expect` | `about` | ✅ |

**All 7 currently route correctly.** The risk is a future heading-gating edit
telling the model to "take the block under the heading", which would pull prices,
itinerary rows and exclusions into What's Included. The rule must say *check each
line*, not *take the block*.

---

### WI-2 · Conditional availability filed as a guaranteed inclusion
**Priority: HIGH** · **4 products** · raised by Suyash on 459312

*"can supply … if you do not have your own"* is **availability**, not something
the booking includes.

| Product | Extracted into What's Included | Sits under |
|---|---|---|
| **459312** | `Arion Riding Centre can supply helmets and riding boots if you do not have your own.` | `##Clothing Requirements` |
| 510317 | `We have everything you need. If you don't have roof racks, that's ok, we have portable ones` | `##Pick up only` |
| 529363 | `We can supply tables so you can set yourself up for the cruise.` | no heading |
| 317691 | `PFD's are available` · `Wetsuit if required (or you can bring your own)` | `We will provide you with the following:` |

**459312 is the clearest.** The supplier wrote seven sentences under
`##Clothing Requirements`; six went to Requirements and this one was pulled out.

**WI-R1 fixes three of the four** — 459312, 510317 and 529363 have no inclusions
heading, so heading-gating empties them. **317691 survives** because its list *is*
under a valid heading, and two of its seven rows are conditional.

**Decided:** conditional rows are filtered out to About (WI-R5). 317691 loses 2
of its 7 rows; the other 5 stay.

---

### WI-3 · Same sentence emitted into two fields
**Priority: MEDIUM** · **1 product**

509794 — `3.5 hrs cruising the beautiful Sydney Harbour waterways` appears in both
`duration_text` and `what_included`. The supplier wrote it **twice** in the source
(once under `**Duration**`, once in the inclusions list), so the model routed each
occurrence and the page prints it twice.

Proposed wording, appended to the NO DUPLICATION RULE:

```
REPETITION IN THE SOURCE DOES NOT LICENSE REPETITION IN THE OUTPUT. If the same
sentence appears MORE THAN ONCE in the raw text, it is still ONE sentence and
belongs in EXACTLY ONE output field. Emit it once, in the most specific field.
This applies ONLY when the wording is IDENTICAL -- two different sentences
describing the same thing are not duplicates and both are kept.
```

The second half protects 458669, where the supplier wrote a prose paragraph *and*
a separate bullet list covering the same items — different sentences, both correct
to keep.

---

## DECIDED — conditional rows are filtered out (was open)

**Option B chosen.** Under a valid inclusions heading the list is read **row by
row**; conditional rows go to About.

317691 keeps 5 of its 7 rows:

```
Stand Up Paddleboard          KEEP
Paddle                        KEEP
PFD's are available           -> About   (conditional)
Rash Shirt                    KEEP
Wetsuit if required           -> About   (conditional)
Sunscreen                     KEEP
Professional Instruction      KEEP
```

**Risk to watch:** this is a row-level rule, and row-level rules are where the
model has been least consistent. Verify on the next run that no validly-headed
list loses a genuine inclusion.

---

## NOT DEFECTS — checked and cleared, do not re-raise

### 458669 — supplier wrote it twice, correctly
Raised as a duplicate, withdrawn. The supplier wrote a prose paragraph
(`Enjoy a reserved table for your group, cold drinks from the bar...`) **and** a
separate `What's Included` bullet list. Different sentences. Both kept. Correct.

### Supplier-mislabelled blocks, correctly re-routed
637762, 625744, 419423, 419095, 659457 — see WI-1. The model overrides a wrong
supplier label with the right destination and does it well.

### Exclusions correctly split out of an inclusions block
364822, 252851, 690572 — *"not included"*, *"additional cost"*,
*"purchased additionally"* all reached `what_excluded`.

### Empty labels
598043, 661870 carry `what_is_included:` with nothing after it. Empty is correct.

---

## Verified clean across all 100 products

| Check | Result |
|---|---|
| Invented words not in the raw source | ✅ 0 |
| Label marker emitted as content | ✅ 0 |
| Exclusion language misfiled as an inclusion | ✅ 0 |
| Items dropped from a labelled inclusions list | ✅ 0 |

---

## Method note — two corrections I had to make

**1.** I first reported this section as clean with 1 defect. That was wrong. My
checks only covered products where the raw had an inclusions heading; the 21
filled by classification alone I validated by eyeballing four. Suyash opened one
(459312) and found a defect. **Check every product in a category or state that you
did not.**

**2.** My first heading detector found only 9 headings because it required the
heading to end its line. The real count is 41. A detector that under-counts makes
a rule look far more destructive than it is — the first impact estimate I showed
was 56 → 9, then 56 → 35, and the true figure is 56 → 41.
