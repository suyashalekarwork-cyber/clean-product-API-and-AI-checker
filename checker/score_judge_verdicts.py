"""
AI accuracy checker -- Part C: score the four judge outputs by majority vote
and build the workbook.

Majority rule per (product_id, field):
  - final_verdict = the verdict with >=2 votes among models that returned a
    parseable verdict for that field.
  - ties / no verdict reaching 2 -> DISPUTED.
  - a model that did not return a verdict for a field is NO_VOTE. It is never
    silently counted as CORRECT, and it lowers n_models for that row.

Scope is placement only, so the headline metric is named placement_accuracy_pct
-- it is NOT an overall extraction-quality score (it says nothing about
hallucinated or dropped content).

Review bands (assigned per product from placement_accuracy_pct):
  100-80  NO_HUMAN_NEEDED        ship as-is
   80-70  MAYBE_REVIEW           spot-check
   70-0   HIGHLY_RECOMMENDED     needs a human
Boundaries are inclusive at the top of each band: >=80 no human, >=70 maybe,
below 70 highly recommended.

Usage:
    python score_judge_verdicts.py
    python score_judge_verdicts.py --limit 5
    python score_judge_verdicts.py --run v500 --models gpt-5.5-pro
"""
import sys
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd

from judge_fields import VALID_VERDICTS, VALID_SHOULD_BE

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ALL_MODELS = ["gpt-4o-mini", "gpt-5.4", "gpt-5.5-pro", "gpt-5.6-terra"]

NO_VOTE = "NO_VOTE"
DISPUTED = "DISPUTED"

# Human-review triage bands, applied to a product's placement_accuracy_pct.
BAND_NO_HUMAN = "NO_HUMAN_NEEDED"
BAND_MAYBE = "MAYBE_REVIEW"
BAND_HIGHLY = "HIGHLY_RECOMMENDED"
BAND_ORDER = [BAND_NO_HUMAN, BAND_MAYBE, BAND_HIGHLY]


def review_band(pct):
    """100-80 -> no human; 80-70 -> maybe; below 70 -> highly recommended."""
    if pct >= 80:
        return BAND_NO_HUMAN
    if pct >= 70:
        return BAND_MAYBE
    return BAND_HIGHLY


def parse_content(txt):
    """Unwrap optional markdown fencing and parse the judge's JSON reply."""
    t = txt.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        t = t.removeprefix("json").strip()
        if t.endswith("```"):
            t = t[: t.rfind("```")]
    return json.loads(t.strip())


