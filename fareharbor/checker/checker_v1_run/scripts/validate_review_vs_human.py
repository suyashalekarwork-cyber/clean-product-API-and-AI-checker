"""
Gate 2 -- the accuracy gate the old judge never passed.

The old judge flagged 22.5% of fields as WRONG_FIELD across 500 products and
nobody ever measured whether it was right. judge_validation_30.xlsx, the sheet
built to answer that, is an empty 5-row stub.

This scores the reviewer against 73 products a human actually read.

    python validate_review_vs_human.py

Reads review_validation73_scores.json, writes review_validation73_gate2.json.
Exit code 1 if any gate fails -- do NOT proceed to the 1,000 on a failure.
Fix the prompt, append a new version, re-run the 73, and log it in
REVIEW_PROMPT_LOG.md.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

import review_key as rk  # noqa: E402

SCORES = TEST_DIR / "review_validation73_scores.json"
OUT = TEST_DIR / "review_validation73_gate2.json"

# Gates, with the prior art each was set from.
GATE_MAX_FP_ON_OK = 2        # union+verifier false-alarm rate 0.038
GATE_MIN_RECALL = 0.70       # qa_bot_v2 recall 0.700
GATE_MIN_PRECISION = 0.64    # qa_bot_v2 precision 0.638
GATE_MAX_AGE_FLAGS = 0       # the ~34-of-35 false-positive class
GATE_MIN_PROBES = 3          # of 4 -- the blind spot this build exists for

AGE_COLUMNS = {"redo_min_age", "redo_max_age"}

# Human class -> reviewer checks that count as having found it.
CLASS_TO_CHECKS = {
    "CONTENT_LOSS": {"CONTENT_LOSS"},
    "MISCLASS": {"MISCLASSIFICATION", "LABEL_LOSS", "EMPTY_BUT_HEADING"},
    "LABEL_LOSS": {"LABEL_LOSS", "MISCLASSIFICATION"},
}


def upheld_ours(p):
    return [f for f in p["findings"] if f["owner"] == "OURS" and f["verdict"] == "UPHELD"]


def any_upheld(p):
    return [f for f in p["findings"] if f["verdict"] == "UPHELD"]


def main():
    if not SCORES.exists():
        raise SystemExit("missing %s -- run score_review.py --set validation73 first"
                         % SCORES.name)
    rk.check()
    data = json.loads(SCORES.read_text(encoding="utf-8"))
    products = data["products"]

    missing = [p for p in rk.KEY if p not in products]
    if missing:
        raise SystemExit("no reviewer output for %d key products: %s"
                         % (len(missing), missing[:10]))

    rows = []
    for pid, k in sorted(rk.KEY.items(), key=lambda kv: kv[1]["klass"]):
        p = products[pid]
        ours = upheld_ours(p)
        rows.append({
            "product_id": pid,
            "human_class": k["klass"],
            "human_is_ours": k["is_ours"],
            "run": k["run"],
            "score": p["score"],
            "band": p["band"],
            "n_findings": p["n_findings"],
            "n_upheld_ours": len(ours),
            "n_upheld_any": len(any_upheld(p)),
            "checks_upheld_ours": sorted({f["check"] for f in ours}),
            "checks_all": sorted({f["check"] for f in p["findings"]}),
            "flagged_ours": bool(ours),
        })
    by_pid = {r["product_id"]: r for r in rows}

    # --- Gate A: false positives on the 15 OK products -----------------------
    fp = [r for r in rows if r["human_class"] == "OK" and r["flagged_ours"]]
    gate_a = len(fp) <= GATE_MAX_FP_ON_OK

    # --- Gate B: recall on the 23 OURS defects -------------------------------
    defects = [r for r in rows if r["human_is_ours"]]
    found = [r for r in defects if r["flagged_ours"]]
    recall = len(found) / len(defects)
    gate_b = recall >= GATE_MIN_RECALL

    class_found = [r for r in defects
                   if set(r["checks_upheld_ours"]) & CLASS_TO_CHECKS[r["human_class"]]]
    class_recall = len(class_found) / len(defects)

    # --- Gate C: precision -----------------------------------------------------
    # Product-level: of the products the reviewer accuses of a defect, how many
    # does the human key also record a defect on?
    #
    # MINOR counts as a true positive. The human class MINOR means "defensible,
    # but worth a look" -- i.e. the human DID record a defect there (198064's
    # marketing line in what_included, 501920's marketing line in extras).
    # Counting an agreeing finding on those as a false alarm would be wrong on
    # the merits. MINOR is excluded from RECALL, which is defined over the 23
    # OURS defects only; this affects the denominator of precision alone.
    #
    # SUPPLIER stays a negative: the reviewer claiming OURS where the human
    # ruled the supplier's own text caused it is a genuine disagreement and
    # should count against precision. Still conservative -- the key holds one
    # label per product, so a real second defect on a SUPPLIER product reads as
    # a false positive here.
    accused = [r for r in rows if r["flagged_ours"]]
    tp = [r for r in accused if r["human_is_ours"] or r["human_class"] == "MINOR"]
    precision = len(tp) / len(accused) if accused else 0.0
    gate_c = precision >= GATE_MIN_PRECISION
    strict_tp = [r for r in accused if r["human_is_ours"]]
    strict_precision = len(strict_tp) / len(accused) if accused else 0.0

    # --- Gate D: age-column flags ---------------------------------------------
    age_raised, age_upheld = [], []
    for pid, p in products.items():
        for f in p["findings"]:
            if {f["column"], f["target_column"]} & AGE_COLUMNS:
                age_raised.append((pid, f["check"], f["column"], f["verdict"]))
                if f["verdict"] == "UPHELD":
                    age_upheld.append((pid, f["check"], f["column"]))
    gate_d = len(age_upheld) <= GATE_MAX_AGE_FLAGS

    # --- Gate E: the label-loss probes ----------------------------------------
    probes = {}
    for pid in rk.LABEL_LOSS_PROBES:
        r = by_pid[pid]
        hit = bool(set(r["checks_upheld_ours"]) & {"LABEL_LOSS", "MISCLASSIFICATION"})
        probes[pid] = {"human_class": r["human_class"],
                       "checks": r["checks_upheld_ours"], "found": hit}
    n_probes = sum(1 for v in probes.values() if v["found"])
    gate_e = n_probes >= GATE_MIN_PROBES

    gates = [
        ("A  false positives on the %d OK products" % len(rk.OK_PRODUCTS),
         "%d" % len(fp), "<= %d" % GATE_MAX_FP_ON_OK, gate_a,
         ", ".join(r["product_id"] for r in fp)),
        ("B  recall on the %d OURS defects" % len(defects),
         "%.3f (%d/%d)" % (recall, len(found), len(defects)),
         ">= %.2f" % GATE_MIN_RECALL, gate_b,
         "missed: " + ", ".join(r["product_id"] for r in defects if not r["flagged_ours"])),
        ("C  precision on accused products",
         "%.3f (%d/%d)" % (precision, len(tp), len(accused)),
         ">= %.2f" % GATE_MIN_PRECISION, gate_c,
         "strict (MINOR as negative): %.3f" % strict_precision),
        ("D  min_age/max_age blanks upheld",
         "%d (raised %d)" % (len(age_upheld), len(age_raised)),
         "== %d" % GATE_MAX_AGE_FLAGS, gate_d, str(age_upheld[:5])),
        ("E  label-loss probes found",
         "%d/4" % n_probes, ">= %d" % GATE_MIN_PROBES, gate_e,
         ", ".join("%s:%s" % (k, "HIT" if v["found"] else "MISS")
                   for k, v in sorted(probes.items()))),
    ]

    print("=" * 92)
    print("GATE 2 -- reviewer vs 73 hand-verified products")
    print("=" * 92)
    print("  pass-1 findings: %d   upheld OURS: %d   rejection rate: %s"
          % (data["summary"]["findings_total"],
             data["summary"]["findings_upheld_ours"],
             data["summary"]["rejection_rate"]))
    print("  class-matched recall (secondary, not a gate): %.3f (%d/%d)"
          % (class_recall, len(class_found), len(defects)))
    print()
    for name, got, need, ok, note in gates:
        print("  [%s] %-42s %-18s need %s" % ("PASS" if ok else "FAIL", name, got, need))
        if note.strip(" ,:"):
            print("         %s" % note[:160])

    print("\n  per-class detection")
    for cls in ("CONTENT_LOSS", "MISCLASS", "LABEL_LOSS", "SUPPLIER", "MINOR", "OK"):
        grp = [r for r in rows if r["human_class"] == cls]
        if not grp:
            continue
        hit = sum(1 for r in grp if r["flagged_ours"])
        anyf = sum(1 for r in grp if r["n_findings"])
        print("    %-13s %2d products   OURS-upheld on %2d   any finding on %2d"
              % (cls, len(grp), hit, anyf))

    passed = all(g[3] for g in gates)
    OUT.write_text(json.dumps({
        "passed": passed,
        "gates": [{"gate": n, "got": g, "need": nd, "passed": ok, "note": note}
                  for n, g, nd, ok, note in gates],
        "recall": recall, "class_recall": class_recall, "precision": precision,
        "false_positives_on_ok": [r["product_id"] for r in fp],
        "missed_defects": [r["product_id"] for r in defects if not r["flagged_ours"]],
        "probes": probes,
        "age_flags_raised": age_raised,
        "rows": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 92)
    if passed:
        print("GATE 2 PASSED -- clear to run the 1,000")
    else:
        print("GATE 2 FAILED -- fix the prompt, append a new version, re-run the 73 ONLY.")
        print("Log the failure and the fix in REVIEW_PROMPT_LOG.md.")
    print("wrote %s" % OUT.name)
    print("=" * 92)
    print("\nLIMITATION: recall here is recall against KNOWN defects. The 952 "
          "never-hand-read\nproducts are not an answer key -- findings outside "
          "these 73 need reading, not counting.")
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
