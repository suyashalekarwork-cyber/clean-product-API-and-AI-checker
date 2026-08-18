# Best Model for This Task — 13 Models, 10 Identical Products

Prompt V4.4, unchanged. No paste fix, no judge. 9 new models tested; 4 models
already measured on these exact products are merged in as free baselines.

## 1. HEADLINE RANKING

| Rank | Model | Coverage | MISSING | 23,034 products | Status |
|---|---|---|---|---|---|
| 1 | **gpt-5.4-nano** | **99.75%** | **0** | **$50** | NEW |
| 2 | gpt-5.5-pro | 99.24% | 1 | $7,309 | baseline |
| 3 | **gpt-5-mini** | 99.16% | 1 | $75 | NEW |
| 4 | gpt-5.6-terra | 99.13% | 1 | $487 | baseline |
| 5 | gpt-5.4 | 98.68% | 2 | $609 | baseline |
| 6 | **gpt-5.6-luna** | 98.16% | 2 | **$49** | NEW |
| 7 | gpt-4.1-mini | 97.76% | 5 | $75 | NEW |
| 8 | gpt-5.4-mini | 97.24% | 5 | $183 | NEW |
| 9 | gpt-4.1-nano | 94.74% | 16 | $19 | NEW |
| 10 | gpt-4o-mini *(current)* | 89.38% | 26 | $28 | baseline |
| 11 | gpt-5 | 89.34%* | 36 | $374 | NEW — unreliable |
| 12 | gpt-5-nano | 78.49%* | 56 | $15 | NEW — unreliable |
| 13 | o4-mini | 77.24%* | 29 | $207 | NEW — unreliable |

\* deflated by response failures — see section 3.

## 2. THE RESULT

**gpt-5.4-nano beats gpt-5.5-pro at 1/146th the cost.** 99.75% coverage, the
only model with **zero** missing units across all 10 products, for **$50** to
process all 23,034 products versus $7,309.

Against the current gpt-4o-mini: **+10.4 coverage points, 26 missing units → 0,
for $22 more** across the entire catalogue. That is not a trade-off; it is
strictly better on both axes that matter.

Three models land at ~99% for under $75: gpt-5.4-nano ($50), gpt-5.6-luna ($49),
gpt-5-mini ($75). **Quality plateaus well below $100** — everything above that
buys nothing on this evidence.

## 3. Three models are unreliable, not bad

`gpt-5-nano`, `o4-mini` and `gpt-5` each failed to return usable output on some
products — truncated responses or unparseable JSON. Because a failed response
counts as total content loss, their headline coverage is misleading.

Measured only on products where they actually responded:

| Model | All 10 products | Clean responses only | Failed |
|---|---|---|---|
| gpt-5 | 89.34% | **99.27%** | 1/10 |
| o4-mini | 77.24% | **99.16%** | 3/10 |
| gpt-5-nano | 78.49% | **99.14%** | 3/10 |

So all three extract at ~99% *when they work*. Their problem is **reliability,
not capability**. gpt-5-nano in particular is the cheapest model available at
$15, and it is genuinely capable — it just failed 3 of 10 times, which
disqualifies it for production without a retry layer.

This distinction only surfaced because bad-JSON and truncation were tracked as
separate outcomes from quality. Scored naively, gpt-5-nano looks like a poor
extractor; it is not.

## 4. A caveat on gpt-5.4-nano's perfect score

Reading its actual output rather than trusting the number: on product 391584 it
reached 100% coverage partly by **duplicating content** — the same text appears
in both `redo_desc_what_excluded` and `redo_desc_other` — and it left markdown
(`**bold**`, `##headers`) in several fields.

Coverage rewards duplication, because a word counted twice still counts as
present. So 99.75% is real but slightly flattering. gpt-5.5-pro's 99.24% comes
from cleaner, non-duplicated output.

This does not change the recommendation — gpt-5.4-nano still loses no content
and costs $50 — but it is exactly the kind of thing coverage cannot see, and it
is why the judge matters.

## 5. What this measurement cannot tell you

**Coverage measures content survival, not correctness of placement.**
gpt-5.5-pro scored 99.58% coverage on a separate 50-product run but only 74.5%
placement accuracy when judged. The same gap almost certainly exists here.

No judge has been run on these 13 models. The state files are already named for
it, so judging is three commands per model when wanted:
```
python build_judge_batches.py  --run bestmodel_{model} --models gpt-5.6-terra
python run_judge_batches.py    --run bestmodel_{model} --models gpt-5.6-terra
python score_judge_verdicts.py --run bestmodel_{model} --models gpt-5.6-terra
```

**Empty-field counts are near-identical across all models** (17.3-21.0 of 28
fields empty on average), so no model is winning by dumping everything into one
catch-all — a failure mode coverage would otherwise reward.

