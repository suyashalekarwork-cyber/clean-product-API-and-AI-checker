# Fareharbor Description Extraction — Session Report

**Date:** 2026-08-10
**Scope:** description-side extraction, 100-product sample, model `gpt-5.6-luna`
**Prompt:** V4.7 at the start → **V4.8.3** now

---

## What we set out to do

Work through the extraction one field at a time: agree what the field means,
rewrite that part of the prompt, re-run the same 100 products, and check the
result **against the supplier's raw text** rather than against the previous run.

Three fields were completed: **Itinerary**, **FAQ**, **What's Included**.

---

## Headline results

| Field | Before | After | What changed |
|---|---|---|---|
| **Itinerary** | 30 filled, roughly half holding the wrong content | **12 filled** | Now only genuine day-wise or time-wise plans |
| **FAQ** | did not exist | **new field, 2 products** | Q&A blocks kept whole instead of scattered |
| **What's Included** | 58 filled, 21 inferred with no supplier heading | **41 filled** | Only filled when the supplier says so |

**Across every change: no content was deleted.** Every value removed from a field
was verified present elsewhere in the output, at 100% word retention. **Zero
invented content** in any run.

---

## Field by field

### Itinerary — the largest clean-up

The prompt accepted the words *"then"* and *"next"* as proof of an itinerary.
Every narrative paragraph contains a "then", so the field filled with the wrong
thing on roughly half the products that had it.

**Examples of what was being published as a tour route:**

```
382277   "1. Park your vehicle in our valet car parks
          2. Drop your keys in the last-minute key drop"      <- airport parking

186343   "Chill beach intro + simple ocean safety rundown
          Learn the basics on the sand"                        <- Tour Highlights

678270   "9:30am / 10:35am / 12:10pm / 1:15pm / 2:20pm"        <- a departure
                                                                  timetable, not
                                                                  five stops
```

**Now defined as:** a day-wise or time-wise plan of what happens during the
experience, extracted whole. An activity list with no day and no time marker is
Highlights, not an itinerary.

**Result:** 30 → 12. One known defect remains (382277, below).

Along the way the field also stopped emitting the raw `itinerary:` label as
visible text, and started splitting two numbered steps the supplier had run
together on one line.

---

### FAQ — a new field

One supplier wrote a single `faqs:` block with nine questions and answers. The
extraction **scattered it across six different fields**:

| Where it landed | What the page would have shown |
|---|---|
| Cancellation Policy | a question about whether games run in the rain |
| What to Bring | a question about what to wear |
| **What's NOT Included** | *"Do you have a BBQ? Yes we do — the fee is $25"* |

That last one is the clearest illustration of the cost: a paid extra published as
something the customer does **not** get. One question — *"Do you have EFTPOS?"* —
was dropped entirely while its answer survived with nothing to attach to.

**Fix:** a dedicated `redo_desc_faqs` field, with questions and answers kept
together in source order.

**Result:** 9 of 9 questions now in one field and nowhere else. A second product
was also picked up that nobody had noticed had FAQ content.

**Scale note:** one product in this sample, but FAQ headings appear on roughly
13.7% of the catalogue — about **3,100 products** at full scale.

---

### What's Included — gated on the supplier's own heading

58 products had this field filled, but only 37 had any heading announcing an
inclusions list. The rest were inferred from ordinary prose, and the inference
went wrong in a specific way:

```
459312   "Arion Riding Centre can supply helmets and riding boots
           if you do not have your own."
```

That sentence sits under the supplier's **##Clothing Requirements** heading. Six
of its seven sentences went to Requirements; this one was pulled out into What's
Included. Two problems: *"can supply … if you don't have your own"* is
availability, not an inclusion — and the sentence was separated from its own
section.

**Now:** the field fills only when the raw text has a heading announcing
inclusions — including synonyms (`provided`, `we supply`, `you get`,
`Buffet Includes:`, `##Package Inclusions:`) and a sentence ending in a colon that
introduces a list. Each line under that heading is checked individually rather
than copied as a block, and only guaranteed items qualify.

**Result:** 58 → 41. Fifteen products correctly emptied, all text preserved.
Every conditional-availability case resolved.

---

## How the work was verified

Each change was tested by re-running the same 100 products and checking the
output **against the raw supplier text** — not against the previous version. That
matters: a prompt version can look like an improvement purely because the earlier
one was worse, and the earlier one was often measurably wrong.

Checks applied every run:

- **Nothing deleted** — text removed from one field must appear in another
- **Nothing invented** — every word must trace back to the raw source
- **Untouched fields must not move** — a change to one field's definition should
  leave the others alone

That third check earned its place. Changing one field's wording has twice shifted
behaviour in a field we did not edit. Every run now verifies the fields we did not
intend to change.

**Four batch runs, 664 requests, zero technical failures.** Total spend well under
$2.

---

## Two process items worth keeping

**A decision log.** Sixteen decisions are recorded with the reasoning and the
product that prompted each one — including four that were later reversed as
better examples came to light. Without it we re-argued the same points more than
once.

**A version log with rollback.** Every prompt version is appended to the file
rather than replacing the previous one, so any version can be re-run with a
one-line change. Each entry records what it fixed **and what it broke**.

---

## What is still open

### Needs a prompt change — 3 products

| Product | Issue |
|---|---|
| **382277** | Airport parking instructions still extracted as a tour itinerary. The rule that should catch it sits below the rule that lets it through |
| **252851** | What's Included filled with no supplier heading — the one gating miss in 100 |
| **675102** | Itinerary rows read `cellar door 1, 2, 3, 4` — a placeholder list with no named venue |

### Needs code, not wording — cannot be fixed by the prompt

| Issue | Products |
|---|---|
| The same sentence stored in two fields, so the page prints it twice | **26** |
| The same itinerary in the description and booking sections, sometimes in **opposite order** | 5 |
| Occasional malformed output that current scripts drop silently | 1–2 per run |

The duplication issue is now the largest single quality problem on the
description side — larger than anything left in the three fields we worked on.
Three prompt versions have tried and failed to fix it; the rule exists and is
being ignored. It needs a post-processing pass.

The malformed-output issue is worth fixing early: the affected products currently
vanish from every report without warning, which caused one product to be
mis-reported as content loss when its extraction had actually been correct.

### Not yet started

Highlights · What's NOT Included · Cancellation policy · Check-in and meeting
point · Duration, age and group size · the entire booking-notes side.

---

## Recommended next steps

1. **One prompt version** covering the three open products above
2. **The de-duplication pass** — highest remaining impact, and it is code
3. **Continue field by field** through the sections not yet started

The method is working and is worth keeping: agree the definition, change one
field, re-run, check against the raw text, record the decision. It is slower than
changing several things at once, but when quality moves we know exactly what moved
it — and twice now that has been the only reason we caught a change we did not
intend.
