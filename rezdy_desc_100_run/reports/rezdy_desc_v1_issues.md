# Rezdy description V1 — issues found, and what V1.1 changes

*Round 1, 100 hardest products, `SYSTEM_PROMPT_RZ_DESC_V1`. Every count below is
measured on that run, not estimated.*

---

## The run was structurally clean

| | |
|---|---|
| Responses | 100 / 100 |
| Unparseable | 0 |
| Truncated | 0 |
| Wrong key set | 0 |
| Prompt contamination | 0 |
| Mean retention | **98.6%** (old method: 71.8%) |
| Products with no finding | 35 / 100 |

Nothing below is a plumbing failure. Every issue is a **rule** that produces the
wrong answer on text the supplier wrote correctly.

---

## ISSUE 1 — the itinerary line test tears day blocks apart

**41 of 100 products.** The single biggest defect in the run.

### What the supplier wrote (PWLAK8)

```
## Full Itinerary
**Day 1: Sydney **
We start in Australia's Harbour City...
**Included Activities**
- Get to know your fellow travellers with a welcome meeting and dinner
**Included Meals**
- Welcome Dinner
**Accommodation** – [Holiday Inn Potts point](https://www.ihg.com/...)
**Day 2: Hunter Valley and Newcastle **
```

Everything is inside `## Full Itinerary`, inside a `Day 1` block. It is itinerary.

### What we produced

The meals and accommodation lines went to **About**. The model said why:

> `itinerary: moved Included Meals and Accommodation blocks to about (no time, day/step number, or ordered stop)`

### Why

STEP 3's ITINERARY LINE TEST requires **every line, independently**, to carry a
clock time, a day/step number, or an ordered stop. `Included Meals: Welcome
Dinner` carries none on its own line.

**The rule contradicts STEP 1E.** STEP 1E says the outer heading wins — so
`## Full Itinerary` should claim everything beneath it. STEP 3 then ejects most
of it, line by line. STEP 3 runs last, so STEP 3 wins.

This is inherited from Fareharbor, where descriptions rarely nest multi-day
blocks. Rezdy is full of them. Same shape as the known Fareharbor case *382277 —
airport parking still an itinerary; CONTENT TEST sits below the qualifying rules
so rule (b) wins.*

### Fix (V1.1)

A Day or Step heading supplies the structural signal for **everything under it,
until the next Day or Step heading.** The line test then applies only where no
day block is open. Asking each child line to prove a day number that its own
heading already states is asking twice.

---

## ISSUE 2 — About fills with orphaned fragments

**34 of 100 products.** This is the *visible damage* caused by Issue 1, and it is
what a reader actually notices.

The ejected lines land in About in source order, stripped of the context that
gave them meaning:

```
PWLAK8 About:
  Included Meals: Welcome Dinner
  Accommodation: Holiday Inn Potts point (https://www.ihg.com/...)
  Included Meals: Breakfast
  Accommodation: Lucky Hotel Newcastle (https://theluckyhotel.com.au/)
  Included Meals: Breakfast
  ...30 fragments
```

Which night is which hotel? Unanswerable — the Day headings that separated them
stayed in Itinerary.

`PPCW71` has 30 such fragments, `P1YNVU` 27, `PVFNZS` 24.

**Retention cannot see this.** Every word survived, so the product scores highly
while being unusable. Exactly the caution recorded on the Fareharbor side: 11 of
13 defects in one run lost no text at all.

### Fix

Falls out of Issue 1's fix — if the day block stays intact, nothing is orphaned.

---

## ISSUE 3 — a lead-in is severed from its list

**3 of 100 products.** Rare, but it damages meaning on *both* sides at once.

### PMUZZL

Supplier:

```
Enjoy a continental breakfast with fresh-brewed coffee or tea, while observing:
- Jabiru (black-necked storks)
- Magpie geese
- Jacanas
```

Result — **Itinerary** keeps the sentence and its dangling colon:

> *…enjoy a continental breakfast with fresh-brewed coffee or tea, while observing:*

**About** gets the birds, attached to nothing:

> *Jabiru (black-necked storks) / Magpie geese / Jacanas*

The itinerary now promises a list it does not contain. About holds bird names
with no sentence, no place, no reason. And because two different lists were
ejected into the same field, **"Magpie geese" appears twice** with nothing left
to distinguish Fogg Dam from Mamukala.

Also seen: `PTW3FE` (*"Here are some key points about Fogg Dam:"*), `PFYJ8P`
(*"Day 1 Highlights:"*).

### Fix (V1.1)

A line ending in `:` and the list beneath it are ONE unit and move together —
the same principle as RULE 6 FAQ PAIRING, which already says a question and its
answer never separate. Splitting a lead-in from its list is the same failure.

---

## ISSUE 4 — 5 URLs lost, confirmed

**2 products, 5 URLs, all verified real** (checked against raw text):

| Product | Lost |
|---|---|
| `PS0MP2` | 4 Chinese-language Wikipedia links, inline in `[text](url)` form |
| `PF008R` | `http://www.arrowtown.com/` |

RULE 7 is explicit that a link keeps its target, so this is the rule being
disobeyed rather than absent. Low volume; worth watching at 1,000-product scale
before writing a rule for it.

*(A 6th was a false positive — `PKBUB1`'s Google Maps link is present in full.
The checker compared URLs exactly and a long URL differed in its tail. Fixed.)*

---

## ISSUE 5 — 3 values start mid-sentence

**3 of 100.** RULE 10 (a sentence is the smallest movable unit) was ported from
the booking side for exactly this, and mostly holds. Monitor rather than change.

---

## NOT an issue, though it looks like one

**Fill rate is 24.8% — about 5 of 21 fields.** That is the gate working. A field
fills only when the supplier wrote a heading for it, and about half of Rezdy
products write few or none. Low fill + high retention means the text is all
present, sitting in About.

**"NO HEADING" flags: 61, of which roughly a third are real.** Verified by
sampling: `Numbers on the Day`, `Session Length`, `Gift eCards Available` and a
block of FAQ questions were all flagged as unlicensed fills — and all four ARE
headings our stem list does not name. CLAUDE.md already records that this mapper
cannot be completed; adding a pattern per topic wording is classification by
meaning, the thing heading-gating replaced.

Two genuine ones worth reading: `PQC41U` (content under *Meeting Time* went to
`check_in`, not `meeting_point`) and `P4RRV9` (`highlights` filled with no
highlights heading).

---

## V1.1 — two changes, nothing else

| # | Change | Fixes | Products |
|---|---|---|---|
| 1 | A Day/Step heading licenses everything beneath it until the next one; the line test applies only outside a day block | Issues 1 & 2 | 41 + 34 |
| 2 | A lead-in line ending in `:` moves with its list | Issue 3 | 3 |

Both are additions to existing rules, not rewrites. Everything else stays
byte-identical, asserted by the builder — the same discipline as V5.4 on the
booking side, which changed one rule and proved the rest untouched by diff.

**Then re-run the same 100 products** for a direct A/B. Every difference must be
explainable by one of these two changes; anything else is a regression.