## 6. Verification

| Check | Result |
|---|---|
| State files == screen output (no fix applied) | PASS |
| Extracted text traces to raw source (no invention) | PASS |
| The 4 existing baselines unchanged by the merge | PASS |
| Every model answered every product/side | FAIL — 7 cases (reported above) |
| No truncated responses | FAIL — 4 cases (reported above) |
| All responses parseable JSON | FAIL — 7 cases (reported above) |

The three failures are **model behaviour, not pipeline defects** — they are the
finding in section 3, not a reason to distrust the numbers. Integrity
assertions all passed.

Prompts and user messages were verified byte-identical to the original run
before submitting, so the 4 merged baselines are genuinely comparable.

## 7. PLACEMENT AUDIT — added after this report was first written

Section 5 above said no placement score existed. One has since been produced:
`placement_audit_10_report.txt` (from `audit_placement_10.py`), auditing the
top 3 models + gpt-5.6-terra + the incumbent on all 10 products for WHERE
content landed, not whether it survived.

| Model | HIGH | MEDIUM | LOW | Coverage | Cost 23k |
|---|---|---|---|---|---|
| **gpt-5.4-nano** | **1** | **4** | 18 | 99.75% | $50 |
| gpt-4o-mini *(current)* | 2 | 8 | 6 | 89.38% | $28 |
| gpt-5-mini | 1 | 17 | 8 | 99.16% | $75 |
| gpt-5.6-terra | 3 | 18 | 9 | 99.13% | $487 |
| gpt-5.5-pro | 4 | 19 | 2 | 99.24% | $7,309 |

**gpt-5.4-nano wins on placement AND coverage** — the only model that does
both. It confirms the recommendation below on independent evidence.

**gpt-5.5-pro has the WORST placement record of the five** despite ranking 2nd
on coverage, at $7,309. Coverage and placement are close to uncorrelated: a
model can preserve every word and still file half of them wrong.

**One defect found here is in the prompt, not any model.** V4.4 maps the raw
label `extras:` to `redo_desc_what_excluded`, assuming "extras" means paid
add-ons. On product 451390 it means a *complimentary* shuttle bus and free
low-sensory sessions — so the output states the opposite of the source. Because
V4.4 declares the mapping "authoritative and overrides your own judgment", the
two most expensive models tested both obeyed it and both got it wrong. No
choice of model fixes it.

**Scale of that defect, measured across the full dataset** (all 11,231
Fareharbor rows, not just these 10 products):

| `extras:` section contains | Rows | V4.4 verdict |
|---|---|---|
| Paid signals only | 438 | correct — genuinely not included |
| Ambiguous (no clear signal) | 407 | unknowable from keywords |
| **Free signals only** | **8** | **misfiled** |
| Mixed free + paid | 9 | needs sentence-level handling |

862 products carry an `extras:` section and only **8 (0.9%) are clearly
misfiled**. So the mapping is right in the large majority of cases. The defect
is real and customer-facing on those 8, but it is NOT a pipeline-wide problem —
an earlier draft of this report called it "the single largest defect" on the
strength of one product, before the frequency was measured. That was wrong.

Consequence for the fix: a prompt-version bump is poor value here (a full
re-run and re-validation to correct 8 rows), and narrowing rules is exactly
what caused the V4.6 regression, where added rules made the model drop content
instead of routing it to the catch-all. A deterministic post-hoc correction —
move free-signal text out of `what_excluded` into `what_included` — fixes all 8
with no re-run and no regression risk.

## 8. Recommendation

**Switch to gpt-5.4-nano.** $50 for all 23,034 products, zero missing content,
best placement record, and it outperforms a model costing 146x more.

Before committing to a full run:
1. **Strip markdown in code.** gpt-5.4-nano leaves `**`/`##` in 17 fields, the
   worst of any model — cosmetic, trivially fixable, zero risk. Highest
   value-per-effort item on this list.
2. **Fix the 8 misfiled `extras:` rows in code**, not in the prompt — move
   free-signal text out of `what_excluded` into `what_included`. Deterministic,
   no re-run, no regression risk. A V4.7 prompt bump is not justified for 0.9%
   of rows (see section 7).
3. **Check the duplication behaviour** (section 4) on a wider sample.
4. An LLM judge has still NOT been run on these models. The audit above is
   rule-based detection: it finds defects it was told to look for and misses
   types nobody has named. Absence of a finding is not proof of correct
   placement. This repo's own `checker/` is the tool for that job.

Do not pursue gpt-5.5-pro. On this evidence it is not the best model for this
task even ignoring cost — gpt-5.4-nano beat it on both content and placement.
