# Rezdy — description extraction, first 100 products

The first heading-gated extraction run on **Rezdy**, the second-largest supplier
in the catalogue. 100 products, the hardest in the catalogue, run end to end and
read by hand.

Everything here is reproducible from this folder: the prompt, the scripts, the
100 source products, the raw model output, and the reports built from it.

---

## Why Rezdy needed this

Rezdy's fields were previously filled by **guessing what the text was about**.
We sampled 329 of its extraction failures: **294 of them (89%) were text filed
under the wrong field.** Not missing — misfiled.

Fareharbor had the same problem and one rule fixed it:

> **A field fills only when the supplier wrote a heading naming it.**
> No heading, no fill. The text stays in the description.
> An empty field is a correct answer.

This run applies that rule to Rezdy for the first time.

---

## The result

| | Old method | This run |
|---|---|---|
| **Supplier's words kept** | 71.8% | **98.6%** |
| Products at ≥95% | — | 98 / 100 |
| Fields available | 9 | 21 |

The old method was **silently dropping more than a quarter of every supplier's
text**, and nothing in its output showed that. That is the headline finding.

Structurally the run was clean: 100/100 responses parsed, 0 truncated, 0 with a
wrong key set, 0 contaminated by the prompt's own examples.

**35 of 100 products had no issue found at all.** These are the hardest 100
products in the catalogue — 16 to 55 headings each, up to 2,881 words.

---

## Rezdy has three text fields, not one

This is the main structural difference from Fareharbor, and it decided the
order of work.

| Field | Products | What it is |
|---|---|---|
| `description` | 9,363 | The sales text. What the tour is, what you'll see, what's included. |
| `additionalInformation` | 4,041 | Practical detail. Where to meet, what to bring, check-in, contact. |
| `terms` | 3,377 | The legal small print. Cancellation, liability, booking conditions. |

### Why description first

**1. It is the biggest.** 9,363 products have one, against 4,041 and 3,377. Every
product with any text at all has a description.

**2. It carries the fields customers actually read.** We measured which field
supplies which column across the whole catalogue:

| Column | description | additionalInformation | terms |
|---|---|---|---|
| Highlights | **1,091** | 3 | 0 |
| Itinerary | **1,051** | 21 | 26 |
| What's included | **2,748** | 119 | 35 |
| What's not included | **519** | 20 | 14 |
| Duration | **208** | 45 | 3 |

Highlights, itinerary and inclusions are almost entirely a description
phenomenon. Getting description right delivers most of the visible value.

**3. It is the hardest, so it tests the method properly.** The description is
where suppliers write freely — 8,544 distinct heading wordings. If heading-gating
survives that, the other two fields are easier.

### Why additionalInformation second

It supplies the *practical* columns, and on several it beats the description:

| Column | description | additionalInformation |
|---|---|---|
| Check in | 118 | **160** |
| Contact | 83 | **110** |
| Meeting point | 581 | **404** |
| What to bring | 780 | **426** |

It also shares columns with the description, which raises a question we have not
answered yet: **when both fields contain "What to Bring", which wins?** Running
description first, alone, keeps that question out of the way until the harder
work is done.

### Why terms last

**It is mostly one answer already.** Its most common heading by a wide margin is
literally *"Cancellation Policy"* (66 suppliers), and our schema already maps the
whole field to the cancellation column. Splitting it gains the least.

It is also structurally different — **only 23 of 3,377 contain any HTML**, the
rest is plain text — so it needs its own rules rather than a reuse of these.

And leaving it out keeps the eventual merge a two-way problem rather than a
three-way one, while the two-way version is still unsolved.

---

## How long it took

Both runs used the OpenAI Batch API with `gpt-5.6-luna`, 100 requests each.

| Run | Submitted | Completed | Wall clock |
|---|---|---|---|
| V1 | 17:00:38 | ~17:06:40 | **≈ 6 minutes** |
| V1.2 | 17:57:53 | 18:29:12 | **≈ 31 minutes** |

Same size, same model, same 100 products — but **5x the wall clock**. Batch API
queue time is not predictable and does not scale with the work; plan the full
run around that rather than around the 6-minute case.

~1.05M tokens per run, most of which is the 32 KB system prompt repeated on
every request. At catalogue scale that is the binding constraint: 9,363
description requests is ~276 MB and must be chunked at 3,000 per batch to stay
under the API's 200 MB file limit and its enqueued-token cap.

---

## Issues found, with examples

Every one below is a **rule** producing the wrong answer on text the supplier
wrote correctly — not a crash, not a parsing failure.

### 1. Multi-day tours were split in half — 41 of 100 products

Supplier wrote (product `PWLAK8`, a 16-day tour):

```
## Full Itinerary
**Day 1: Sydney**
We start in Australia's Harbour City...
**Included Meals**
- Welcome Dinner
**Accommodation** – Holiday Inn Potts Point
**Day 2: Hunter Valley**
```

