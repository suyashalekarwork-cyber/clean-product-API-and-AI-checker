# Prompt Version Log — Fareharbor description side

Every version, what it changed, what it fixed, what it broke, and how to go back.

**All blocks live in `config/fareharbor_prompts.txt`** and are appended, never
edited in place — so every earlier version is still there and still extractable.
Rolling back is a one-line change to `run_luna100.py`, not a file restore.

**Booking prompt has not changed since V4.7** (`SYSTEM_PROMPT_FH_BOOKING_V4_7`).
Everything below is description-side only.

---

## Quick reference

| Version | Line in prompts.txt | Run output | Changed | Status |
|---|---|---|---|---|
| `..._DESC_V4_7` | 3132 | `luna100_output.jsonl` | baseline | superseded |
| `..._DESC_V4_8` | 4270 | `luna100_v4_8_output.jsonl` | itinerary, structural test | superseded |
| `..._DESC_V4_8_1` | 4469 | `luna100_v4_8_1_output.jsonl` | itinerary, day/time-wise, copy whole | superseded |
| `..._DESC_V4_8_2` | 4677 | `luna100_v4_8_2_output.jsonl` | **new `redo_desc_faqs` field** + 3 itinerary fixes | superseded |
| `..._DESC_V4_8_3` | 4903 | `luna100_v4_8_3_output.jsonl` | **What's Included heading-gating** | **CURRENT** |

**Schema note:** V4.8.2 added a 16th output field, `redo_desc_faqs`. Any rollback
to V4.8.1 or earlier drops that field — `screen_model_comparison.DESC_FIELDS` and
`build_luna100_workbook.NICE` would need it removed too.

---

## How to roll back

```
# in run_luna100.py
DESC_VERSION = "SYSTEM_PROMPT_FH_DESC_V4_8_2"      # <- any version name above
OUTPUT       = TEST_DIR / "luna100_rollback_output.jsonl"
```

Then `python run_luna100.py`. Nothing is deleted; the old run outputs stay on disk
for comparison. Cost per full re-run: ~$0.42, ~3 minutes.

To read an old prompt without running it:

```python
from build_model_comparison_batches import PROMPT_PATH, extract_prompt
p = extract_prompt(PROMPT_PATH.read_text(encoding="utf-8"),
                   "SYSTEM_PROMPT_FH_DESC_V4_8_1")
```

⚠️ Version matching is **exact-string**. `V4_8` will not accidentally match
`V4_8_1` or `V4_8_2` — verified each time a version was added. Keep it that way.

---

## V4.7 — baseline

**Built by:** `build_v47_prompts.py` · **From:** V4.4 · **Run:** `luna100_output.jsonl`

V4.4 verbatim plus two rules inserted after the VERBATIM RULE: **NO DUPLICATION**
and **NO INVENTION**.

**Known defect, never fixed here:** the builder copied V4.4's header verbatim, so
the published booking prompt still reads `VERSION: 4.4 — no content change` while
its body does carry the new rules. Documentation only; the run itself was valid.

**Itinerary state:** accepted `then` / `next` as proof of an itinerary. 30 of 100
products filled; roughly half held prose, marketing copy or airport parking.

---

## V4.8 — itinerary, structural test

**Built by:** `build_v4_8_prompts.py` · **From:** V4.7 · **Run:** `luna100_v4_8_output.jsonl`

**Changed:** `redo_desc_itinerary` only. Replaced the "time signals" gate with a
row-level structural test — clock time, step marker, or short stop names.

**Fixed:** prose accepted via "then" (7 products), selling-point lists, airport
parking (382277), equipment admin (716074), marketing paragraphs (270858),
start-time-only (252851), opening hours inside the field (288725). 24-hour times
recognised (738691).

**Result:** 30 → 16 filled. Zero text lost.

**Broke:** trimmed rows out of good itineraries — 288725 lost `11:30am – Check in`,
186343 lost 3 rows.

---

## V4.8.1 — itinerary, day/time-wise, copy whole

**Built by:** `build_v4_8_1_prompts.py` · **From:** V4.8 · **Run:** `luna100_v4_8_1_output.jsonl`

**Changed:** `redo_desc_itinerary` only. Definition became **day-wise or
time-wise, extracted WHOLE** — clause (c) deleted, no length test, no trimming.
Decisions D11/D12.

**Fixed:** activity lists rejected (186343, 666061, 709179, 714769). Trimming
stopped — 738691 kept all 12 rows, 709572 kept its DAY ONE/DAY TWO narrative.

**Result:** 16 → 13 filled.

**Broke:**
- 382277 airport parking came **back** — CONTENT TEST sits below the qualifying
  rules, so rule (b) outranks it. **Still open (ISSUE-2).**
