# V5.3 — heading-gated extraction, 500 products

Prompt `SYSTEM_PROMPT_FH_DESC_V5_3` run on the 500 hardest Fareharbor products
via `gpt-5.6-luna`. **499/499 completed, 0 failed, 0 truncated, 0 unparseable.**

---

## To review this run, open these three

| File | What it is |
|---|---|
| **`v5_3_500_audit.xlsx`** | The review workbook. Four sheets: `Priority_Matrix` (every issue by severity, with product IDs), `Issues_Only` (the 33 flagged products), `All_Products` (all 499 with a verdict and a written comment), `Per_Product` (each product's raw description beside all 22 extracted columns). **Start here** — filterable, and it holds the verdicts. |
| **`prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt`** | The prompt that produced everything else. The rules the extraction actually followed, the 22-field output schema, and 6 worked examples. Read this to judge whether a given output is a defect or the rules working as written. |
| **`reports/v5_3_hard500_audit.txt`** | The full per-product audit in plain text — 1.5 MB, issues first, clean products last. Each entry: verdict, comment, retention, the raw description, and every filled column. Use it to read a product end to end without opening Excel. |

Same three are described in `FILE_DESCRIPTIONS.md`, with the rest of the folder.

---

# The issues

Three groups of ours, plus the supplier's. Each rated High / Medium / Low.

## 1. CONTENT LOSS — 3 products (0.6%)

*Text that was in the supplier's description and reached no column.*

| Severity | ID | What was lost |
|---|---|---|
| 🔴 **HIGH** | `535701` | *"Please order your protein at the time of booking"* — an instruction the customer has to act on |
| 🟠 MEDIUM | `371805` | Engine spec — **happens every run**, the only repeatable one |
| 🟡 LOW | `293135` | Opening tagline |

**Fix:** a check after extraction that returns any orphaned sentence to About.
Not a prompt rule — the loss is random, see Repeatability.

## 2. MISCLASSIFICATION — 10 products (2.0%)

*Text landed in the wrong column, or lost the label that identified it.*

| Severity | IDs | What's wrong |
|---|---|---|
| 🔴 **HIGH** | `634003` | `Departure times` and `Arrival times` both dropped and the two lists merged — Mission Beach 5:30 PM now reads as a fourth pickup point |
| 🟠 MEDIUM | `466438` `491113` | Difficulty rating in the **Restrictions** box — reads `Moderate` / `Level: Hard` |
| 🟠 MEDIUM | `639882` | Sub-labels `Scenic Landscapes:`, `Wildlife Encounters:`, `Dress Code:` all dropped — highlights reads as unattributed paragraphs |
| 🟡 LOW | `713497` `324361` `697755` | Label stripped — every value survived, the section just has no title |
| 🟡 LOW | `251713` | Content overrode the heading (the answer is arguably better) |
| 🟡 LOW | `198064` `501920` | A marketing line sitting in a list column |

**Fix:** two lines of prompt for difficulty. The label losses need a sharper
rule — see *A blind spot worth naming*.

## 3. SUPPLIER MISTAKE — 22 products (4.4%)

*Wrong in the raw text before extraction touched it.*

| Severity | Count | IDs | What's wrong |
|---|---|---|---|
| 🔴 **HIGH** | 3 | `564767` `531290` `598043` | **No description at all** — the raw is just the product name |
| 🔴 **HIGH** | 1 | `327258` | What-to-Bring says the supplier **provides** everything — the opposite |
| 🔴 **HIGH** | 1 | `266189` | The whole description is `meeting_point: Te Anau` |
| 🟠 MEDIUM | 2 | `156525` `500245` | Notes / cancellation terms filed under `What to bring` |
| 🟠 MEDIUM | 1 | `680927` | Headings written with no content under them |
| 🟡 LOW | 10 | `509794` `203555` `249729` `330482` `279178` `444088` `397465` `319096` `171361` `324361` | Raw repeats itself — the text shows twice on the page |
| 🟡 LOW | 4 | `417608` `442752` `328897` `697755` | Near-duplicate · control character · `n/a` placeholder · template keys |

**Fix:** mostly nothing we can do. De-duplicate at render time; the 3 with no
description need chasing with the supplier.

---

## Totals

| | Products | % of 499 |
|---|---|---|
| **Clean** | **466** | **93.4%** |
| Content loss | 3 | 0.6% |
| Misclassification | 10 | 2.0% |
| Supplier mistake | 22 | 4.4% |
| *(`324361` and `697755` appear in two groups)* | | |

### The ones actually worth fixing

**6 products (1.2%)** are High or Medium and ours:

| Group | Count | IDs |
|---|---|---|
| Content loss | 2 | `535701` `371805` |
| Misclassification | 4 | `634003` `466438` `491113` `639882` |

**High severity across everything: 7 products (1.4%) — and 5 of those are the
supplier's**, not fixable by any prompt.

---

## Delivery plan — two phases

**Phase 1 — ship now.** Accept both the supplier problems and our own, because
at this scale they are few: **33 of 499 products (6.6%)** carry any known issue
— 13 ours, 22 the supplier's, 2 counted in both — and only **6 (1.2%)** are High
or Medium and ours to fix. The other **466 (93.4%) are clean**.

That is good enough for the web dev team to build the product page against: the
schema is settled, the columns are stable, and every known exception is listed
by product ID above and in the `Issues_Only` sheet of `v5_3_500_audit.xlsx`.
Nothing is hidden — "accept" here means *known and listed*, not resolved.

**Phase 2 — go inside the content.** Phase 1 routes by **heading**. Phase 2 goes
a level deeper and checks each **line within** a section, routing it to the
column it actually belongs to.

`327258` is the model for this: the supplier's heading says *What to bring*
while the line under it says *"Salt Spray Surf School provides all surfboards...
wetsuits are provided if need be."* — the opposite. Heading-gating obeyed the
label, which is correct at Phase 1 and wrong for the customer. Extending the
line test — which already exists for `itinerary` and `what_included` — is the
mechanism.

**Why split it this way.** The web team is blocked on schema, not on the last
few percent of placement accuracy. Shipping Phase 1 unblocks them immediately,
and the pages they build become the real feedback for Phase 2.

**One caveat for whoever consumes Phase 1 data:** the defect rate is *per run*,
not a fixed set of products. See Repeatability — a different run loses different
sentences. Phase 1 output is a snapshot, which matters if it gets cached rather
than regenerated.

---

## Repeatability — the most important finding

The 500 re-ran all 100 products from the previous run on the **identical**
prompt, so the two are directly comparable. **Most defects did not reproduce:**

| Product | Run 1 (100) | Run 2 (500) | |
|---|---|---|---|
| `457336` | lost 3 sentences | **lost 0** | vanished |
| `676702` | lost 1 sentence | **lost 0** | vanished |
| `135308` | duplicated | **clean** | vanished |
| `417608` | duplicated | **clean** | vanished |
| `371805` | lost 1 sentence | lost 1 | **repeatable** |
| `509794` | duplicated | duplicated | **repeatable** |

Four of six were sampling noise, not a rule the model gets wrong.

**This changes what a fix can achieve.** A prompt rule can only address the
repeatable cases. For the random ones no wording is a guarantee — the only way
to make content loss structurally impossible is a deterministic check after
extraction that returns any unaccounted-for sentence to About.

It also means **a single run understates the true rate**: a different run loses
different sentences.

---

## The strongest evidence: products with no heading at all

51% of the run (254 products) has **no heading naming a column**. This is the
situation V5.3 exists for: with nothing to go on, earlier versions guessed which
section a sentence belonged to, and on a 329-failure sample 294 (89.4%) of those
guesses filed real text under the wrong heading. V5.3's rule is that no heading
means the text stays in About.

| Group | Products | Issues found |
|---|---|---|
| No headings at all — pure prose | 192 | **0** |
| Headings present, none maps to a column | 37 | **0** |
| Filled a column anyway | 23 | 1 real defect |

**229 of 254 with zero issues.** Of the 23 that filled something, 20 turned out
to be the model reading a heading the review script's regex could not see —
`Your Day in the Hunter Valley begins at:` (8 words, regex caps at 7),
`Cost: $79 per adult` (inline), `Accessebility` (supplier's typo, matched by
meaning). One was a supplier data accident, one debatable, one real (`491113`).

Detail in `reports/v5_3_no_heading_review.txt`.

Separately, **93 products (18.6%)** have at least one column filled where no
heading names *that* column — 122 such fills in total. That is a question about
how strict the gate should be, not a defect list, so it is not in the buckets
above.

---

## Method — read before trusting a clean verdict

500 products cannot be read line by line. Every defect class found in the
earlier **100-product hand audit** was turned into a detector
(`scripts/detect_v5_3_issues.py`), the detectors were checked back against those
100 where the answers are already known, then run over all 499. **Every product
they flagged was then opened and read** against its raw description. Five
detector hits were overturned as false positives.

So: the flagged products are hand-verified. The rest mean *"none of the known
defect classes fired"*, which is weaker than *"read and confirmed correct"*.

### A blind spot worth naming

This run was audited **twice, independently**. The second audit found **two real
defects the first one missed** — `634003` and `639882`, both label loss. Both are
in the tables above.

The cause was a rule added mid-audit: *"a line ending in `:` or a short bare
label is not content loss."* That is correct for lead-ins like *"We will provide
you with the following:"* — and it also silenced genuine losses:

> One label introducing one list → safe to drop.
> **Two contrasting labels** (`Departure times` / `Arrival times`) → dropping
> them merges things that must stay apart.

The first audit's detector only flags text **absent** from the output, so it
structurally cannot see a label stripped while its value survives. The second
audit's could.

The second audit also over-reported. Its largest category — 35 products with
blank `min_age` / `group_size` — is **~34 false positives**: `min_age` and
`max_age` are always blank by design (age content goes to `restrictions`), and
in all 11 `group_size` cases the raw had no `Group Size` heading, so blank is
the correct heading-gated answer. It was measuring against "fill every column
the raw mentions" — the standard V5 deliberately abandoned.

**Neither audit alone was right.** Both are reflected above.

---

## Files

| Path | What it is |
|---|---|
| `v5_3_500_audit.xlsx` | 4 sheets — `Priority_Matrix`, `Issues_Only`, `All_Products` (499 with verdict + comment), `Per_Product` (raw beside all 22 columns) |
| `reports/v5_3_hard500_audit.txt` | Full per-product audit, 1.5 MB. Issues first, clean products last |
| `reports/v5_3_no_heading_review.txt` | The 254 no-heading products in the 3 groups above |
| *(batch input not shipped)* | It was 15 MB — the 28 KB system prompt repeated in all 499 requests. Rebuild it exactly with `scripts/build_v5_3_hard500_batch.py` |
| `input/v5_3_hard500_output.jsonl` | Raw Batch API replies |
| `input/hard500_products.json` | The product selection and its ordering rule |
| `prompts/SYSTEM_PROMPT_FH_DESC_V5_3.txt` | The prompt itself |
| `scripts/` | Selection, batch build, scorer, issue detectors, audit comments, report/workbook builders |

---

## What is not fixed — and which phase it belongs to

| # | Open item | Products | Phase | Why |
|---|---|---|---|---|
| 1 | **Content loss** | 3 | 2 | Needs a deterministic post-check, not more prompt wording. Three versions running have each written a stronger rule and it keeps returning somewhere new — the loss is random. |
| 2 | **Label loss** | 4+ | 2 | `634003` and `639882` show the sharper rule needed: contrasting label pairs must survive even where single lead-ins are dropped. Count is provisional — the first audit could not see this class. |
| 3 | **`what_to_bring` line test** | 3 | **2 — the core of Phase 2** | Needs a decision: it means overriding a supplier's own heading a second time (`what_included` already rejects "available for purchase" under `Inclusions:`). |
| 4 | **Difficulty ratings** | 2 | 1 or 2 | Two lines of prompt, no downside. |
| 5 | **Supplier self-duplication** | 10 | neither | De-duplicate at render time. |

None of these block Phase 1.

---

## Reproducing

```bash
python scripts/select_500_hardest.py        # -> hard500_products.json
python scripts/build_v5_3_hard500_batch.py  # -> v5_3_hard500_batch.jsonl
# submit to the OpenAI Batch API, download output
python scripts/score_v5_3.py v5_3_hard500_output.jsonl
python scripts/detect_v5_3_issues.py v5_3_hard500_output.jsonl
python scripts/build_v5_3_500_audit_txt.py
python scripts/build_v5_3_500_workbook.py
```

Scripts expect `find_raw_file` / `strip_html` from
`build_model_comparison_batches.py` and the raw Fareharbor JSON, neither of
which ships here — see the repo root for the dataset.
