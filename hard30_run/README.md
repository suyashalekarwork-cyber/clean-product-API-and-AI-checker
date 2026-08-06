# 30-Product Model Comparison — V4.7 Prompt

**Decision: `gpt-5.6-luna` — $49 to extract all 23,034 products.**

Three candidate models on 30 of the hardest Fareharbor products, using a new
prompt version (V4.7). Raw extraction output only — nothing cleaned or
post-processed, so the numbers show each model's real behaviour.

---

## 1. Results

| Model | Coverage | MISSING | Word ratio | Duplicate sentences | Markdown fields | Cost 23,034 |
|---|---|---|---|---|---|---|
| **gpt-5.6-luna** ← chosen | 98.96% | 5 | 0.946 | 16 | 12 | **$49** |
| gpt-5.6-terra | 99.39% | 4 | 0.945 | **1** | 1 | $487 |
| gpt-5.4-nano | **99.43%** | 4 | **1.187** | **184** | 34 | $50 |
| gpt-4o-mini *(current)* | 96.29% | 0 | 0.827 | 3 | 13 | $28 |

**Word ratio** = words emitted ÷ words in the source. 1.00 means the model
reproduced the source once. Above 1.00 means it repeated content.

**Duplicate sentences** = sentences the model placed in more than one field on
the same side. Counted per side only: cancellation and accessibility genuinely
appear in both the description and the booking notes, and that is correct.

### Why luna, when it is not the top scorer

It is third on coverage and has 16 duplicated sentences to terra's 1. Stating
that plainly matters, because the case for it rests on other things:

- **$49 against terra's $487** — 10x cheaper for 0.43 coverage points
- **Faithful to the source** — 0.946 word ratio, effectively identical to
  terra's 0.945, and nothing like nano's 1.187
- **Newest knowledge cutoff** (Feb 2026) and a 1.05M context window
- **OpenAI's own recommendation** for "cost-sensitive, high-volume workloads"
- **Human review passed it on 6 products**, twice noting it beat nano outright

### Why not the others

**gpt-5.4-nano ($50)** has the best coverage — and duplicated **184
sentences**, emitting 19% more words than the supplier wrote. Coverage cannot
see this: a word counted twice still counts as present, so duplication *raises*
the score. Reviewed by hand and failed.

**gpt-5.6-terra ($487)** is the cleanest output by a clear margin (1 duplicate,
1 markdown field). It is the better model. It is not 10x better.

**gpt-4o-mini ($28)** looks safest on MISSING (0) but that is misleading: it
emits **11,226 words against terra's 12,822 from identical source text**. It is
not more complete — it drops roughly 17% of what the supplier wrote, and has
the worst coverage of the four.

---

## 2. Known weaknesses of the chosen model

Recorded so they can be watched in production, not buried.

**FAQ handling is its weak spot.**
Human review on product `492734`: *"here it failed to capture the FAQ"* —
terra captured it. Product `719471` is its worst row: 22 fields against terra's
14, with an FAQ question landing in `what_included` and its own answer landing
in `what_to_bring`. On a 650-word FAQ-heavy source it over-splits.

**It invents itineraries.**
On `302171` and `328673` it filled `desc_itinerary` with plain narrative — no
clock times, no "Day 1", no list of stops — where terra correctly left the
field empty. On `430823` its itinerary *is* valid (it begins "Start Time:
9:30am"), so it is not always wrong, which makes the failure harder to spot.
See §4 for the prompt text that causes this.

---

## 3. What V4.7 is

**V4.7 = V4.4 verbatim + 2 rules (+11 lines).** Nothing removed, nothing
reworded — `scripts/build_v47_prompts.py` asserts this at build time and fails
if any V4.4 line is lost.

| Rule | Why it was added |
|---|---|
| **NO DUPLICATION** | V4.4 forbade rewording and cross-field borrowing, but never said that extracting text *removes* it from the parent field. That gap let gpt-5.4-nano copy the same sentence into two or three fields 70 times across an earlier 10-product run. Worded as a move, not a copy. |
| **NO INVENTION** | A guard, not a fix. Invention was already near zero, but rules that suppress duplication can push a model toward inventing connective text instead. Also bans placeholder prose such as "No content found in raw text for this field". |

**Why not V4.6:** it is a measured regression — coverage fell 87.23% → 85.95%
because its narrowing rules made the model *drop* content it could not classify
instead of parking it. V4.7's duplication rule therefore states explicitly that
removing a duplicate means removing the extra copy, **never the last copy**.

**V4.7 is a patch, not the destination.** It still classifies by meaning when
no label is present — the guessing that heading-gated extraction is meant to
remove. It exists so this model comparison could run on something better than
V4.4 without waiting for the larger rewrite.

Full text: [`prompts/fareharbor_prompts_v4_7.txt`](prompts/fareharbor_prompts_v4_7.txt)

---

## 4. What V4.7 revealed — measured on this run

### ✅ Worked: NO INVENTION

**0 placeholder fields across all three models.** Earlier V4.4 output had two
models each writing "No content found in raw text for this field" four times.
The rule eliminated it completely.

### ⚠️ Partly worked: NO DUPLICATION

It cut nano's word ratio from 1.32x to 1.19x — but nano still duplicated **184
sentences with the rule explicitly forbidding it**. luna duplicated 16.

Where luna's 16 land:

| Field pair | Count |
|---|---|
| `desc_about` + `desc_requirements` | 3 |
| `desc_about` + `desc_what_included` | 3 |
| `desc_about` + `desc_other` | 2 |
| `desc_other` + `desc_requirements` | 2 |
| `booking_departure_info` + `booking_important_info` | 2 |
| 4 other pairs | 1 each |

**10 of 16 involve `desc_about`** — the exact field the rule names. The
instruction is understood and still not reliably executed.

**Conclusion: a prompt rule alone cannot guarantee this.** It must be enforced
structurally or accepted as best-effort.

### ❌ Did not work: markdown still leaks

V4.7 has no markdown-stripping rule — that was V4.6's approach, dropped because
V4.6 regressed. On luna's output:

| Artifact | Fields affected |
|---|---|
| `- bullet` | 38 |
| `**bold**` | 11 |
| `##heading` | 1 |

**50 fields carry markdown.**

### 🔍 Root cause found: the itinerary definition is too loose

V4.7 defines `redo_desc_itinerary` as:

> "Must contain time signals (e.g. "9am", "Day 1", **"then", "next",
> "first...then...finally"**)"