The day's story went to **Itinerary**; the meals and hotel went to **About**.

The model explained itself in its own notes:

> `itinerary: moved Included Meals and Accommodation blocks to about (no time, day/step number, or ordered stop)`

Our rule demanded every *line* independently prove it belonged in an itinerary
by carrying a time or day number. `Accommodation: Holiday Inn` carries neither.

**Consequence:** About became 30 hotel and meal lines with no days attached — you
could not tell which night was which hotel. **34 of 100 products** ended up with
these orphaned fragments.

**Fix (V1.1):** once a supplier writes `Day 1`, everything until `Day 2` is that
day. The day heading already supplies the signal; asking each child line to
prove it again is asking twice.

### 2. A sentence lost its list — 3 products

Product `PMUZZL`:

```
Enjoy a continental breakfast, while observing:
- Jabiru (black-necked storks)
- Magpie geese
- Jacanas
```

The sentence stayed in **Itinerary**; the birds went to **About**. Itinerary now
promises a list it does not contain, and About holds bird names attached to
nothing. Both halves became useless.

**Fix (V1.1):** a line ending in `:` moves with its list. We already had this
rule for questions and their answers; it simply never covered lists.

### 3. Terms & Conditions was never extracted — the field was dead

`disclaimers` filled **0 times across all 100 products**, while the catalogue
census measures it at 178 suppliers and 7.9% of products.

The inherited definition read, in full:

```
redo_desc_disclaimers   Disclaimers, Risk Disclosure, Liability, Waiver.
```

It never mentions **Terms & Conditions** — which is what 75 Rezdy suppliers
actually write, against 5 for "liability" and 4 for "disclaimer". Six of the 100
products carry an explicit `**Terms & Conditions**` heading; none filled the
field. The model was right, and the prompt was incomplete.

**Fix (V1.2):** Terms & Conditions is now named as that field's main heading.

### The pattern behind issues 1 and 3

Both have the same cause: **our column document and our prompt disagreed.** The
column document maps `Day 1` to itinerary and `terms and conditions` to
disclaimers. The prompt mentioned neither.

Twice is a pattern. Before porting to the next source, diff the two documents
against each other first.

### Found but not fixed

- **5 web links lost**, across 2 products (`PS0MP2`, `PF008R`) — all verified
  real. The rule already forbids this, so it is the model slipping rather than a
  missing rule. Too rare to redesign around; re-measure at 1,000 products.
- **3 values starting mid-sentence.** Same reasoning.

---

## Things that look like failures and are not

**Fill rate is 24.8% — about 5 of 21 fields.** That is the design. A field fills
only when the supplier wrote a heading, and about half of Rezdy products write
few or none. **Low fill plus high retention means the text is all present,
sitting in the About field.** The two numbers are only meaningful together.

**61 "filled with no heading" warnings, of which roughly a third are real.**
Verified by hand: `Numbers on the Day`, `Session Length` and `Gift eCards
Available` were all flagged as unlicensed — and all three ARE headings, just not
ones our checker's list names. The heading-to-column map cannot be completed;
adding a pattern per supplier wording is meaning-based classification, the thing
this method replaced.

---

## What's in this folder

| Path | Contents |
|---|---|
| `prompts/rezdy_prompts.txt` | All three prompt versions, append-only. **V1.2 is current.** |
| `scripts/` | Every script, in run order — see below. |
| `input/rezdy_desc_100_products.json` | The 100 selected products with their heading counts. |
| `input/products/` | The 100 raw Rezdy API responses, unmodified. |
| `results/rezdy_desc_100_output.jsonl` | Raw Batch API replies for the V1 run. |
| `reports/rezdy_desc_100_raw_vs_extracted.txt` | Supplier text and extraction side by side, per product. |
| `reports/rezdy_desc_100_issues.txt` | Per-product issue list, all 100 including the clean ones. |
| `reports/rezdy_column_definitions.md` | The field list, built from supplier evidence before any prompt was written. |
| `reports/rezdy_heading_census.md` | The viability study — do Rezdy suppliers write headings at all? |
| `reports/rezdy_desc_v1_issues.md` | The issue list that produced V1.1 and V1.2. |
| `rezdy_100_manager_review.xlsx` | **Start here for review** — supplier text and extraction per product. |
| `rezdy_step1_vs_step2_100.xlsx` | Old method vs new, stacked, same 100 products. |

### Run order

