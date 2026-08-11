"""
The reviewer's xlsx deliverable.

    python scripts/build_review_1000_workbook.py --set validation73
    python scripts/build_review_1000_workbook.py --set random1000

Sheets: Summary | Findings | Per_Product | Validation_73

Writes exports/review_v1_{set}.xlsx. openpyxl raises IllegalCharacterError on
the ASCII control characters present in some supplier raw text, so every string
goes through xl() -- same ILLEGAL regex as build_v5_3_500_workbook.py.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = ROOT / "data_pipeline" / "batch_api_test"
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import find_raw_file  # noqa: E402

ILLEGAL = re.compile(r"[\000-\010\013\014\016-\037]")


def xl(v):
    return ILLEGAL.sub("", v) if isinstance(v, str) else v


def product_name(pid):
    try:
        item = json.loads(Path(find_raw_file(pid)).read_text(encoding="utf-8"))["item"]
        return item.get("name") or ""
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="which", choices=["validation73", "random1000"], required=True)
    args = ap.parse_args()

    scores_path = TEST_DIR / ("review_%s_scores.json" % args.which)
    if not scores_path.exists():
        raise SystemExit("missing %s -- run score_review.py first" % scores_path.name)
    data = json.loads(scores_path.read_text(encoding="utf-8"))
    summary, products = data["summary"], data["products"]

    gate2 = {}
    g2_path = TEST_DIR / "review_validation73_gate2.json"
    if g2_path.exists():
        gate2 = json.loads(g2_path.read_text(encoding="utf-8"))

    import review_key as rk
    names = {pid: product_name(pid) for pid in products}

    # ---- Summary -----------------------------------------------------------
    srows = [{"metric": k, "value": json.dumps(v) if isinstance(v, dict) else v}
             for k, v in summary.items()]
    srows.append({"metric": "", "value": ""})
    srows.append({"metric": "penalty weights", "value": json.dumps(data["weights"]["base"])})
    srows.append({"metric": "prompt", "value": "SYSTEM_PROMPT_FH_REVIEW_V1 + _VERIFY_V1"})
    srows.append({"metric": "model", "value": "gpt-5.6-luna"})
    srows.append({"metric": "column contract",
                  "value": "sliced live from SYSTEM_PROMPT_FH_DESC_V5_3"})
    if data.get("schema_warnings"):
        srows.append({"metric": "schema warnings", "value": len(data["schema_warnings"])})
    summary_df = pd.DataFrame(srows)

    # ---- Findings ----------------------------------------------------------
    frows = []
    for pid, p in products.items():
        for f in p["findings"]:
            frows.append({
                "product_id": pid,
                "product_name": xl(names.get(pid, "")),
                "score": p["score"],
                "finding_id": f["finding_id"],
                "check": f["check"],
                "owner": f["owner"],
                "severity": f["severity"],
                "confidence": f["confidence"],
                "verdict": f["verdict"],
                "column": f["column"],
                "target_column": f["target_column"],
                "placement": f["placement"],
                "evidence": xl(f["evidence"]),
                "explanation": xl(f["explanation"]),
                "pass2_reason": xl(f["verdict_reason"]),
                "penalty": f["penalty"],
                "human_class": rk.KEY.get(pid, {}).get("klass", ""),
            })
    findings_df = pd.DataFrame(frows)
    if not findings_df.empty:
        order = {"CONTENT_LOSS": 0, "MISCLASSIFICATION": 1, "LABEL_LOSS": 2,
                 "EMPTY_BUT_HEADING": 3}
        findings_df["_o"] = findings_df["check"].map(order).fillna(9)
        findings_df["_u"] = (findings_df["verdict"] != "UPHELD").astype(int)
        findings_df = (findings_df.sort_values(["_u", "_o", "product_id", "finding_id"])
                       .drop(columns=["_o", "_u"]))

    # ---- Per_Product -------------------------------------------------------
    prows = [{
        "product_id": pid,
        "product_name": xl(names.get(pid, "")),
        "score": p["score"],
        "band": p["band"],
        "penalty_total": p["penalty_total"],
        "n_findings": p["n_findings"],
        "n_upheld_ours": p["n_ours_upheld"],
        "n_supplier": p["n_supplier"],
        "n_rejected": p["n_rejected"],
        "n_uncertain": p["n_uncertain"],
        "checks": ", ".join(sorted({f["check"] for f in p["findings"]})),
        "human_class": rk.KEY.get(pid, {}).get("klass", ""),
    } for pid, p in products.items()]
    per_product_df = (pd.DataFrame(prows)
                      .sort_values(["score", "product_id"])
                      .reset_index(drop=True))

    # ---- Validation_73 -----------------------------------------------------
    if gate2:
        vrows = [{"gate": g["gate"], "got": g["got"], "need": g["need"],
                  "passed": g["passed"], "note": xl(g["note"])[:300]}
                 for g in gate2["gates"]]
        vrows.append({"gate": "", "got": "", "need": "", "passed": "", "note": ""})
        for r in gate2["rows"]:
            vrows.append({
                "gate": "product %s" % r["product_id"],
                "got": "reviewer: %s" % (", ".join(r["checks_upheld_ours"]) or "no OURS finding"),
                "need": "human: %s" % r["human_class"],
                "passed": (r["flagged_ours"] == r["human_is_ours"]),
                "note": "score %d, %d findings" % (r["score"], r["n_findings"]),
            })
        validation_df = pd.DataFrame(vrows)
    else:
        validation_df = pd.DataFrame([{
            "gate": "not run",
            "got": "",
            "need": "",
            "passed": "",
            "note": "run validate_review_vs_human.py to populate this sheet",
        }])

    out = ROOT / "exports" / ("review_v1_%s.xlsx" % args.which)
    out.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out, engine="openpyxl") as xw:
        summary_df.to_excel(xw, sheet_name="Summary", index=False)
        findings_df.to_excel(xw, sheet_name="Findings", index=False)
        per_product_df.to_excel(xw, sheet_name="Per_Product", index=False)
        validation_df.to_excel(xw, sheet_name="Validation_73", index=False)

    print("wrote %s" % out)
    print("  Summary %d rows | Findings %d | Per_Product %d | Validation_73 %d"
          % (len(summary_df), len(findings_df), len(per_product_df), len(validation_df)))


if __name__ == "__main__":
    main()
