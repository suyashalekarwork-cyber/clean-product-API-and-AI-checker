"""
Automated issue detectors for a V5.3 run, derived from the 100-product hand audit.

Reading 500 products line by line is not feasible, so every defect class found by
hand in the 100-product audit was turned into a detector here. Each one was then
checked back against those 100 products, where the answer is known -- the
false-positive notes in each docstring come from that check.

What this CAN find: the defect classes we have already seen.
What it CANNOT find: a defect class that never appeared in the 100. Treat a clean
result as "none of the known problems", not as "correct".

Verdict codes match audit_v5_3_comments.py.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import strip_html, find_raw_file  # noqa: E402
from score_v5_3 import norm, sentences  # noqa: E402

# --- what_to_bring: lines that are not a thing to bring or wear ---------------
# User-raised on product 156525: the supplier filed notes, weather conditions and
# blackout dates under "What to bring", and heading-gating obeyed the label.
# Tuned against the 100: "booking voucher" and "don't wear your nice clothes" are
# genuine bring/wear items and must NOT match.
NOT_A_BRING_ITEM = re.compile(
    r"^\s*note\s*:|^\s*please note\b|\bsubject to weather\b|\bnot available\b"
    r"|\bpublic holidays\b|\bblackout\b|\bmonies forfeited\b|\bwill be cancelled\b"
    r"|\b(provides|provided|we supply|is supplied) all\b|\bare provided if\b",
    re.I,
)

# --- restrictions: difficulty ratings are not restrictions --------------------
# Products 466438 ("Level: Hard") and 491113 ("Moderate" under a Difficulty
# heading). A Restrictions section reading only "Moderate" tells a customer
# nothing. Anchored so "minimum age 15" and real limits do not match.
DIFFICULTY_ONLY = re.compile(
    r"^\s*(level|difficulty|grade|ability)\s*[:\-]|^\s*(easy|moderate|hard|"
    r"challenging|beginner|intermediate|advanced)\s*[.!]?\s*$",
    re.I,
)

# --- extras / highlights: pure marketing swept in with real items -------------
MARKETING_ONLY = re.compile(
    r"^\s*(designed to make|perfect for|an experience you|it'?s the ultimate|"
    r"fun, safe)", re.I,
)


def load(fn):
    out = {}
    for line in (TEST_DIR / fn).open(encoding="utf-8"):
        d = json.loads(line)
        out[d["custom_id"].split("|")[0]] = json.loads(
            d["response"]["body"]["choices"][0]["message"]["content"]
        )
    return out


def raw_of(pid):
    item = json.loads(Path(find_raw_file(pid)).read_text(encoding="utf-8"))["item"]
    sd = item.get("structured_description") or {}
    return (strip_html(sd.get("description") or item.get("description") or ""),
            item.get("name") or "")


def lines_of(v):
    return [l.strip() for l in (v or "").split("\n") if l.strip()]


def detect(pid, fields, sc, raw):
    """-> list of (verdict, comment). Empty list = no known issue."""
    out = []

    # 1. DUPLICATION -- the business rule: extraction is a MOVE, not a copy.
    if sc.get("duplicated_sentences"):
        seen = {}
        dupes = []
        for k, v in fields.items():
            if k == "redo_flags" or not (v or "").strip():
                continue
            for s in sentences(v):
                n = norm(s)
                if n in seen and seen[n] != k:
                    dupes.append((s[:90], seen[n], k))
                seen.setdefault(n, k)
        for s, a, b in dupes:
            out.append(("DUPLICATION",
                        f"'{s}' appears in BOTH {a.replace('redo_desc_','').replace('redo_','')} "
                        f"and {b.replace('redo_desc_','').replace('redo_','')}. The portal renders "
                        f"both sections, so the customer reads it twice."))

    # 2. CONTENT LOSS -- real only; lead-ins, label-only and bare labels are
    #    already excluded by the scorer per the user's colon ruling.
    for m in sc.get("missing_sentences", []):
        out.append(("CONTENT_LOSS",
                    f"Not present in ANY column: '{m}'"))

    # 3. what_to_bring holding things that are not things to bring
    for l in lines_of(fields.get("redo_desc_what_to_bring")):
        if NOT_A_BRING_ITEM.search(l):
            out.append(("MISCLASS",
                        f"what_to_bring contains a line that is not a thing to bring: "
                        f"'{l[:90]}'. The supplier filed it under that heading, so "
                        f"heading-gating obeyed the label."))

    # 4. difficulty rating filed as a restriction
    for l in lines_of(fields.get("redo_desc_restrictions")):
        if DIFFICULTY_ONLY.match(l):
            out.append(("MISCLASS",
                        f"restrictions holds a difficulty rating, not a limit on who may "
                        f"participate: '{l[:80]}'. Belongs in about."))

    # 5. marketing swept into a list column
    for col in ("redo_desc_extras", "redo_desc_what_included"):
        for l in lines_of(fields.get(col)):
            if MARKETING_ONLY.match(l):
                out.append(("MINOR",
                            f"{col.replace('redo_desc_','')} includes marketing copy rather than "
                            f"an item: '{l[:80]}'"))

    # 6. label stripped from an inline Label: value line (value survived)
    for m in sc.get("dropped_label_only", []):
        out.append(("LABEL_LOSS",
                    f"The label was stripped from '{m}' -- the value survived elsewhere, "
                    f"so nothing is lost, but the line reads bare."))

    # 7. pricing/cancellation column-definition breaches
    if sc.get("pricing_without_figure"):
        out.append(("MISCLASS", "pricing is filled but contains no number, currency "
                                "amount or named charge."))
    if sc.get("cancellation_without_refund"):
        out.append(("MISCLASS", "cancellation is filled but says nothing about what "
                                "happens to the customer's money."))

    # 8. supplier duplicated the text in their own raw description
    src = sentences(raw)
    ns = [norm(s) for s in src if len(norm(s)) > 40]
    if len(ns) != len(set(ns)):
        out.append(("SUPPLIER",
                    "The supplier's own raw description repeats itself; the repetition is "
                    "preserved faithfully. Worth de-duplicating at render time."))

    # 9. everything empty because the supplier wrote headings with no content
    if not any((v or "").strip() for k, v in fields.items() if k != "redo_flags"):
        out.append(("SUPPLIER",
                    "All columns empty -- the supplier wrote headings with no content "
                    "under any of them. Nothing to extract; correct behaviour."))
    return out


def main():
    fn = sys.argv[1] if len(sys.argv) > 1 else "v5_3_hard500_output.jsonl"
    outs = load(fn)
    scores = json.loads(
        (TEST_DIR / (Path(fn).stem.replace("_output", "") + "_scores.json")
         ).read_text(encoding="utf-8"))

    result = {}
    for pid, fields in outs.items():
        raw, name = raw_of(pid)
        issues = detect(pid, fields, scores.get(pid, {}), raw)
        result[pid] = {"name": name, "issues": issues}

    out_path = TEST_DIR / (Path(fn).stem.replace("_output", "") + "_issues.json")
    out_path.write_text(json.dumps(result, indent=1), encoding="utf-8")

    from collections import Counter
    c = Counter(v for r in result.values() for v, _ in r["issues"])
    n_bad = sum(1 for r in result.values() if r["issues"])
    print(f"{len(result)} products scanned")
    print(f"  {n_bad} with at least one detected issue, {len(result)-n_bad} clean")
    for k, n in c.most_common():
        print(f"  {n:>4}  {k}")
    print(f"\nwrote {out_path.name}")


if __name__ == "__main__":
    main()