- 691267 emitted `itinerary: 1. Arrival at HQ…` — the raw label leaked in.
- 585533 rows 3 and 4 merged back onto one line.

---

## V4.8.2 — FAQ field + 3 itinerary fixes

**Built by:** `build_v4_8_2_prompts.py` · **From:** V4.8.1 · **Run:** `luna100_v4_8_2_output.jsonl`

**Changed:**
1. **NEW OUTPUT FIELD `redo_desc_faqs`** — schema 15 → 16 fields. `faqs:` now maps
   here instead of `redo_desc_other`, and the field explicitly overrides SPLIT
   WITHIN SECTION.
2. ISSUE-7 — a bare-time list is a timetable, not an itinerary (678270).
3. ISSUE-3 — the `itinerary:` label is not content (691267).
4. ISSUE-9 — two numbered steps on one line are split (585533).
5. General rule: label markers are structural syntax, not content.

**Fixed:** 606496's FAQ block — 9 of 9 questions now in one field, nothing
scattered. Previously the weather FAQ was in Cancellation Policy (100% of that
field), the clothing FAQ in What to Bring (100%), and "Do you have a BBQ? Yes,
$25" was published under What's NOT Included. One question had been deleted
outright. 391646 also picked up an FAQ block nobody had noticed.
All three itinerary fixes verified passing.

**Broke:** nothing detected.

**Downstream edits shipped with it:** `screen_model_comparison.DESC_FIELDS` and
`build_luna100_workbook.NICE` both gained `redo_desc_faqs`.

---

## V4.8.3 — What's Included heading-gating · CURRENT

**Built by:** `build_v4_8_3_prompts.py` · **From:** V4.8.2 · **Run:** `luna100_v4_8_3_output.jsonl`

**Changed:** `redo_desc_what_included` (was a single line), plus one clause added
to the NO DUPLICATION RULE. Rules WI-R1..WI-R6 — see `WHAT_INCLUDED_ISSUES.md`.

- **WI-R1** heading required; no heading → empty, text stays in About
- **WI-R2** heading = the word **or any synonym**, in any form
- **WI-R3** check every line under the heading, do not copy the block
- **WI-R4** leftovers to About
- **WI-R5** only clearly-guaranteed items; conditional availability is not an
  inclusion, applied row by row
- **WI-R6** repetition in the source does not license repetition in the output

**Fixed:** 56 → 40 filled. 15 products correctly emptied with **100% of text
preserved**. All conditional cases resolved — 459312, 510317, 529363 by
heading-gating; 317691 by the row rule (kept 5 of 7 rows, dropped
`PFD's are available` and `Wetsuit if required`). Zero invention, zero label
leaks, zero non-inclusion lines pulled in under a heading.

**Broke — itinerary drift, though the itinerary definition was NOT touched:**

| Product | V4.8.2 | V4.8.3 |
|---|---|---|
| **550275** | `Boarding: 11:30 am Parsley Bay Wharf / Disembarking: 2:00pm` | **EMPTY** — lost a good itinerary |
| **559785** | empty | `Heli boarding at 10.15am. / Heli departure at 11.30am.` — reverses D10 |
| 659457 | rows prefixed `- ` | prefixes stripped (cosmetic) |
| 606496 | FAQ value | minor change |

**Also open:** 252851 filled with no inclusions heading — the one heading-gating
violation. 598043 at 56% source-word retention.

---

## Recurring defect — malformed JSON, not version-specific

The model intermittently closes its JSON with a stray `,"` before the brace:

```
..."redo_desc_other":"If you book Launch and Retrieve.","}
                                                       ^^^ invalid
```

| Run | Products affected |
|---|---|
| V4.8.1 | 459312 |
| V4.8.3 | 493762, 317691 |

Roughly 1–2 products per run, **different products each time** — so it is a
sampling artefact, not a prompt defect, and it will not be fixed by wording.

**Currently these products are silently dropped by every analysis script**, which
is how 317691 first appeared as "text lost, 0% preserved" when its output was
actually correct.

**Fix belongs in the loader, not the prompt:**
`re.sub(r',\s*"\s*\}\s*$', '}', text)` before `json.loads`. Verified to repair
both V4.8.3 failures cleanly.

---

## Rules of the road

1. **Append, never edit.** Every version stays extractable, so rollback is always
   possible.
2. **One section per version.** V4.8.3 touched only What's Included, which is the
   only reason the itinerary drift was detectable at all.
3. **Check the untouched fields every run.** Twice now, narrowing one field has
   moved another. Assume nothing holds still.
4. **The builder must prove the diff.** Each `build_v4_8_*.py` asserts that
   nothing outside the intended edit changed, and refuses to write otherwise.
