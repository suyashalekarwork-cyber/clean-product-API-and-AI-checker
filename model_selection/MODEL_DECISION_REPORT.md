# Which Model Should Run the Fareharbor Extraction?

**Date:** 6 August 2026
**Question:** Replace `gpt-4o-mini`? If so, with what?
**Evidence:** three independent sources — automated measurement, human review, and OpenAI's own documentation.

---

## 1. SUMMARY

Three sources were consulted and **they do not agree**.

| Source | Says the best model is | Confidence |
|---|---|---|
| Automated coverage test (13 models) | **gpt-5.4-nano** — 99.75%, 0 missing | High — but measures only content survival |
| LLM judge (4 models x 2 judges) | **gpt-5.6-terra** — 72.2% placement | **Low — measurement is faulty, see §6** |
| Human review (your workbook notes) | **gpt-5.5-pro / gpt-5.6-terra** pass, **gpt-5.4-nano fails** | High — but 8 products reviewed |
| OpenAI documentation | **gpt-5.4-nano** — named for "data extraction" | Medium — a vendor claim, not a test |

**Two sources favour gpt-5.4-nano. Two favour terra/pro. They are measuring different things.**

The disagreement resolves once you see *what each model gets wrong*:

- **gpt-5.4-nano** never loses content, but **invents and duplicates** it — it emits
  **32% more words than the source contains**.
- **gpt-5.6-terra / gpt-5.5-pro** stay faithful to the source, but **fragment
  sentences** across fields.

### Recommendation

**Switch to `gpt-5.6-terra` if quality is the priority ($487).**
**Switch to `gpt-5.4-nano` only if you first fix its duplication in code ($50).**

**Do not stay on gpt-4o-mini.** It is the only model that loses real content
(26 missing units vs 0-2 for everything else) and its 16K output cap is a
structural risk.

Full reasoning in §7.

---

## 2. COMPARISON OF ALL MODELS

All 27 Batch-capable models, priced for your full 23,034-product catalogue.
13 were tested on 10 identical hard products with prompt V4.4 unchanged.

| Model | Context | In/1M | Out/1M | **23,034 products** | Coverage | Missing |
|---|---|---|---|---|---|---|
| gpt-5-nano | 400K | $0.025 | $0.20 | **$15** | 78.49%* | 56 |
| gpt-4.1-nano | 1M | $0.05 | $0.20 | $19 | 94.74% | 16 |
| **gpt-4o-mini** *(current)* | 128K | $0.075 | $0.30 | **$28** | 89.38% | 26 |
| **gpt-5.6-luna** | 1.05M | $0.10 | $0.60 | **$49** | 98.16% | 2 |
| **gpt-5.4-nano** | 400K | $0.10 | $0.625 | **$50** | **99.75%** | **0** |
| **gpt-5-mini** | 400K | $0.125 | $1.00 | $75 | 99.16% | 1 |
| gpt-4.1-mini | 1M | $0.20 | $0.80 | $75 | 97.76% | 5 |
| gpt-5.4-mini | 400K | $0.375 | $2.25 | $183 | 97.24% | 5 |
| o4-mini | 200K | $0.55 | $2.20 | $207 | 77.24%* | 29 |
| o3-mini | 200K | $0.55 | $2.20 | $207 | not tested | |
| gpt-5 | 400K | $0.625 | $5.00 | $374 | 89.34%* | 36 |
| gpt-5.1 | — | $0.625 | $5.00 | $374 | not tested | |
| gpt-4.1 | 1M | $1.00 | $4.00 | $376 | not tested | |
| o3 | 200K | $1.00 | $4.00 | $376 | not tested | |
| gpt-4o | 128K | $1.25 | $5.00 | $470 | not tested | |
| **gpt-5.6-terra** | 1.05M | $1.00 | $6.00 | **$487** | 99.13% | 1 |
| gpt-5.2 | — | $0.875 | $7.00 | $523 | not tested | |
| gpt-5.4 | 400K | $1.25 | $7.50 | $609 | 98.68% | 2 |
| gpt-5.5 | 1.05M | $2.50 | $15.00 | $1,218 | not tested | |
| gpt-5.6-sol | 1.05M | $2.50 | $15.00 | $1,218 | not tested | |
| o1 | 200K | $7.50 | $30.00 | $2,822 | not tested | |
| o3-pro | — | $10.00 | $40.00 | $3,763 | not tested | |
| gpt-5-pro | — | $7.50 | $60.00 | $4,486 | not tested | |
| gpt-5.2-pro | — | $10.50 | $84.00 | $6,281 | not tested | |
| **gpt-5.5-pro** | 1.05M | $15.00 | $90.00 | **$7,309** | 99.24% | 1 |
| gpt-5.4-pro | — | $15.00 | $90.00 | $7,309 | not tested | |
| o1-pro | — | $75.00 | $300.00 | $28,223 | not tested | |

