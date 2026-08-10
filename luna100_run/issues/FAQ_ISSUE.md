# FAQ Block Shredded Across Six Fields

> **STATUS: FIXED and confirmed by Suyash, 2026-08-10 (V4.8.2 run).**
> New field `redo_desc_faqs` added. 9/9 questions land there and nowhere else;
> no FAQ text remains in cancellation / what_to_bring / what_excluded /
> requirements. A second product (391646) was also picked up. Reviewer marked
> no failures on the FAQ sheet.

**Product:** 606496 (zombieland) · **Field:** description side · **Type:** PROMPT
**Status:** confirmed present in V4.8.1 · **Scale:** ~3,100 products at full catalogue

---

## The issue in one line

A supplier wrote one `faqs:` block containing **9 questions with their answers**.
The model scattered it across **6 different fields**, so the website would print
FAQ answers under Cancellation Policy, What to Bring and What's NOT Included —
and one question vanished entirely.

---

## What the supplier wrote

```
faqs: Do you have EFTPOS?
      Yes we have EFTPOS onsite. We also accept cash.

      Do you still run games in the rain?
      YES! Paintball and Slingshot will always run even if it's raining...

      I have a voucher from Zombieland, when can it be used?
      Vouchers are able to be used on Mondays, Tuesdays...

      What should I wear to my booking?
      At Zombieland ALL of our activities are outdoors...

      ... 5 more question/answer pairs
```

One labelled block. 9 questions. Each answer belongs to the question above it.

## Where each question landed

| Question | Field it ended up in |
|---|---|
| Do you have EFTPOS? | `redo_desc_other` (question text **dropped**, answer kept) |
| Do you still run games in the rain? | ❌ `redo_desc_cancellation` |
| I have a voucher, when can it be used? | `redo_desc_other` |
| What should I wear to my booking? | ❌ `redo_desc_what_to_bring` |
| What happens if I damage the equipment? | `redo_desc_other` |
| What if I turn up with fewer players? | `redo_desc_other` |
| Can I bring alcohol? | `redo_desc_other` |
| Do you have a BBQ at Zombieland? | ❌ `redo_desc_what_excluded` |
| What do I do if I'm late? | ❌ `redo_desc_check_in` |

**Six fields are now majority-FAQ content:**

| Field | % of its words from the FAQ block |
|---|---|
| `redo_desc_what_to_bring` | **100%** |
| `redo_desc_cancellation` | **100%** |
| `redo_desc_other` | 99% |
| `redo_desc_check_in` | 89% |
| `redo_desc_requirements` | 83% |
| `redo_desc_what_excluded` | 79% |

## Why this is worse than "untidy"

**1. The Cancellation Policy is not a cancellation policy.**
```
redo_desc_cancellation:
  "Do you still run games in the rain?
   YES! Paintball and Slingshot will always run even if it's raining..."
```
A customer opening Cancellation Policy gets a weather FAQ. The actual refund
terms are not there.

**2. What's NOT Included says a BBQ is excluded — it isn't.**
```
redo_desc_what_excluded:
  "Do you have a BBQ at Zombieland?
   Yes we do! If you want to use our BBQ you must reserve it at the time of
   booking, the fee is $25.00"
```
The answer is **yes, for $25**. Filed under exclusions, it reads as "no BBQ".
This is the same failure class as Defect 9 in the manager review (663995's
orchards).

**3. A question was silently deleted.**
`"Do you have EFTPOS?"` does not appear in any output field. Its answer
(`"Yes we have EFTPOS onsite. We also accept cash."`) survives in
`redo_desc_other`, orphaned — an answer with no question.

**4. Raw label markers leaked in.**
`redo_desc_requirements` begins `min_age: 12` — structural syntax printed as
prose. Same defect as ISSUE-3 on 691267 (`itinerary:` leaking).

---

## Root cause

Two rules in the prompt contradict each other, and the wrong one wins.

| Rule | Line | Says |
|---|---|---|
| LABEL MAPPING | ~70 | `faqs:` → `redo_desc_other`, and the mapping "is authoritative and overrides your own judgment" |
| SPLIT WITHIN SECTION | ~144 | "A single labeled section … may contain content belonging to several different fields. Never place a whole mixed block into one field. **Split it line by line and route each line to its correct field.**" |

An FAQ block is *exactly* what SPLIT WITHIN SECTION describes — one labelled
section whose lines are topically mixed. So the model obeys it and scatters the
block. **No tie-break is stated**, and SPLIT WITHIN SECTION is the more specific
instruction, so it wins.

This is the model doing what it was told. It is not a model-quality problem and no
model upgrade will fix it.

---

## The fix

Append to the `redo_desc_other` definition:

```
FAQ INTEGRITY: a question and its answer are a single unit and must never be
separated. When the raw text contains a "faqs:" label or an FAQ / Q&A heading,
the ENTIRE block -- every question together with its own answer -- goes to this
one field, in source order. The SPLIT WITHIN SECTION RULE does NOT apply to an
FAQ block. Never drop a question and keep only its answer.
```

**Why it goes on `redo_desc_other`:** that is already where LABEL MAPPING sends
`faqs:`. The rule is not changing the destination — it is stopping the block being
torn apart on the way there.

**The critical sentence is the third one.** Without an explicit exemption, SPLIT
WITHIN SECTION still applies and still wins. Naming the rule it overrides is what
makes the fix work.

**The last sentence** covers the dropped `"Do you have EFTPOS?"` — the model kept
an answer and discarded its question, which the first sentence alone does not
forbid clearly enough.

---

## Scale

| | |
|---|---|
| In this sample | **1 of 100** products |
| At full catalogue | **~3,100 of 11,236** — the mapping-rules doc puts FAQ headings at 13.7% |

One product in the sample makes this look minor. It is not: at 13.7% it is the
single largest structural defect still open on the description side.

**Also note:** the booking-side `redo_booking_faqs` field is **0% filled across all
100 products** — it has never fired once. Worth checking separately whether FAQ
content on the booking side is being routed anywhere at all.

---

## Verification after the run

1. **606496's `redo_desc_other` contains all 9 questions**, each immediately
   followed by its own answer, in source order
2. `redo_desc_cancellation`, `redo_desc_what_to_bring`, `redo_desc_what_excluded`
   and `redo_desc_check_in` contain **no FAQ text**
3. `"Do you have EFTPOS?"` is present — the dropped question is restored
4. `redo_desc_requirements` does not begin with `min_age:`
5. The other 99 products are unchanged — this edit must not move anything else

---

## Interaction with other open work

| Issue | Interaction |
|---|---|
| **Heading-gating decision** (F9 / ungated description) | If heading-gating wins, SPLIT WITHIN SECTION is deleted from the description prompt entirely and this fix becomes unnecessary — the `faqs:` label would route the whole block to one destination on its own. **Settle that first, or this wording may be written and then deleted.** |
| **ISSUE-3** (`itinerary:` label leaking, 691267) | Same defect class as `min_age:` appearing in Requirements here. Both need "the label marker is structural syntax, not content." Consider fixing together. |
| **Duplication** (26 products) | Unrelated, but the FAQ answer text currently appears in multiple fields, so this fix will reduce the duplicate count as a side effect. |
