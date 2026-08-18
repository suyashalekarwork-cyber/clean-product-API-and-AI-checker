# Judge Results — Top 4 Models by Coverage

Two judges (`gpt-5.4-nano`, `gpt-5.6-terra`) grading the same 10 products,
prompt V4.4, no extraction re-run. Each judge scored separately in
single-judge mode — see *Method* below for why.

## 1. Ranking

| Model | Placement (nano) | Placement (terra) | Avg | Coverage | Cost 23k |
|---|---|---|---|---|---|
| **gpt-5.6-terra** | 66.7% | 77.8% | **72.2%** | 99.13% | $487 |
| gpt-5-mini | 68.7% | 72.7% | **70.7%** | 99.16% | $75 |
| gpt-5.5-pro | 67.0% | 68.0% | **67.5%** | 99.24% | $7,309 |
| gpt-5.4-nano | 64.3% | 65.3% | **64.8%** | 99.75% | $50 |

**Best placement: gpt-5.6-terra at 72.2%.**

## 2. The headline finding

**All four models score far below the 77.5% gpt-4o-mini baseline** from
the 500-product run. On these 10 products the top models place content
correctly only ~64-73% of the time.

That is not a contradiction — these 10 products were selected as the
*hard* set (7 known-difficult + 3 clean controls), while the 77.5%
baseline came from 500 randomly-selected products. Hard products score
worse. The two numbers are not comparable, and neither should be quoted
as 'the' placement accuracy.

**What IS comparable is the four models against each other**, since they
all saw identical inputs and identical judges.

## 3. Self-judging bias: not detected

gpt-5.4-nano graded its own output at **64.3%**, while gpt-5.6-terra graded the same output at **65.3%** — a gap of -1.0 points.

The bias control found no inflation. If anything nano is marginally
*harsher* on itself. Its verdicts can be read at face value here.

## 4. Judge agreement

| Judged model | Fields | Agree | Disagree | Agreement % |
|---|---|---|---|---|
| gpt-5.4-nano | 98 | 76 | 22 | 77.6% |
| gpt-5.5-pro | 103 | 70 | 33 | 68.0% |
| gpt-5-mini | 99 | 72 | 27 | 72.7% |
| gpt-5.6-terra | 99 | 72 | 27 | 72.7% |

The two judges agree on the great majority of fields, and the
model ranking is the same under both — so the ordering does not depend
on which judge you trust.

## 5. Judge vs the regex audit

| Model | Judge avg | Regex HIGH | Regex MEDIUM |
|---|---|---|---|
| gpt-5.6-terra | 72.2% | 3 | 18 |
| gpt-5-mini | 70.7% | 1 | 17 |
| gpt-5.5-pro | 67.5% | 4 | 19 |
| gpt-5.4-nano | 64.8% | 1 | 4 |

The regex audit ranked gpt-5.4-nano best and gpt-5.5-pro worst. The
judge broadly agrees on gpt-5.5-pro being weak, but the spread between
models is far narrower than the regex counts implied. Where they
disagree, **the judge is the better evidence** — regex cannot read
meaning, and three of its detectors were confidently wrong before being
corrected against raw text.

## 6. The judge and the prompt disagree with each other

Hand-checking flagged fields against the raw text found a real problem
with the scores above. Example — product 451390, `redo_desc_requirements`:

> **Text:** `accessibility: For all ages. Pram and wheelchair accessible…`
> **Judge:** WRONG_FIELD, should be `redo_desc_other`

But V4.4's own LABEL MAPPING says:

```
accessibility:          -> redo_desc_requirements
```

The model did exactly what the extraction prompt instructed, and the
judge marked it wrong. **The judge is grading against its own notion of
where content belongs, not against V4.4's rules.**

A second case in the same sample: text beginning `Kia Ora! Thank you for
booking…` was flagged as branding filler that 'should not have been
extracted' — a defensible view, but V4.4 has a NO CONTENT LOSS RULE that
tells the model to keep unclassifiable text rather than drop it.

So part of the 27-35% marked wrong is the two prompts disagreeing, not
the extraction failing. A literal scan for leaked `label:` prefixes
matched only 2 of 240 WRONG_FIELD verdicts, but that scan only catches
cases where the label survived into the text — the true overlap is
larger and is not mechanically countable.

**This affects all four models equally**, so the ranking between them
still holds. What it undermines is reading any absolute number here as
'placement accuracy'.

## 7. Method

**Each judge scored separately, not as a panel.** `score_judge_verdicts.py`
resolves verdicts by majority (`top_n >= 2` and one clear winner). With
exactly two judges, any disagreement produces a 1-1 tie → `DISPUTED`,
which counts as not-correct and would have deflated all four models.
Scoring each judge alone (`single_judge` mode) keeps verdicts intact and
turns the disagreement into a measurement instead of a penalty.

**State files.** gpt-5.5-pro and gpt-5.6-terra had no
`bestmodel_*_post_fix_state.json` — `screen_best_models.py` writes state
only for new candidates and merges baselines verbatim. Their fields were
copied from `bestmodel_screen_results.json` by
`make_baseline_state_files.py`, asserted identical. No re-extraction, no
new extraction API calls.

**gpt-5.4-nano as a judge was untested before this run.** It returned 40/40
parseable responses with zero truncation, so its verdicts are usable —
that was checked, not assumed.

## 8. Limits

- **10 products, deliberately hard.** Directionally useful; not a
  production accuracy figure, and not comparable to the 500-product 77.5%.
- **A judge is one model's opinion, not ground truth.** Two judges make
  disagreement visible; they do not make either one correct.
- **Absolute numbers are unreliable** (section 6): the judge grades against
  its own notion of correct placement, not V4.4's label map, so some
  WRONG_FIELD verdicts penalise the model for obeying the prompt.
- The four models sit within a few points of each other on placement
  while spanning $50 to $7,309 — the placement differences here are
  smaller than the coverage differences, and much smaller than the cost
  differences.