```
rezdy_heading_census.py             is heading-gating viable on Rezdy at all?
build_rezdy_column_definitions.py   which fields exist, from supplier evidence
build_rezdy_desc_prompt.py          V1, derived from the Fareharbor prompt
build_rezdy_desc_v1_1_prompt.py     V1.1  (day blocks, lead-in lists)
build_rezdy_desc_v1_2_prompt.py     V1.2  (Terms & Conditions)
select_rezdy_desc_100.py            pick the 100 hardest, max 3 per supplier
build_rezdy_desc_100_batch.py       build the request file, 4 pre-flight checks
run_rezdy_desc_100_batch.py         submit and poll
build_rezdy_desc_100_issues.py      per-product issue list
build_rezdy_desc_100_raw_vs_extracted.py
build_rezdy_100_manager_workbook.py
compare_rezdy_v1_vs_v1_2.py         the A/B
```

`rezdy_common.py` holds the piece everything depends on — see below.
`rezdy_postprocess.py` is the safety net that finds text the model dropped, and
records **which heading it belonged under**, so a loss is fixable rather than
merely counted.

---

## The one technical thing worth knowing

**Rezdy's text is HTML. Fareharbor's is markdown.** Fareharbor's tool simply
deletes HTML tags — which is safe there, because its line breaks are real
newline characters.

On Rezdy the line breaks **are** the tags. Deleting them collapses the text to a
single line and every heading disappears. Measured on a real product, the
Fareharbor tool turned a heading and its three-item list into one unbroken
paragraph.

The conclusion would have been *"Rezdy suppliers don't write headings, abandon
this"* — and it would have been wrong. We destroyed them ourselves.

So `rezdy_common.html_to_markdown()` **restores structure instead of deleting
it**: `<h1-6>` → `##`, `<li>` → `- `, `<b>` → `**bold**`, `<a>` → `[text](url)`.
**72.8% of Rezdy's headings come from that markup** — bold alone is 50.7%, more
than double the heading tags.

It makes no judgement about what is a heading. That decision stays with the
model, where the rules are written down and testable. An earlier version did
judge, and it silently deleted **484 real headings** across 241 products for
ending in a question mark — `<h4>What do you need to bring?</h4>`.

The converter is verified word-for-word lossless across all 9,361 products, and
the batch builder refuses to run if a single word would be dropped.

---

## The re-run: V1 vs V1.2, same 100 products

Both prompt versions were run on the **same 100 products with the same supplier
text**, so any difference is the prompt and nothing else. V1.2 declared three
fixes; the job of the A/B is to check that each one did what it said, and that
nothing else moved.

Full detail: `reports/rezdy_v1_vs_v1_2_ab.txt`. Raw output:
`results/rezdy_desc_100_output_rzd12.jsonl`.

### Fix 1 — day blocks stay whole ✅

| | V1 | V1.2 |
|---|---|---|
| Words in Itinerary | 53,679 | **61,404** (+7,725) |
| Words in About | 45,351 | **35,508** (−9,843) |
| Orphaned fragments in About | 883 | **512** (−371) |

Nearly **10,000 words left About and went back into the itinerary**, where the
supplier had put them. The number of products *with* an itinerary barely moved
(59 → 59) — the same products always had one. What changed is that each day is
now whole instead of split across two fields.

### Fix 3 — Terms & Conditions ✅

`disclaimers` went from **0 to 6** — exactly the six products carrying an
explicit Terms & Conditions heading. A field that was dead is now doing its job.

### Fix 2 — lead-in with its list ⚠️ inconclusive

Our proxy (an itinerary value ending in a colon) moved 2 → 1. The measure is too
weak to prove anything at this scale; the three known products need reading by
hand.

### Five changes with no declared cause

Every product that changed was checked against the three fixes. Five moved
something the fixes do not touch:

| Product | What moved | Reading |
|---|---|---|
| `PATGNR` | pricing: "Travel With us" → "Travel With Us" | a capitalisation change — a small VERBATIM slip |
| `PJZBNW` | duration: "3 hours" → "Duration 3 hours" | kept a label that names its own column |
| `P1CL35` | meeting point lost the "PICK UP & DROP OFF" label | arguably an improvement — the label named the column |
| `PS01BF` | what's included, same length, reordered | cosmetic |
| `PGKMXJ` | **one sentence lost from extras** | a real loss: *"Transform your picnic into a full romantic or celebratory escape…"* appears nowhere in V1.2's output |

### What this comparison cannot prove

**There is no control run.** The model is not deterministic — on the Fareharbor
side, re-running identical products against an *identical* prompt made 4 of 6
defects disappear. So a small difference here cannot be attributed to our change
rather than to run-to-run variance.

That is fine for the large movements: ~10,000 words moving in the predicted
direction is not noise. It is **not** fine for those five small diffs, which is
why they are listed individually rather than counted. Reading them is the only
way to tell a regression from a coin flip.

### Verdict

Two of the three fixes are confirmed at a scale that variance cannot explain.
The third needs a hand-read. One sentence was lost in a product that has nothing
to do with the fixes — worth watching at 1,000 products, not worth a rule yet.

**V1.2 is the version to scale with.**