\* score deflated by truncated or unparseable responses, not by weak extraction.
Measured on clean responses only: gpt-5 99.27%, o4-mini 99.16%, gpt-5-nano 99.14%.
These three are **unreliable, not weak** — they failed 1-3 times out of 10.

### The five finalists, all measurements together

| | gpt-5.4-nano | gpt-5.6-luna | gpt-5-mini | gpt-5.6-terra | gpt-5.5-pro | gpt-4o-mini |
|---|---|---|---|---|---|---|
| **Cost 23k** | **$50** | **$49** | $75 | $487 | $7,309 | $28 |
| **Coverage** | **99.75%** | 98.16% | 99.16% | 99.13% | 99.24% | 89.38% |
| **Missing units** | **0** | 2 | 1 | 1 | 1 | **26** |
| **Judge placement** | 64.8% | not judged | 70.7% | **72.2%** | 67.5% | not judged |
| **Words vs source** | **1.32x** ⚠️ | 0.95x | 0.94x | 0.96x | 1.00x | 0.77x ⚠️ |
| **Markdown junk** | **17** ⚠️ | 15 | 8 | 9 | **2** | 6 |
| **Your verdict** | **FAIL** (1), pass (1) | — | — | **PASS** | **PASS** | — |
| Context | 400K | 1.05M | 400K | 1.05M | 1.05M | **128K** ⚠️ |
| Max output | 128K | 128K | 128K | 128K | 128K | **16K** ⚠️ |
| Knowledge cutoff | Aug 2025 | **Feb 2026** | May 2024 | **Feb 2026** | Dec 2025 | **Oct 2023** ⚠️ |

---

## 3. WHAT I FOUND (automated testing)

**gpt-5.4-nano won the coverage test outright.** 99.75%, the only model with
**zero** missing content units across all 10 products, at $50 — beating
gpt-5.5-pro (99.24%, $7,309) at 1/146th the cost.

**Quality plateaus below $100.** Three models reach ~99% for under $75.
Everything above that buys nothing on this evidence — gpt-4o at $470 and
gpt-5.4 at $609 are not worth testing.

**Your incumbent is the weakest tested model that actually works.**
gpt-4o-mini lost 26 content units where the leaders lost 0-2. It is only
$21-22 cheaper than luna or nano across the entire catalogue.

**Three models are unreliable, not bad.** gpt-5-nano, o4-mini and gpt-5 each
returned truncated or unparseable JSON on some products. All three extract at
~99% when they work. This only surfaced because bad JSON was tracked
separately from quality — scored naively, gpt-5-nano looks like a poor
extractor and is not.

