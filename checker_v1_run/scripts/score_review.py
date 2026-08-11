"""
Merge pass 1 and pass 2, then score each product.

The score is COMPUTED HERE, not asked of the model -- models are unreliable at
calibrated numbers. The shape is qa_bot_v2/score.py's, unchanged:

    penalty = BASE[check] * SEV[severity] * CONF[confidence] * VERDICT[verdict]
    score   = clamp(round(100 - sum(penalties)), 1, 100)

Only OURS findings are scored. SUPPLIER findings are a verdict about the raw
text, not a defect in the extraction, so they are reported at zero penalty.
Bands come from score_judge_verdicts.review_band -- one source of truth.

    python score_review.py --set validation73
    python score_review.py --set random1000

Writes review_{set}_scores.json.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from build_review_batch import parse_content  # noqa: E402
from score_judge_verdicts import review_band  # noqa: E402

# Penalty weights. Set during validation on the 73 so the known products land in
# sensible bands -- not guessed up front. See REVIEW_PROMPT_LOG.md.
SCORE_BASE = {
    "CONTENT_LOSS": 25,        # the customer loses information outright
    "MISCLASSIFICATION": 15,   # information survives, in the wrong place
    "LABEL_LOSS": 15,          # value survives, unreadable without its label
    "EMPTY_BUT_HEADING": 10,   # supplier headed it, we returned nothing
}
SCORE_SEVERITY = {"major": 1.0, "minor": 0.5}
SCORE_CONFIDENCE = {"high": 1.0, "medium": 0.7, "low": 0.4}
# UNCERTAIN counts half -- same as qa_bot_v2/config.py SCORE_VERDICT.
SCORE_VERDICT = {"UPHELD": 1.0, "UNCERTAIN": 0.5, "REJECTED": 0.0, "": 1.0}

VALID_CHECKS = set(SCORE_BASE)
VALID_VERDICTS = {"UPHELD", "REJECTED", "UNCERTAIN"}


def load(stem, kind):
    path = TEST_DIR / (stem + "_output.jsonl")
    if not path.exists():
        if kind == "verify":
            return {}
        raise SystemExit("missing %s" % path.name)
    out, bad = {}, []
    for line in path.open(encoding="utf-8"):
        row = json.loads(line)
        pid = row["custom_id"].split("|")[0]
        try:
            out[pid] = parse_content(row["response"]["body"]["choices"][0]["message"]["content"])
        except Exception as exc:
            bad.append((pid, str(exc)))
    if bad:
        print("  WARNING unparseable %s rows: %d %s" % (kind, len(bad), bad[:5]))
    return out


def penalty_for(f):
    """Points this finding costs. SUPPLIER and REJECTED always cost nothing."""
    if f["owner"] != "OURS":
        return 0.0
    if f["check"] not in SCORE_BASE:
        return 0.0
    return round(
        SCORE_BASE[f["check"]]
        * SCORE_SEVERITY.get(f["severity"], 1.0)
        * SCORE_CONFIDENCE.get(f["confidence"], 1.0)
        * SCORE_VERDICT.get(f["verdict"], 1.0),
        3,
    )


def merge(reviews, verdicts):
    """Attach pass-2 verdicts to pass-1 findings, by position."""
    products, schema_warnings = {}, []
    for pid, rev in reviews.items():
        raw_findings = rev.get("findings") or []
        vs = (verdicts.get(pid) or {}).get("verdicts") or []
        by_id = {}
        for v in vs:
            try:
                by_id[int(v.get("finding_id"))] = v
            except (TypeError, ValueError):
                continue

        findings = []
        for i, f in enumerate(raw_findings, 1):
            check = (f.get("check") or "").strip()
            owner = (f.get("owner") or "").strip().upper()
            if check not in VALID_CHECKS:
                schema_warnings.append((pid, "unknown check %r" % check))
            if owner not in ("OURS", "SUPPLIER"):
                schema_warnings.append((pid, "unknown owner %r" % owner))
                owner = "SUPPLIER"

            v = by_id.get(i, {})
            verdict = (v.get("verdict") or "").strip().upper()
            if verdict and verdict not in VALID_VERDICTS:
                schema_warnings.append((pid, "unknown verdict %r" % verdict))
                verdict = ""
            correction = (v.get("owner_correction") or "").strip().upper()
            if correction in ("OURS", "SUPPLIER"):
                owner = correction

            rec = {
                "finding_id": i,
                "check": check,
                "owner": owner,
                "severity": (f.get("severity") or "major").strip().lower(),
                "confidence": (f.get("confidence") or "medium").strip().lower(),
                "column": f.get("column") or "",
                "target_column": f.get("target_column") or "",
                "placement": f.get("placement") or "",
                "evidence": f.get("evidence") or "",
                "explanation": f.get("explanation") or "",
                "verdict": verdict or ("UPHELD" if not vs else "UNCERTAIN"),
                "verdict_reason": v.get("reason") or "",
                "verified": bool(v),
            }
            rec["penalty"] = penalty_for(rec)
            findings.append(rec)

        counted = [f for f in findings if f["penalty"] > 0]
        total = round(sum(f["penalty"] for f in findings), 3)
        score = max(1, min(100, round(100 - total)))
        products[pid] = {
            "product_id": pid,
            "score": score,
            "band": review_band(score),
            "penalty_total": total,
            "n_findings": len(findings),
            "n_ours_upheld": sum(1 for f in findings
                                 if f["owner"] == "OURS" and f["verdict"] == "UPHELD"),
            "n_supplier": sum(1 for f in findings if f["owner"] == "SUPPLIER"),
            "n_rejected": sum(1 for f in findings if f["verdict"] == "REJECTED"),
            "n_uncertain": sum(1 for f in findings if f["verdict"] == "UNCERTAIN"),
            "n_scored": len(counted),
            "findings": findings,
        }
    return products, schema_warnings


def summarise(products, n_verified_products):
    findings = [f for p in products.values() for f in p["findings"]]
    ours = [f for f in findings if f["owner"] == "OURS"]
    upheld = [f for f in ours if f["verdict"] == "UPHELD"]
    rejected = [f for f in findings if f["verdict"] == "REJECTED"]
    verified = [f for f in findings if f["verified"]]
    return {
        "products": len(products),
        "products_with_findings": sum(1 for p in products.values() if p["n_findings"]),
        "products_verified_pass2": n_verified_products,
        "products_clean": sum(1 for p in products.values() if not p["n_findings"]),
        "findings_total": len(findings),
        "findings_ours": len(ours),
        "findings_supplier": len(findings) - len(ours),
        "findings_upheld_ours": len(upheld),
        "rejection_rate": round(len(rejected) / len(verified), 4) if verified else None,
        "by_check": dict(Counter(f["check"] for f in upheld)),
        "by_check_all": dict(Counter(f["check"] for f in findings)),
        "by_verdict": dict(Counter(f["verdict"] for f in findings)),
        "by_band": dict(Counter(p["band"] for p in products.values())),
        "mean_score": round(sum(p["score"] for p in products.values())
                            / max(1, len(products)), 2),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="which", choices=["validation73", "random1000"], required=True)
    args = ap.parse_args()

    reviews = load("review_" + args.which, "review")
    verdicts = load("review_verify_" + args.which, "verify")
    print("pass 1: %d products   pass 2: %d products" % (len(reviews), len(verdicts)))

    products, warnings = merge(reviews, verdicts)
    summary = summarise(products, len(verdicts))

    out = TEST_DIR / ("review_%s_scores.json" % args.which)
    out.write_text(json.dumps(
        {"summary": summary, "weights": {"base": SCORE_BASE,
                                         "severity": SCORE_SEVERITY,
                                         "confidence": SCORE_CONFIDENCE,
                                         "verdict": SCORE_VERDICT},
         "schema_warnings": warnings,
         "products": products}, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 70)
    for k, v in summary.items():
        print("  %-26s %s" % (k, v))
    print("=" * 70)
    if warnings:
        print("schema warnings: %d  %s" % (len(warnings), warnings[:8]))
    print("wrote %s" % out.name)

    if summary["rejection_rate"] is not None and summary["rejection_rate"] > 0.5:
        print("\nWATCH: pass 2 rejected %.0f%% of verified findings. If pass 2 is "
              "rejecting most of pass 1, pass 1 is the problem."
              % (100 * summary["rejection_rate"]))


if __name__ == "__main__":
    main()
