"""
Plain-text audit report for the V5.3 100-product run.

Same content as exports/v5_3_hard100_audit.xlsx but readable in any text editor:
a findings summary, then every product with its verdict, comment, raw
description and all filled columns side by side.

Writes reports/v5_3_random1000_audit.txt (issues first, then the clean ones).
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
from audit_v5_3_random1000_comments import verdict as audit_verdict  # noqa: E402

OUT = ROOT / "reports" / "v5_3_random1000_audit.txt"
SEVERITY = {"DUPLICATION": 0, "CONTENT_LOSS": 1, "MISCLASS": 2, "SCHEMA": 2,
            "LABEL_LOSS": 3, "MINOR": 4, "SUPPLIER": 5, "OK": 9}
HEAD = {
    "DUPLICATION": "DUPLICATION -- same sentence in two columns (breaks the "
                   "extraction-is-a-MOVE rule)",
    "CONTENT_LOSS": "CONTENT LOSS -- text in the raw that reached no column",
    "MISCLASS": "MISCLASSIFICATION -- text landed in the wrong column",
    "SCHEMA": "SCHEMA -- the model returned a key name outside the agreed schema",
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
    new = load("v5_3_random1000_output.jsonl")
    old = load("v5_3_hard500_output.jsonl")
    scores = json.loads((TEST_DIR / "v5_3_random1000_scores.json").read_text(encoding="utf-8"))

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
            "cohort": "random draw, never run before",
        })
    rows.sort(key=lambda r: (SEVERITY.get(r["verdict"], 9), r["pid"]))

    counts = Counter(r["verdict"] for r in rows)
    L = []
    A = L.append

    A("=" * 100)
    A("V5.3 EXTRACTION AUDIT -- 1,000 RANDOM FAREHARBOR PRODUCTS")
    A("=" * 100)
    A("")
    A("A UNIFORM RANDOM SAMPLE -- this is the point of this run.")
    A("")
    A("Every previous set was chosen for difficulty: flagged for human review first, then")
    A("lowest coverage, then longest input. That is the right way to hunt for defects, but")
    A("it means every rate quoted so far came from the WORST products in the catalogue.")
    A("")
    A("These 1,000 are a uniform random draw (seed 42) from the 10,570 products with a")
    A("description that the 500-run never touched. Zero overlap. If the heading gate is")
    A("sound, this should be CLEANER than the hardest-500, and the gap between the two is")
    A("the honest error bar for a full-catalogue run.")
    A("")
    A(f"Model: gpt-5.6-luna    Prompt: SYSTEM_PROMPT_FH_DESC_V5_3    Products: {len(rows)}")
    A("")
    A("-" * 100)
    A("FINDINGS")
    A("-" * 100)
    for k in ("DUPLICATION", "CONTENT_LOSS", "MISCLASS", "SCHEMA", "LABEL_LOSS", "MINOR",
              "SUPPLIER", "OK"):
        if counts.get(k):
            A(f"  {counts[k]:>4}  {HEAD[k]}")
    A("")
    real = sum(counts.get(k, 0) for k in
               ("DUPLICATION", "CONTENT_LOSS", "MISCLASS", "SCHEMA", "LABEL_LOSS", "MINOR"))
    A(f"  {real} products carry a defect ({100*real/max(1,len(rows)):.1f}%); "
      f"{counts.get('SUPPLIER', 0)} are supplier-side; "
      f"{counts.get('OK', 0)} ({100*counts.get('OK',0)/max(1,len(rows)):.1f}%) show no known problem.")
    A("")
    A("-" * 100)
    A("METHOD -- read before trusting a clean verdict")
    A("-" * 100)
    A("  1,000 products cannot be read line by line. Every defect class found in the")
    A("  100-product HAND audit was turned into a detector, checked back against those 100")
    A("  where the answers are known, then run over all of these. Every product the")
    A("  detectors flagged was then opened and read against its raw description.")
    A("")
    A("  So the flagged products are hand-verified. The rest mean 'none of the known defect")
    A("  classes fired', which is weaker than 'read and confirmed correct'.")
    A("")
    A("  Known blind spot: the detectors flag text ABSENT from the output, so they cannot")
    A("  see a label stripped while its value survives -- the 634003 / 639882 class from the")
    A("  500-run. Expect that class to be under-counted here.")
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
    for k in ("DUPLICATION", "CONTENT_LOSS", "MISCLASS", "SCHEMA", "LABEL_LOSS", "MINOR",
              "SUPPLIER", "OK"):
        if counts.get(k):
            print(f"  {counts[k]:>3}  {k}")


if __name__ == "__main__":
    main()