def load_model_verdicts(model, suffix):
    """-> {(pid, field): verdict_dict}, plus a parse-failure count."""
    path = TEST_DIR / f"judge_output_{model}{suffix}.jsonl"
    out, failures = {}, 0
    if not path.exists():
        print(f"  WARNING: {path.name} missing — all its votes will be NO_VOTE")
        return out, failures
    for line in path.open(encoding="utf-8"):
        rec = json.loads(line)
        pid = rec["custom_id"].split("|")[0]
        try:
            body = rec["response"]["body"]["choices"][0]["message"]["content"]
            data = parse_content(body)
            for v in data["verdicts"]:
                field = v.get("field", "")
                verdict = str(v.get("verdict", "")).upper().strip()
                if verdict not in VALID_VERDICTS:
                    continue
                should_be = str(v.get("should_be", "") or "").strip()
                if should_be not in VALID_SHOULD_BE:
                    should_be = ""  # judge named a field that does not exist
                out[(pid, field)] = {
                    "verdict": verdict,
                    "should_be": should_be,
                    "offending_text": str(v.get("offending_text", "") or ""),
                    "reason": str(v.get("reason", "") or ""),
                }
        except Exception:
            failures += 1
    return out, failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--run", default="v50", help="v50 | v500")
    ap.add_argument("--models", nargs="+", default=ALL_MODELS)
    args = ap.parse_args()
    suffix = f"_{args.run}" + (f"_limit{args.limit}" if args.limit else "")

    global MODELS
    MODELS = args.models
    single_judge = len(MODELS) == 1

    state_path = TEST_DIR / f"{args.run}_post_fix_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    pids = list(state)
    if args.limit:
        pids = pids[: args.limit]

    # Ground truth: every non-empty field that was sent for judging.
    judged_keys = []
    text_of = {}
    for pid in pids:
        for f, v in state[pid]["field_values"].items():
            if v and str(v).strip():
                judged_keys.append((pid, f))
                text_of[(pid, f)] = str(v)
    print(f"Non-empty fields expected: {len(judged_keys)}")

    per_model, parse_failures = {}, {}
    for m in MODELS:
        per_model[m], parse_failures[m] = load_model_verdicts(m, suffix)
        print(f"  {m:16s} verdicts={len(per_model[m])} parse_failures={parse_failures[m]}")

    rows = []
    agreement_hits = Counter()
    agreement_opps = Counter()

    for key in judged_keys:
        pid, field = key
        votes = {}
        for m in MODELS:
            votes[m] = per_model[m].get(key)

        cast = {m: v["verdict"] for m, v in votes.items() if v}
        counts = Counter(cast.values())
        n_models = len(cast)

        if not cast:
            final, agree = NO_VOTE, ""
        elif single_judge:
            # One judge: its verdict stands as-is. No majority, so no DISPUTED.
            final = next(iter(cast.values()))
            agree = "1/1"
        else:
            top, top_n = counts.most_common(1)[0]
            tied = [v for v, c in counts.items() if c == top_n]
            if top_n >= 2 and len(tied) == 1:
                final = top
                agree = f"{top_n}/{n_models}"
            else:
                final = DISPUTED
                agree = f"{top_n}/{n_models}"

        # should_be consensus among models that said WRONG_FIELD
        sb = [v["should_be"] for v in votes.values()
              if v and v["verdict"] == "WRONG_FIELD" and v["should_be"]]
        sb_consensus = Counter(sb).most_common(1)[0][0] if sb else ""

        # supporting evidence from a model that voted with the majority
        off = reason = ""
        for m in MODELS:
            v = votes[m]
            if v and v["verdict"] == final and final not in ("CORRECT", DISPUTED, NO_VOTE):
                off, reason = v["offending_text"], v["reason"]
                break
        if final == DISPUTED:
            for m in MODELS:
                v = votes[m]
                if v and v["verdict"] != "CORRECT" and v["reason"]:
                    off, reason = v["offending_text"], v["reason"]
                    break

        for m in MODELS:
            if votes[m]:
                agreement_opps[m] += 1
                if final not in (DISPUTED, NO_VOTE) and votes[m]["verdict"] == final:
                    agreement_hits[m] += 1

        row = {
            "product_id": pid,
            "field": field,
            "extracted_text": text_of[key][:2000],
            "final_verdict": final,
            "agreement": agree,
            "n_models": n_models,
            "should_be_consensus": sb_consensus,
            "offending_text": off[:1000],
            "reason": reason[:1000],
        }
        for m in MODELS:
            row[f"vote_{m}"] = votes[m]["verdict"] if votes[m] else NO_VOTE
        rows.append(row)

    verdicts_df = pd.DataFrame(rows)

    # --- verification assert: coverage is exact, no dupes, none lost ---
    assert len(verdicts_df) == len(judged_keys), "row count != non-empty field count"
    assert not verdicts_df.duplicated(["product_id", "field"]).any(), "duplicate rows"

    # --- Summary ---
    summary = []
    for pid in pids:
        sub = verdicts_df[verdicts_df.product_id == pid]
        n = len(sub)
        correct = int((sub.final_verdict == "CORRECT").sum())
        pct = round(100 * correct / n, 1) if n else 0.0
        summary.append({
            "product_id": pid,
            "fields_judged": n,
            "correct": correct,
            "wrong_field": int((sub.final_verdict == "WRONG_FIELD").sum()),
            "garbled": int((sub.final_verdict == "GARBLED").sum()),
            "disputed": int((sub.final_verdict == DISPUTED).sum()),
            "no_vote": int((sub.final_verdict == NO_VOTE).sum()),
            "placement_accuracy_pct": pct,
            "review_band": review_band(pct),
        })
    summary_df = pd.DataFrame(summary).sort_values("placement_accuracy_pct")

    # --- Review bands ---
    band_counts = summary_df.review_band.value_counts()
    bands_df = pd.DataFrame([{
        "review_band": b,
        "score_range": {BAND_NO_HUMAN: "80-100", BAND_MAYBE: "70-79.9",
                        BAND_HIGHLY: "0-69.9"}[b],
        "action": {BAND_NO_HUMAN: "No human needed — ship as-is",
                   BAND_MAYBE: "Maybe — spot-check",
                   BAND_HIGHLY: "Human review highly recommended"}[b],
        "products": int(band_counts.get(b, 0)),
        "pct_of_products": round(100 * int(band_counts.get(b, 0)) / len(summary_df), 1),
        "fields_in_band": int(summary_df[summary_df.review_band == b].fields_judged.sum()),
    } for b in BAND_ORDER])

    # --- Flagged only ---
    flagged = verdicts_df[verdicts_df.final_verdict != "CORRECT"].copy()
    flagged["_agree_n"] = flagged.agreement.str.split("/").str[0]
    flagged = flagged.sort_values(["_agree_n", "product_id"]).drop(columns="_agree_n")

    # --- Model agreement ---
    model_df = pd.DataFrame([{
        "model": m,
        "verdicts_returned": agreement_opps[m],
        "matched_majority": agreement_hits[m],
        "majority_agreement_pct": round(100 * agreement_hits[m] / agreement_opps[m], 1)
        if agreement_opps[m] else 0.0,
        "parse_failures": parse_failures[m],
        "flag_rate_pct": round(
            100 * sum(1 for k in judged_keys
                      if per_model[m].get(k) and per_model[m][k]["verdict"] != "CORRECT")
            / max(agreement_opps[m], 1), 1),
    } for m in MODELS])

    # Human review queue: every product needing eyes, worst first.
    needs_human = summary_df[summary_df.review_band != BAND_NO_HUMAN]

    xlsx = TEST_DIR / f"judge_accuracy{suffix}.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
        bands_df.to_excel(w, sheet_name="Review_Bands", index=False)
        summary_df.to_excel(w, sheet_name="Summary", index=False)
        needs_human.to_excel(w, sheet_name="Needs_Human", index=False)
        verdicts_df.to_excel(w, sheet_name="Field_Verdicts", index=False)
        flagged.to_excel(w, sheet_name="Flagged_Only", index=False)
        model_df.to_excel(w, sheet_name="Model_Agreement", index=False)

    csv = TEST_DIR / f"judge_accuracy{suffix}_field_verdicts.csv"
    verdicts_df.to_csv(csv, index=False, encoding="utf-8")

    total = len(verdicts_df)
    dist = verdicts_df.final_verdict.value_counts()
    overall = round(100 * int(dist.get("CORRECT", 0)) / total, 1)

    judge_line = (
        f"Judge: single model `{MODELS[0]}` — its verdict stands alone (no vote, "
        "so no DISPUTED category and no cross-check on outliers)."
        if single_judge else
        f"Judges: {', '.join(MODELS)} — majority vote (>=2 of the models that responded)."
    )

    md = [
        f"# AI Placement-Accuracy Checker — {args.run} ({len(pids)} products)",
        "",
        "Scope: **placement only** — does each extracted field's text belong under",
        "that field name? This does NOT check faithfulness to the raw text and does",
        "NOT look for content dropped entirely, so the score below is a placement",
        "accuracy figure, not an overall extraction-quality score.",
        "",
        judge_line,
        "",
        "## Human-review bands (per product)",
        "",
        "| band | score | action | products | % | fields |",
        "|---|---|---|---|---|---|",
    ] + [
        f"| **{r.review_band}** | {r.score_range} | {r.action} | {r.products} | "
        f"{r.pct_of_products}% | {r.fields_in_band} |"
        for _, r in bands_df.iterrows()
    ] + [
        "",
        f"- Fields judged: **{total}** across {len(pids)} products",
        f"- Placement accuracy: **{overall}%** ({int(dist.get('CORRECT', 0))} CORRECT)",
        f"- WRONG_FIELD: {int(dist.get('WRONG_FIELD', 0))}",
        f"- GARBLED: {int(dist.get('GARBLED', 0))}",
        f"- DISPUTED (no majority): {int(dist.get(DISPUTED, 0))}",
        f"- NO_VOTE (no model returned a verdict): {int(dist.get(NO_VOTE, 0))}",
        "",
        "## Most-flagged fields",
        "",
        "| field | flagged | judged | flag rate |",
        "|---|---|---|---|",
    ]
    fl = verdicts_df.assign(bad=verdicts_df.final_verdict != "CORRECT")
    g = fl.groupby("field").agg(flagged=("bad", "sum"), judged=("bad", "size"))
    g = g[g.flagged > 0].sort_values("flagged", ascending=False)
    for f, r in g.iterrows():
        md.append(f"| `{f}` | {int(r.flagged)} | {int(r.judged)} | "
                  f"{round(100*r.flagged/r.judged)}% |")
    md += ["", "## Model agreement with the majority", "",
           "| model | verdicts | matched majority | parse failures | flag rate |",
           "|---|---|---|---|---|"]
    for _, r in model_df.iterrows():
        md.append(f"| {r.model} | {r.verdicts_returned} | {r.majority_agreement_pct}% | "
                  f"{r.parse_failures} | {r.flag_rate_pct}% |")

    md_path = TEST_DIR / f"judge_accuracy{suffix}_summary.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"\nFields judged: {total}")
    print(f"Placement accuracy: {overall}%")
    print(dist.to_string())
    print(f"\nWrote:\n  {xlsx.name}\n  {csv.name}\n  {md_path.name}")


if __name__ == "__main__":
    main()