Those last three are ordering *words*, not structural signals. Every narrative
contains a "then". This is precisely why luna filled itineraries with
description text on `302171` and `328673`.

---

## 5. Suggested changes for the next prompt version

Concrete wording, so the diagnosis above is actionable rather than
re-litigated. **These are proposals — the next version is not yet written.**

| # | Change | Detail |
|---|---|---|
| 1 | **Tighten the itinerary signal** | Delete `"then"`, `"next"`, `"first...then...finally"` from the time-signal list. Replace with: *"Must contain a STRUCTURAL signal: clock times ("9:00am"), day or step numbering ("Day 1", "Stop 3"), or a discrete list of named stops. Ordering words alone (`before`, `then`, `after`) are NOT enough — flowing narrative that mentions events in sequence is description and goes to `redo_desc_about`."* |
| 2 | **Do not ask the model to strip markdown** | Add nothing to the prompt. Strip `**`, `##` and `- ` in Python before the text reaches the model. V4.6 tried the prompt route and regressed. |
| 3 | **Keep NO INVENTION verbatim** | It achieved 0 placeholder fields across all three models. Carry it forward unchanged. |
| 4 | **Do not rely on NO DUPLICATION alone** | Keep the rule — it did cut nano from 1.32x to 1.19x — but treat it as best-effort. 10 of luna's 16 duplicates involve the very field the rule names, so more forceful wording is unlikely to help. |

---

## 6. Files

| File | Contents |
|---|---|
| `best_model_hard30.xlsx` | 5 sheets, 4 models × 30 products. **`Content_By_Model` carries 38 hand-written review verdicts** with the raw supplier text beside each model's output |
| `hard30_products.json` | The 30 selected product IDs |
| `prompts/fareharbor_prompts_v4_7.txt` | Both V4.7 blocks (description + booking notes) |
| `scripts/` | The full reproducible chain, 7 scripts |

**Reproduce:** `select_30_hardest` → `build_v47_prompts` →
`build_hard30_batches` → `run_hard30_batches` → `screen_hard30` →
`build_hard30_workbook`.

Like the rest of this repo, these scripts reference paths from the larger
internal pipeline and are a **snapshot for review**, not a standalone runnable
project. `run_hard30_batches.py` reads `OPENAI_API_KEY` from the environment;
no key is stored here.

---

## 7. How much to trust this

**Verified.** 156 requests, 0 failures, 0 truncated responses, 0 unparseable
JSON across all three models. The V4.7 prompt was asserted present in every
request before submission.

**Limits, stated plainly:**

- **30 products, deliberately hard-selected** — all 30 were flagged for human
  review by an earlier 500-product run. Scores are therefore *lower* than a
  catalogue average would be, by construction. This ranks models against each
  other; it is not a production accuracy estimate.
- **Human review covers 38 of 210 possible rows.** Partial.
- **No LLM judge was run** on these 30. A judge exists in this repo
  (`checker/`), but its absolute scores are known to be unreliable — it grades
  against its own notion of correct placement rather than the extraction
  prompt's rules, and V4.7 changes those rules again.
- **The gpt-4o-mini column was reused, not re-run.** It comes from the earlier
  500-product run, which used prompt V4.4. It therefore differs from the
  candidates in **both model and prompt** — read it as "what we ship today",
  not as a controlled model-versus-model comparison.
