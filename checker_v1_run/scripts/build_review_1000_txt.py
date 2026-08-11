"""
The reviewer's txt deliverable -- findings first, clean products last.

Same shape as build_v5_3_random1000_txt.py, but this reports what the CHECKER
found, not what the extractor produced.

    python scripts/build_review_1000_txt.py --set validation73
    python scripts/build_review_1000_txt.py --set random1000

Writes reports/review_v1_{set}.txt
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = ROOT / "data_pipeline" / "batch_api_test"
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import strip_html, find_raw_file  # noqa: E402
from build_review_batch import COLUMN_ORDER, load_extractions, select  # noqa: E402

CHECK_HEAD = {
    "CONTENT_LOSS": "CONTENT LOSS -- raw text that reached no column",
    "MISCLASSIFICATION": "MISCLASSIFICATION -- content under a heading that does not name it",
    "LABEL_LOSS": "LABEL LOSS -- value kept, the label identifying it dropped",
    "EMPTY_BUT_HEADING": "EMPTY BUT HEADED -- supplier wrote the heading, the column is empty",
}
CHECK_ORDER = ["CONTENT_LOSS", "MISCLASSIFICATION", "LABEL_LOSS", "EMPTY_BUT_HEADING"]


def wrap(text, width=94, indent=""):
    out, line = [], indent
    for word in (text or "").split():
        if len(line) + len(word) + 1 > width and line.strip():
            out.append(line.rstrip())
            line = indent + word + " "
        else:
            line += word + " "
    if line.strip():
        out.append(line.rstrip())
    return out


def short(key):
    return key.replace("redo_desc_", "").replace("redo_", "").upper()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="which", choices=["validation73", "random1000"], required=True)
    args = ap.parse_args()

    scores_path = TEST_DIR / ("review_%s_scores.json" % args.which)
    if not scores_path.exists():
        raise SystemExit("missing %s -- run score_review.py first" % scores_path.name)
    data = json.loads(scores_path.read_text(encoding="utf-8"))
    summary, products = data["summary"], data["products"]

    key = None
    if args.which == "validation73":
        import review_key as rk
        key = rk.KEY

    sources = dict(select(args.which))
    caches = {}
    rows = []
    for pid, p in products.items():
        fn = sources.get(pid)
        if fn and fn not in caches:
            caches[fn] = load_extractions(fn)
        cols = caches.get(fn, {}).get(pid, {})
        item = json.loads(Path(find_raw_file(pid)).read_text(encoding="utf-8"))["item"]
        sd = item.get("structured_description") or {}
        rows.append({
            "pid": pid,
            "name": item.get("name") or "",
            "p": p,
            "cols": cols,
            "raw": strip_html(sd.get("description") or item.get("description") or ""),
            "human": (key or {}).get(pid, {}).get("klass", ""),
        })

    def rank(r):
        ours = [f for f in r["p"]["findings"]
                if f["owner"] == "OURS" and f["verdict"] == "UPHELD"]
        best = min((CHECK_ORDER.index(f["check"]) for f in ours
                    if f["check"] in CHECK_ORDER), default=9)
        return (0 if ours else (1 if r["p"]["n_findings"] else 2), best,
                r["p"]["score"], r["pid"])

    rows.sort(key=rank)

    upheld_ours = [f for r in rows for f in r["p"]["findings"]
                   if f["owner"] == "OURS" and f["verdict"] == "UPHELD"]
    supplier = [f for r in rows for f in r["p"]["findings"] if f["owner"] == "SUPPLIER"]
    by_check = Counter(f["check"] for f in upheld_ours)

    L, A = [], None
    A = L.append
    A("=" * 100)
    A("V5.3 REVIEWER -- %s" % ("73 HAND-VERIFIED PRODUCTS (VALIDATION)"
                               if args.which == "validation73"
                               else "1,000 RANDOM FAREHARBOR PRODUCTS"))
    A("=" * 100)
    A("")
    A("An LLM checker, not an extractor. For each product it read the raw supplier")
    A("description alongside all 22 extracted columns -- including the empty ones -- and")
    A("reported content loss, misclassification, label loss and empty-but-headed columns.")
    A("A second adversarial pass then tried to knock every finding down; only UPHELD")
    A("findings are scored below.")
    A("")
    A("Why it exists: the V5.3 detectors flag text ABSENT from the output, so they are")
    A("blind by construction to a label stripped while its value survives. That class --")
    A("products 634003 and 639882 -- is what this checker was built to see.")
    A("")
    A("Model: gpt-5.6-luna    Prompts: SYSTEM_PROMPT_FH_REVIEW_V1 + _VERIFY_V1")
    A("Column contract: sliced live from SYSTEM_PROMPT_FH_DESC_V5_3 -- the reviewer is")
    A("held to the same bytes the extractor was given.")
    A("")
    A("-" * 100)
    A("FINDINGS  (upheld, ours)")
    A("-" * 100)
    for c in CHECK_ORDER:
        if by_check.get(c):
            A("  %4d  %s" % (by_check[c], CHECK_HEAD[c]))
    A("  %4d  SUPPLIER-SIDE -- the raw text caused it; not scored against us" % len(supplier))
    A("  %4d  NO FINDING" % summary["products_clean"])
    A("")
    n_def = sum(1 for r in rows if any(f["owner"] == "OURS" and f["verdict"] == "UPHELD"
                                       for f in r["p"]["findings"]))
    A("  %d of %d products carry an upheld defect (%.1f%%).   mean score %.1f"
      % (n_def, len(rows), 100.0 * n_def / max(1, len(rows)), summary["mean_score"]))
    A("  bands: " + "   ".join("%s %d" % (k, v) for k, v in sorted(summary["by_band"].items())))
    A("")
    A("-" * 100)
    A("METHOD -- read before trusting a clean verdict")
    A("-" * 100)
    A("  Pass 1 read every product and raised findings. Pass 2 ran only on products with")
    A("  at least one finding, was told to assume the extraction is CORRECT, and tried to")
    A("  refute each one. Prior art on this repo: judge alone gave a false-alarm rate of")
    A("  0.423; judge plus adversarial verifier gave 0.038.")
    A("")
    A("  Pass 2 rejected %s of the findings it verified. REJECTED and UNCERTAIN findings"
      % ("%.0f%%" % (100 * summary["rejection_rate"])
         if summary["rejection_rate"] is not None else "n/a"))
    A("  are kept in review_%s_scores.json so that rate stays visible -- if pass 2 is"
      % args.which)
    A("  rejecting most of pass 1, pass 1 is the problem.")
    A("")
    A("  A blank column is usually the CORRECT answer under the heading gate, and")
    A("  redo_min_age / redo_max_age are blank BY DESIGN. Neither is reported as a defect.")
    if args.which == "random1000":
        A("")
        A("  LIMITATION: only 73 products across the two V5.3 runs have been hand-read.")
        A("  Precision on findings outside those 73 is unmeasured. Do not quote a")
        A("  repo-wide accuracy number from this run.")
    A("")
    A("=" * 100)
    A("PER-PRODUCT DETAIL -- worst first, clean products last")
    A("=" * 100)

    for r in rows:
        p = r["p"]
        A("")
        A("=" * 100)
        head = "%-5s %s  |  %s" % (p["score"], r["pid"], r["name"])
        A(head)
        A("=" * 100)
        A("  score %d   band %s   findings %d (upheld ours %d, supplier %d, rejected %d)"
          % (p["score"], p["band"], p["n_findings"], p["n_ours_upheld"],
             p["n_supplier"], p["n_rejected"]))
        if r["human"]:
            A("  human answer key: %s" % r["human"])
        if not p["findings"]:
            A("")
            A("  NO FINDING -- the reviewer read the raw against all 22 columns and")
            A("  reported nothing.")
        for f in p["findings"]:
            A("")
            A("  -- FINDING %d  %s  [%s / %s / %s]  verdict %s"
              % (f["finding_id"], f["check"], f["owner"], f["severity"],
                 f["confidence"], f["verdict"]))
            if f["column"]:
                A("     column: %s%s" % (f["column"],
                                         ("  ->  " + f["target_column"]) if f["target_column"] else ""))
            if f["placement"]:
                A("     placement: %s" % f["placement"])
            if f["evidence"]:
                for ln in wrap("evidence: " + f["evidence"], indent="     "):
                    A(ln)
            for ln in wrap(f["explanation"], indent="     "):
                A(ln)
            if f["verdict_reason"]:
                for ln in wrap("pass 2: " + f["verdict_reason"], indent="     "):
                    A(ln)
            if f["penalty"]:
                A("     penalty %.1f" % f["penalty"])
        A("")
        A("  " + "-" * 40 + " RAW DESCRIPTION " + "-" * 39)
        for line in r["raw"].split("\n"):
            A("  | " + line.rstrip())
        A("  " + "-" * 43 + " EXTRACTED " + "-" * 42)
        for k in COLUMN_ORDER:
            v = (r["cols"].get(k) or "").strip()
            if not v:
                continue
            A("  [%s]" % short(k))
            for line in v.split("\n"):
                A("      " + line.rstrip())
        blank = [short(k) for k in COLUMN_ORDER if not (r["cols"].get(k) or "").strip()]
        if blank:
            A("  [EMPTY] %s" % ", ".join(blank))

    out = ROOT / "reports" / ("review_v1_%s.txt" % args.which)
    out.write_text("\n".join(L), encoding="utf-8")
    print("wrote %s" % out)
    print("  %d products, %d lines, %d bytes" % (len(rows), len(L), out.stat().st_size))
    for c in CHECK_ORDER:
        if by_check.get(c):
            print("  %3d  %s" % (by_check[c], c))
    print("  %3d  SUPPLIER" % len(supplier))


if __name__ == "__main__":
    main()
