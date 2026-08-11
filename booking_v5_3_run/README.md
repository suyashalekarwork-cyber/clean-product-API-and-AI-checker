# Booking Notes — V5.3 on 100 products

First heading-gated extraction of the `booking_notes` field, and the first time
booking output has been read by anyone.

> **Read this next to the other folders with the sample size in mind.** The
> description runs cover **500** and **1,000** products. This one covers **100**.
> The evidence here is thinner and should not be treated as equally settled.

---

## Check these three first

| File | What it is |
|---|---|
| **`booking_v5_3_data.xlsx`** | One row per product: all 25 extracted columns **plus** `recovered_content`, `reworded_content` and `duplicate_content` side by side. What we extracted, and what we missed, readable together. **Start here.** |
| **`booking_v5_3_audit.xlsx`** | The review workbook — Summary, Findings, All_Products (verdict + comment per product), Per_Product (raw beside every column). |
| **`reports/booking_v5_3_hard100_audit.txt`** | The full per-product audit in plain text, findings first. |

---

## Why booking needed its own work

The booking prompt had not changed since **V4.7** (2026-07-30), and V4.7 forked
from V4.4 — so it never received the eleven rules V4.6 had added from a measured
500-product run. Worse, **no booking output had ever been checked.** The QA
screener discarded the booking half of every run: *"the tool was physically
incapable of seeing them."*

The column list was also inherited rather than measured, which is backwards for a
heading-gated system where the column list drives every decision. So the columns
here come from a census of **all 8,244 products that have booking notes** —
17,212 heading occurrences across 3,729 distinct wordings, counted by how many
**different suppliers** use each one, not just how often it appears.

## What changed from the previous booking prompt

| | |
|---|---|
| Columns | **15 → 25** |
| Renamed | `inclusions` → `what_included`, `location` → `meeting_point` (so booking and description can be merged mechanically) |
| Replaced | `other` → `booking_notes`, defined as the default destination rather than a junk drawer |
| Added | `disclaimers`, `health_safety`, `pricing`, `duration_text`, `highlights`, `special_requirements`, `accessibility`, `what_excluded`, `extras`, `group_size` |

`health_safety` was the clearest gap: **72 different suppliers** write a safety
heading — more than use `restrictions`, `pricing` or `cancellation` — and the
unified schema already had a Health & Safety page section with nothing feeding it.

## The rules

1. A column fills **only** when the supplier wrote a heading naming it. No
   heading → the text goes to `booking_notes`. An empty column is a correct answer.
2. **Nothing is deleted.** Only greetings and separator rules may be omitted, and
   those are recorded in `flags`.
3. **Trust the supplier's heading even when the content disagrees with it.**
4. **The outer heading wins.** If `##Additional Information` covers four
   sub-blocks, all four go to `booking_notes` — even ones whose content looks like
   meeting-point material. Re-routing on content is classification by meaning.
5. **Every label is kept**, joined to its content with `: `.
6. A bullet or list item is never a heading. Under *What to Bring*, `Sunscreen`
   and `Towel` are items — measured, they are the two most common false "headings"
   in the entire catalogue.
7. Line tests apply to `itinerary` and `what_included` only.

---

## Results

100 requests, 100 completed, **all 100 returned exactly the expected 25 keys**,
no JSON repairs needed. Mean retention **98.8%**, 73 products at 100%.

### Both defect fixes worked

| Gate | Previous prompt | V5.3 |
|---|---|---|
| Text copied from the prompt's own examples | 1 product | **0** |
| **URLs lost** | **72 of 238** | **6** |
| URLs altered | 7 | 1 |
| Products with URL damage | 23 | **5** |

The contamination fix works by making every worked example obviously synthetic —
`Sample Wharf`, `Acme Parking`, `example.test` — so any of those strings in real
output is proof the model copied from the prompt. It also gives us a permanent
one-line test for a failure that was previously invisible.

### The catch-all shrank

`booking_notes` holds **24.9%** of all words, down from 28.9%. Content moved into
the specific columns, traced sentence by sentence:

| `important_info` content went to | Sentences |
|---|---|
| `health_safety` | 403 |
| `disclaimers` | 373 |
| stayed in `important_info` | 155 |
| `before_arrival` | 62 |

---

## Issues found — verified against the raw text

Every claim below was checked against the supplier's original before being
written down. One claim did not survive that check and was withdrawn (see
*Corrected* at the end).

### Content loss — 7 products