**A regex placement audit ranked gpt-5.4-nano best** (1 HIGH, 4 MEDIUM defects
vs gpt-5.5-pro's 4 HIGH, 19 MEDIUM). **This later proved unreliable** —
three of its seven detectors were confidently wrong and were corrected only by
reading raw text. It disagrees with the LLM judge, and I trust neither fully.

---

## 4. WHAT YOU FOUND (review notes in best_model_13.xlsx)

Eight rows reviewed in `Content_By_Model`. Your verdicts:

| Product | Model | Verdict | Your comment |
|---|---|---|---|
| 63315 | gpt-5.4-nano | **FAIL** | "Trying to find information pro actively (about)" |
| 63315 | gpt-5.4-mini | **FAIL** | |
| 63315 | gpt-5.5-pro | **PASS** | |
| 63315 | gpt-5.6-terra | **PASS** | "terra is between the nano and pro" |
| 451390 | gpt-5.4-nano | — | "pro active. And there are lot of duplicates" |
| 402575 | gpt-5.4-nano | — | "pro active in the what included and excluded. Did extract whats extras in what excluded" |
| 585211 | gpt-5.4-nano | **PASS** | |
| 585211 | gpt-5.4-mini | **PASS** | |

### Your "pro active" observation is measurable, and it is the key finding

You flagged gpt-5.4-nano three separate times for being "pro active" —
inventing or padding content rather than extracting it. Quantified across all
10 products:

| Model | Raw words | Words emitted | **Ratio** | Products emitting >100% of source |
|---|---|---|---|---|
| **gpt-5.4-nano** | 4,007 | 5,272 | **1.32x** | **8 / 10** |
| gpt-5.5-pro | 4,007 | 4,016 | 1.00x | 4 / 10 |
| gpt-5.6-terra | 4,007 | 3,860 | 0.96x | 2 / 10 |
| gpt-5.6-luna | 4,007 | 3,824 | 0.95x | 1 / 10 |
| gpt-5-mini | 4,007 | 3,759 | 0.94x | 1 / 10 |
| gpt-4o-mini | 4,007 | 3,075 | 0.77x | 0 / 10 |

**gpt-5.4-nano emits 32% more words than the supplier actually wrote, on 8 of
10 products.** gpt-5.6-terra sits at 0.96x — almost exactly faithful. Your
comment "terra is between the nano and pro" is precisely right: terra is
faithful like pro, at 1/15th the price.

**This is the single most important number in the report, and the automated
coverage test could not see it.** Coverage asks "did the words survive"; a word
counted twice still counts as present. So duplication *raises* the coverage
score. gpt-5.4-nano's 99.75% is partly earned by the very behaviour you failed
it for.

Your 402575 note was also verified. gpt-5.4-nano put this in
`redo_desc_what_excluded`:

> "Extra children; 3 and under are free. 4 and over are $5 per child. Extra Adult $15 per adult."

That is a **rate card**, not an exclusion list. It belongs in pricing. You
caught a placement error that both the regex audit and the LLM judge scored as
acceptable.

---

## 5. WHAT OPENAI SAYS (official documentation)

| Model | OpenAI's stated purpose |
|---|---|
| **gpt-5.4-nano** | *"designed for tasks where speed and cost matter most like classification, **data extraction**, ranking, and sub-agents"* |
| **gpt-5.6-luna** | *"designed for cost-sensitive, high-volume workloads"* |
| **gpt-5.6-terra** | *"balances intelligence and cost"*; *"roughly corresponds to the mini model tier"* |
| **gpt-5-mini** | *"great for well-defined tasks and precise prompts"* |
| **gpt-5.5-pro** | *"uses more compute to think harder"*; warns requests *"may take several minutes"* |
| **gpt-4o-mini** | *"ideal for fine-tuning"* and distillation from larger models |

**gpt-5.4-nano is the only model where your exact use case — data extraction —
is named in the official description.**

**The full catalogue has only three current text models:** gpt-5.6 Sol
($1,218), Terra ($487), Luna ($49). Everything else is images, voice, or
transcription. **You have already tested two of the three.** The untested one
(Sol) is built for "complex professional work" and costs 24x your current
spend — not worth trying.

### Three specification facts that matter

**gpt-4o-mini caps output at 16,384 tokens — 8x smaller than every other
model here.** Your batch requests already set 8,000. On a long supplier
description with 28 fields to fill, that ceiling is a real truncation risk and
is a likely cause of its 26 missing units.

**gpt-4o-mini's knowledge cutoff is October 2023** — nearly three years stale,
and it is the only finalist with no reasoning support at all.

**Context window is irrelevant to this decision.** Your products average ~6,700
input tokens. Even the smallest window (128K) is 19x more than needed, so
gpt-5.6-terra's 1.05M window is capacity you would pay for and never use.

---

## 6. THE LLM JUDGE — AND WHY ITS SCORES SHOULD NOT DECIDE THIS

A judge was run: 4 models x 2 judges (gpt-5.4-nano + gpt-5.6-terra as bias
control), 80 requests, 0 failures.

| Model | Judge: nano | Judge: terra | Avg |
|---|---|---|---|
| **gpt-5.6-terra** | 66.7% | 77.8% | **72.2%** |
| gpt-5-mini | 68.7% | 72.7% | 70.7% |
| gpt-5.5-pro | 67.0% | 68.0% | 67.5% |
| **gpt-5.4-nano** | 64.3% | 65.3% | **64.8%** |

**Self-bias check passed.** gpt-5.4-nano graded its own output at 64.3% while
terra graded it 65.3% — a gap of **-1.0 points**. It was marginally *harsher*
on itself, so its verdicts are not inflated.

**But the absolute scores are not trustworthy.** Hand-checking flagged fields
against the raw text found the judge penalising models **for following the
extraction prompt**. Product 451390:

> **Text:** `accessibility: For all ages. Pram and wheelchair accessible…`
> **Judge:** WRONG_FIELD, should be `redo_desc_other`

But V4.4's own LABEL MAPPING states:

```
accessibility:          -> redo_desc_requirements
```

The model did exactly what it was instructed to do and was marked wrong. A
second case: text beginning `Kia Ora! Thank you for booking…` was flagged as
filler that "should not have been extracted" — but V4.4 has a NO CONTENT LOSS
RULE requiring the model to keep unclassifiable text.

**The judge grades against its own notion of correct placement, not against
V4.4's rules.** So part of the 27-35% marked wrong is two prompts disagreeing,
not extraction failing.

This affects all four models equally, so **the ranking between them survives**.
What it destroys is any reading of 64.8% or 72.2% as "placement accuracy."

**The 77.5% baseline from the 500-product run is also not comparable** — these
10 products were deliberately selected as the hard set.

---

## 7. CONCLUSION

### The models fail in two different ways, and only one is repairable

**gpt-5.4-nano — over-extraction.** Never loses content (0 missing, best of any
model) but emits 1.32x the source words on 8 of 10 products, leaves markdown in
17 fields, and pads fields with invented framing. **You failed it for exactly
this.**

**gpt-5.6-terra / gpt-5.5-pro / gpt-5-mini — fragmentation.** Faithful to the
source (0.94-1.00x) but split sentences across fields. On product 63315 all
three severed *"Please arrive 15 minutes ahead of your booking time to complete
registration"* into two fields, leaving `"to complete registration."` alone in
`check_in`. gpt-5.4-nano was the **only** model that kept it whole, and the only
one that used the dedicated `faqs` field rather than dumping the FAQ link into
`contact`.

**Duplication and markdown are fixable in code after the fact. Content that was
never extracted is not.** That argues for nano. But **invented content is worse
than either** — it puts words in a supplier's mouth on a live B2B portal, and
no downstream script can detect text that was never in the source.

### Recommendation

> ### ⚠️ SUPERSEDED — the decision is now `gpt-5.6-luna` ($49)
>
> See [`../hard30_run/`](../hard30_run/) for the run that changed it: **30
> hard-selected products, 3 models, a new prompt version (V4.7)**, plus human
> review.
>
> This report recommends gpt-5.6-terra at $487 and treats gpt-5.6-luna as
> "untested, worth one cheap run". Luna has now been tested and reviewed:
> **0.946 word ratio (effectively identical to terra's 0.945), 98.96% coverage,
> and human review passed it on 6 products** — for **$49 instead of $487**.
>
> It is *not* the top scorer — terra remains the cleanest output (1 duplicated
> sentence to luna's 16). The judgement is that terra is the better model but
> not 10x better. Luna's known weaknesses (FAQ handling, occasional invented
> itineraries) are documented in the new report rather than glossed over.
>
> Everything below remains accurate as of when it was written and is kept for
> the audit trail — how the conclusion moved (coverage → placement →
> duplication → cost) is itself the finding.

**Primary: `gpt-5.6-terra` — $487.**
Highest judged placement, faithful to the source at 0.96x, only 1 missing unit,
newest knowledge cutoff (Feb 2026), and **you passed it on review**. Your own
note captures it: *"terra is between the nano and pro"* — pro's fidelity at
1/15th the cost. $487 is 17x your current spend but is a one-off catalogue
cost, not recurring per user.

**Budget alternative: `gpt-5.4-nano` — $50, conditional.**
Only after a deterministic post-processing pass that (a) strips markdown and
(b) removes duplicated text across fields. Both are straightforward. Without
that pass it ships invented content, and you already rejected it once.

**Untested but worth one cheap run: `gpt-5.6-luna` — $49.**
OpenAI's explicit recommendation for high-volume work, 0.95x fidelity (better
than nano), Feb 2026 cutoff, 1.05M context, and the same price as nano. It
ranked 6th on coverage (98.16%, 2 missing) and its whole deficit comes from one
product where it dropped ~20% of the text — a worse failure mode than
duplication, which is why it is not the primary pick. But it has never been
judged or human-reviewed. **One judging run costs cents.**

**Rejected: `gpt-5.5-pro` — $7,309.** Passed your review and is faithful, but
ranks 3rd of 4 on placement, and OpenAI warns requests "may take several
minutes." Impractical across 23,034 products at 146x the cost of nano.

**Rejected: staying on `gpt-4o-mini` — $28.** 26 missing content units, a 16K
output ceiling, an Oct 2023 knowledge cutoff, and no reasoning support. The
saving over luna or nano is ~$21 across the entire catalogue.

### Before committing

1. **Human-review gpt-5.6-terra and gpt-5.6-luna** on the same products you
   already reviewed. Your 8 verdicts found what two automated systems missed;
   more of them is the highest-value evidence available.
2. **Fix the judge** to grade against V4.4's label map, then re-run. Until then
   the judge measures prompt disagreement as much as extraction quality.
3. **Do not run the full catalogue on any model yet.** The `extras:` mapping
   defect (§4, product 402575) is a prompt-level bug affecting ~8 of 11,231
   rows and should be fixed in code first.

---

## 8. LIMITS OF THIS REPORT

- **10 products, deliberately chosen as hard** (7 known-difficult + 3 clean
  controls). Directionally useful; not a production accuracy figure.
- **8 human-reviewed rows** across 4 products. The strongest evidence here, and
  the smallest sample.
- **The judge's absolute numbers are unreliable** (§6). Rankings survive;
  percentages do not.
- **The regex audit contradicts the judge** and both were wrong on cases caught
  by reading raw text. Where automated and human review disagree in this
  report, human review has been treated as correct.
- **13 of 27 models tested.** The untested ones are either far more expensive
  than the plateau point or already superseded.
- Costs assume the measured token shape (6,705 prompt + 2,408 completion per
  product). ~88% of input cost is the V4.4 system prompt resent on every call,
  so cost scales with product **count**, not description length.

**Sources:** [OpenAI Batch pricing](https://developers.openai.com/api/docs/pricing?latest-pricing=batch) ·
[model specifications](https://developers.openai.com/api/docs/models) ·
`best_model_13.xlsx` · `judge_top4.xlsx` · `placement_audit_10_report.txt`