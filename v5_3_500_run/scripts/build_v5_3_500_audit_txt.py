"""
Plain-text audit report for the V5.3 100-product run.

Same content as exports/v5_3_hard100_audit.xlsx but readable in any text editor:
a findings summary, then every product with its verdict, comment, raw
description and all filled columns side by side.

Writes reports/v5_3_hard500_audit.txt (issues first, then the clean ones).
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = ROOT / "data_pipeline" / "batch_api_test"
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import strip_html, find_raw_file  # noqa: E402
from audit_v5_3_500_comments import verdict as audit_verdict  # noqa: E402

OUT = ROOT / "reports" / "v5_3_hard500_audit.txt"
SEVERITY = {"DUPLICATION": 0, "CONTENT_LOSS": 1, "MISCLASS": 2,
            "LABEL_LOSS": 3, "MINOR": 4, "SUPPLIER": 5, "OK": 9}
HEAD = {
    "DUPLICATION": "DUPLICATION -- same sentence in two columns (breaks the "
                   "extraction-is-a-MOVE rule)",
    "CONTENT_LOSS": "CONTENT LOSS -- text in the raw that reached no column",
    "MISCLASS": "MISCLASSIFICATION -- text landed in the wrong column",
    "LABEL_LOSS": "LABEL LOSS -- value kept, the label identifying it dropped",
    "MINOR": "MINOR -- defensible, but worth a look",
    "SUPPLIER": "SUPPLIER-SIDE -- the defect is in the raw text, preserved faithfully",
    "OK": "NO ISSUE FOUND",
}


def load(fn):
    out = {}
    for line in (TEST_DIR / fn).open(encoding="utf-8"):
        d = json.loads(line)
        out[d["custom_id"].split("|")[0]] = json.loads(
            d["response"]["body"]["choices"][0]["message"]["content"]
        )
    return out


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


def main():
    new = load("v5_3_hard500_output.jsonl")
    old = load("v5_3_hard100_output.jsonl")
    scores = json.loads((TEST_DIR / "v5_3_hard500_scores.json").read_text(encoding="utf-8"))

    rows = []
    for pid, fields in new.items():
        v, c = audit_verdict(pid)
        item = json.loads(Path(find_raw_file(pid)).read_text(encoding="utf-8"))["item"]
        sd = item.get("structured_description") or {}
        rows.append({
            "pid": pid, "name": item.get("name") or "",
            "verdict": v, "comment": c, "fields": fields,
            "raw": strip_html(sd.get("description") or item.get("description") or ""),
            "sc": scores.get(pid, {}),
            "cohort": "carried over from the V5.2 50" if pid in old else "new this run",
        })
    rows.sort(key=lambda r: (SEVERITY.get(r["verdict"], 9), r["pid"]))

    counts = Counter(r["verdict"] for r in rows)
    L = []
    A = L.append

    A("=" * 100)
    A("V5.3 EXTRACTION AUDIT -- 500 HARDEST FAREHARBOR PRODUCTS")
    A("=" * 100)
    A("")
    A("METHOD -- read this before trusting a clean verdict.")
    A("")
    A("500 products cannot be read line by line. Every defect class found in the earlier")
    A("100-product HAND audit was turned into a detector, the detectors were checked back")
    A("against those 100 where the answers are already known, then run over all 499.")
    A("EVERY PRODUCT THEY FLAGGED WAS THEN OPENED AND READ against its raw description --")
    A("the verdicts below are that reading, not the detector output. Five detector hits")
    A("were overturned as false positives and are marked OK with the reason.")
    A("")
    A("So: the flagged products are hand-verified. The rest mean 'none of the known defect")
    A("classes fired', which is weaker than 'read and confirmed correct'. A defect class")
    A("that never appeared in the first 100 would not be caught here.")
    A("")
    A(f"Model: gpt-5.6-luna    Prompt: SYSTEM_PROMPT_FH_DESC_V5_3    Products: {len(rows)}")
    A("Set: the whole 500-product pool, ordered by (flagged for review, lowest coverage,")
    A("     longest input). Includes all 100 from the previous run, so those 100 got a")
    A("     second independent pass on the identical prompt -- see REPEATABILITY below.")
    A("")
    A("-" * 100)
    A("FINDINGS")
    A("-" * 100)
    for k in ("DUPLICATION", "CONTENT_LOSS", "MISCLASS", "LABEL_LOSS", "MINOR",
              "SUPPLIER", "OK"):
        if counts.get(k):
            A(f"  {counts[k]:>3}  {HEAD[k]}")
    A("")
    real = sum(counts.get(k, 0) for k in
               ("DUPLICATION", "CONTENT_LOSS", "MISCLASS", "LABEL_LOSS", "MINOR"))
    A(f"  {real} products carry a defect ({100*real/max(1,len(rows)):.1f}%); "
      f"{counts.get('SUPPLIER', 0)} are supplier-side, not model defects; "
      f"{counts.get('OK', 0)} show no known problem.")
    A("")
    A("  SPLIT BY WHO CAUSED IT (user ruling 2026-08-11: 'if we did mistake during")
    A("  extraction then that is the issue, otherwise that is not even an issue'):")
    A("")
    A("    OUR EXTRACTION DEFECTS -- 8 products, 1.6%")
    A("      content loss        3   371805, 535701, 293135     text dropped that the raw had once")
    A("      difficulty rating   2   466438, 491113             we routed it to restrictions")
    A("      label loss          3   713497, 324361, 697755     cosmetic, every value survived")
    A("")
    A("      Of these, only 5 (1.0%) cost the customer anything -- the 3 label losses")
    A("      keep all their information.")
    A("")
    A("    SUPPLIER DATA, REPRODUCED FAITHFULLY -- 13 products, not extraction defects")
    A("      raw repeats itself  9   509794, 203555, 249729, 330482, 279178,")
    A("                              444088, 397465, 319096, 171361")
    A("      mis-filed heading   3   156525, 327258, 500245  (notes/cancellation terms")
    A("                              placed under the supplier's own 'What to bring' heading)")
    A("      empty headings      1   680927")
    A("")
    A("-" * 100)
    A("REPEATABILITY -- the most important finding in this run")
    A("-" * 100)
    A("  The 500 re-ran all 100 products from the previous run on the SAME prompt, so the")
    A("  two can be compared directly. Most defects DID NOT REPRODUCE:")
    A("")
    A("      product   run 1 (100)        run 2 (500)")
    A("      457336    lost 3 sentences   lost 0        <- vanished")
    A("      676702    lost 1 sentence    lost 0        <- vanished")
    A("      135308    duplicated         clean         <- vanished")
    A("      417608    duplicated         clean         <- vanished")
    A("      371805    lost 1 sentence    lost 1        <- REPEATABLE")
    A("      509794    duplicated         duplicated    <- REPEATABLE")
    A("")
    A("  Four of six defects were sampling noise, not a rule the model gets wrong. That")
    A("  changes what a fix can achieve: a prompt rule can only address the two repeatable")
    A("  cases. For the random ones, no wording is a guarantee -- the only way to make")
    A("  content loss structurally impossible is a deterministic check after extraction")
    A("  that puts any unaccounted-for sentence back into about.")
    A("")
    A("  It also means a single run understates the true rate: a different run loses")
    A("  different sentences. Expect roughly 1% of products to have SOMETHING wrong on")
    A("  any given pass, but not the same 1%.")
    A("")
    A("-" * 100)
    A("WHAT STILL NEEDS A DECISION")
    A("-" * 100)
    A("  1. what_to_bring needs the line test (156525, 327258, 500245). It is the third")
    A("     point-wise column and has an equally precise test: is this a physical item or")
    A("     clothing the customer brings? 327258 is the clearest case -- its entire")
    A("     What-to-Bring section says the school PROVIDES everything.")
    A("  2. Difficulty ratings need a home (466438, 491113). They are not restrictions.")
    A("  3. Duplication: still 2 products, still a hard gate failure. Parked by decision.")
    A("")
    A("  NOT defects, for the record: the 44 'itinerary lines without a signal' the scorer")
    A("  reports are mostly correct -- named stops in stated order, and 'AM -' / 'PM :'")
    A("  markers, which the scorer's regex cannot see. It only detects clock times and day")
    A("  numbers.")
    A("")
    A("=" * 100)
    A("PER-PRODUCT DETAIL -- worst class first, clean products last")
    A("=" * 100)

    for r in rows:
        sc = r["sc"]
        A("")
        A("=" * 100)
        A(f"{r['verdict']:<13} {r['pid']}  |  {r['name']}")
        A("=" * 100)
        A(f"  ({r['cohort']})")
        A("")
        for ln in wrap(r["comment"], indent="  "):
            A(ln)
        A("")
        A(f"  retention {sc.get('retention_pct')}%   duplicated {sc.get('duplicated_sentences')}   "
          f"fields filled {sc.get('fields_filled')}   fidelity {sc.get('fidelity')}")
        if sc.get("missing_sentences"):
            A("  NOT PRESENT IN ANY COLUMN:")
            for m in sc["missing_sentences"]:
                A(f"      - {m}")
        if (r["fields"].get("redo_flags") or "").strip():
            A("  MODEL'S OWN FLAGS:")
            for fl in r["fields"]["redo_flags"].split("\n"):
                if fl.strip():
                    A(f"      {fl.strip()}")
        A("")
        A("  " + "-" * 40 + " RAW DESCRIPTION " + "-" * 39)
        for line in r["raw"].split("\n"):
            A("  | " + line.rstrip())
        A("  " + "-" * 43 + " EXTRACTED " + "-" * 42)
        for k, v in r["fields"].items():
            if not (v or "").strip() or k == "redo_flags":
                continue
            A(f"  [{k.replace('redo_desc_', '').replace('redo_', '').upper()}]")
            for line in str(v).split("\n"):
                A("      " + line.rstrip())
        blank = [k.replace("redo_desc_", "").replace("redo_", "")
                 for k, v in r["fields"].items()
                 if not (v or "").strip() and k != "redo_flags"]
        A(f"  [EMPTY] {', '.join(blank)}")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  {len(rows)} products, {len(L)} lines, {OUT.stat().st_size:,} bytes")
    for k in ("DUPLICATION", "CONTENT_LOSS", "MISCLASS", "LABEL_LOSS", "MINOR",
              "SUPPLIER", "OK"):
        if counts.get(k):
            print(f"  {counts[k]:>3}  {k}")


if __name__ == "__main__":
    main()