| ID | Issue |
|---|---|
| **478478** | **Worst — 82.4% retention.** The supplier runs three paddle variants (Lunch 10.30, Dinner Oct–Mar 4.30pm, Dinner Apr–Sep 3.00pm) whose text is near-identical apart from the time. Only one survived. **A customer booking an April date sees the wrong meeting time.** The seal-approach regulations and *"Please follow Sam's instructions at all times"* also went. |
| **481445** | **Safety content.** The entire `11. Boating Etiquette` list — wear your life jacket when instructed, stay seated when the boat is in motion, maintain three points of contact, stay clear of running engines, never throw anything overboard. |
| **211166** | 86.8%. **Image markdown `![alt](url)` is not covered by the link rule** — 2 URLs destroyed, 2 inventions produced (`"Description of image (https://…)"`), and the finish times (4:30 PM / 5:00 PM) lost. |
| **403385** | Both Chandon options lost — *"We can take you to Chandon instead for lunch but this is all at your own expense"*. |
| **254882** | Itinerary closing line lost — *"From 12:30pm – Arrive back at Riverside Adventure Base"*. |
| **743218** | `- Operator: Down Under Cruise & Dive` lost. |
| **100271** | Contact email line lost. **But `100273` is the same supplier with the same sentence, and there it survived** — the documented non-determinism, not a rule failure. |

### URLs — 4 products

**427365** — a URL was **altered**: `www.transport.wa.gov.au/…` → `transport.wa.gov.au/…`. A broken government licensing link that still looks valid.
**272826 / 569893 / 569896** — `tiakinewzealand.com` lost, same supplier all three.

### Duplication — 6 products

**478480** (5 sentences across `notes` and `departure_info`) · **701258** (3) ·
**553708** and **595531** (same sentence, same supplier) · **512675** · **580166**

Duplication is **reported, never removed.** A dedup pass was trialled earlier on
this project and would have emptied 9 booking fields across 8 products. Deciding
which copy is "more specific" is a judgement about meaning made where nobody can
see it, so post-processing may only ADD or REPORT — never delete.

### Cosmetic — 4

**582607** (the lost text is the single word "Agreement") · **108022**, **109135**,
**282368** (a markdown character survived into `notes`).

---

## Working as designed — verified

**`631971` is the flagship.** The raw is `##Additional Information` over 17 bold
sub-labels (Scheduling, Waiver, Location, Food, Footwear, Hat…). The previous
prompt scattered them across six columns. V5.3 keeps **all of it** in
`booking_notes` with every label preserved:

```
Additional Information:
Scheduling: In general camps are 3 days long 9.30-3pm...
Sign-in and out: Please escort your child to the sign in desk...
```

That is the outer-heading rule working exactly as intended.

**`701630`** — a bare Terms & Conditions document split correctly across **six**
of the new columns: Booking & Payment → `pricing`, Cancellations & Refunds →
`cancellation`, Weather & Skipper's Discretion → `important_info`, Safety &
Compliance → `health_safety`, Alcohol & Behaviour → `restrictions`, Liability &
Risk → `disclaimers`.

**`701591`** — collapsed to `disclaimers` only. The raw has no operational
headings, so declining to fill is correct.

---

## Corrected

**`701630` was first reported as content loss and that was wrong.** The retention
figure read 86.3% because the detector compared `"1. Booking & Payment"` against
`"Booking & Payment:"` and scored it absent. Checking against the raw showed all
seven sections present at 90–96% similarity — only the enumeration numbers were
dropped, which carry no information once the heading text is kept. It is one of
the better results in the run, not a defect.

Twelve further flags were overturned the same way: sign-offs the filter missed
(*"I'm looking forward to…"*, *"Ka mihi,"*), inline labels mistaken for packing
items, and label-joining changing a string. **Roughly a quarter of what any
detector here reports is the detector, not the model** — every number in this
folder was checked before being written down.

---

## Not fixed

- **Image markdown `![alt](url)`** — the link rule covers `[text](url)` but not
  the image form. That single gap caused the worst URL losses and both
  inventions (`211166`, `580166`). One rule fixes it.
- **Near-identical blocks are being collapsed** (`478478`). The NO DUPLICATION
  rule is being applied to blocks that differ in one detail — a time. This is the
  most consequential defect in the run, because it changes what time a customer
  turns up.
- **Duplication** (6 products) needs the deterministic pass, not more wording.

## Reproducing

`scripts/` in order: `select_booking_100.py` → `build_booking_v5_3_prompt.py` →
`build_booking_v5_3_batch.py` → `run_booking_v5_3_batch.py` →
`score_booking_v5_3.py` → `build_booking_v5_3_audit_txt.py` →
`build_booking_v5_3_workbook.py`.

See `FILE_DESCRIPTIONS.md` for what every file is.
