"""Build SYSTEM_PROMPT_RZ_DESC_V1_2 = V1.1 plus ONE change: Terms & Conditions.

WHAT WAS WRONG. `redo_desc_disclaimers` was filled ZERO times across all 100
products in Round 1, while the column census measures it at 178 distinct
suppliers and 7.9% of the catalogue -- the 9th biggest column we ship. A dead
column that the data says should be busy.

WHY. The inherited definition is one line:

    redo_desc_disclaimers Disclaimers, Risk Disclosure, Liability, Waiver.

It never mentions "Terms & Conditions", which is the commonest wording by a
distance -- 40 suppliers write "terms and conditions" and 35 write "terms &
conditions", 75 in total, against 5 for "liability" and 4 for "disclaimer".
STEP 2 tells the model to match by meaning, but "Terms & Conditions" is not
close enough to "Disclaimers / Risk Disclosure / Liability / Waiver" for that to
fire, so the heading named no column and its content correctly fell to About.

MEASURED on the 100: six products carry an explicit Terms & Conditions heading
(PBWS0N `**TERMS & CONDITIONS**`, PHUG8D `**Terms & Conditions **`, PUR10W
`**Terms and Conditions of Booking**` and three more). Disclaimers filled on
none of them.

This is the same class as the Day 1/Day 2 gap fixed in V1.1: OUR COLUMN DOCUMENT
AND OUR PROMPT DISAGREED. reports/rezdy_column_definitions.md maps `terms and
conditions` to disclaimers and the prompt never said so. Found by a reviewer
reading output, not by any check we run -- worth a check of its own before the
next source is ported.

DELIBERATELY NOT DONE: clause-level routing. It is tempting to say "a
cancellation clause inside a T&C block goes to cancellation", but that is
classification by meaning INSIDE a block, which STEP 1E forbids -- the outer
heading wins. A supplier who wants a separate cancellation section writes a
separate heading, and that already works.
"""
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
sys.path.insert(0, str(TEST_DIR))

from build_rezdy_desc_prompt import COLUMNS, extract_prompt  # noqa: E402

RZ_PROMPTS = ROOT / "config" / "rezdy_prompts.txt"
SOURCE = "SYSTEM_PROMPT_RZ_DESC_V1_1"
NEW = "SYSTEM_PROMPT_RZ_DESC_V1_2"

OLD = "  redo_desc_disclaimers Disclaimers, Risk Disclosure, Liability, Waiver."

NEW_DEF = """  redo_desc_disclaimers
      The operator's legal terms and risk statements. Headings: Disclaimers,
      Risk Disclosure, Understanding the Risks, Liability, Waiver, Indemnity,
      Conditions of Entry -- and, most commonly of all, TERMS & CONDITIONS:
      "Terms & Conditions", "Terms and Conditions", "T&Cs", "Booking Terms",
      "Terms and Conditions of Booking", "General Terms and Conditions".
      Terms & Conditions is this field's commonest heading by a wide margin. It
      does NOT name redo_desc_about.
      A numbered list of booking clauses under such a heading belongs here as a
      block -- do not sort the clauses between fields. If the supplier wanted a
      separate cancellation section they wrote a separate heading for it, and
      the outer heading rule (STEP 1E) applies here as everywhere."""

HEADER = f"""
PROMPT: {NEW}
VERSION: 1.2-rezdy-desc
CREATED: 2026-08-17
AUTHOR: Claude Code
SOURCE: {SOURCE} with EXACTLY ONE change, proved by diff in
        build_rezdy_desc_v1_2_prompt.py -- it refuses to write if a second
        region differs.
PURPOSE: Revive redo_desc_disclaimers, which filled 0 times in 100 products
         while the column census measures it at 178 distinct suppliers and 7.9%
         of the catalogue.
CHANGE FROM {SOURCE}:
  1. redo_desc_disclaimers now names TERMS & CONDITIONS as its commonest
     heading. The inherited one-line definition listed only Disclaimers / Risk
     Disclosure / Liability / Waiver -- 75 suppliers write some form of "terms
     and conditions" against 5 for "liability" and 4 for "disclaimer", so the
     commonest wording was the one wording the prompt never mentioned.
     MEASURED: 6 of the 100 products carry an explicit Terms & Conditions
     heading (PBWS0N, PHUG8D, PUR10W and three more) and disclaimers filled on
     NONE of them; that content sat in About instead.
ROOT CAUSE, worth carrying to the next source: the column document
         (reports/rezdy_column_definitions.md) and the prompt disagreed. Same
         class as the Day 1/Day 2 gap fixed in V1.1. Diff the two before
         shipping a prompt for any new supplier.
NOT DONE: clause-level routing inside a T&C block. Sorting clauses between
         fields is classification by meaning inside a block, which STEP 1E
         forbids.
========================================
""".lstrip("\n")


def main():
    raw = RZ_PROMPTS.read_text(encoding="utf-8")
    before = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    src = extract_prompt(raw, SOURCE)
    print(f"{SOURCE}: {len(src):,} chars")

    if f"PROMPT: {NEW}" in raw:
        raise SystemExit(f"REFUSING TO WRITE -- {NEW} already exists. "
                         f"Prompts are APPEND-ONLY.")
    if src.count(OLD) != 1:
        raise SystemExit(f"REFUSING TO WRITE -- disclaimers definition matched "
                         f"{src.count(OLD)} times, expected 1")

    body = src.replace(OLD, NEW_DEF, 1)
    print("  applied: disclaimers definition")

    sm = difflib.SequenceMatcher(None, src.split("\n"), body.split("\n"),
                                 autojunk=False)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    print(f"\n  diff regions: {len(ops)}")
    for tag, i1, i2, j1, j2 in ops:
        print(f"    {tag:8s} {SOURCE} {i1}-{i2}  ->  {NEW} {j1}-{j2}")
    if len(ops) != 1 or ops[0][0] != "replace":
        raise SystemExit("REFUSING TO WRITE -- expected exactly ONE replaced "
                         "region. Something else moved.")

    schema = re.search(r'^\{"redo_desc_about".*\}$', body, re.M)
    if list(json.loads(schema.group(0)).keys()) != COLUMNS:
        raise SystemExit("REFUSING TO WRITE -- schema keys changed")
    for inv in ["THE ONE RULE THAT GOVERNS EVERYTHING",
                "STEP 1E -- NESTED HEADINGS: THE OUTER HEADING WINS",
                "FIRST, ASK WHETHER A DAY OR STEP BLOCK IS OPEN.",
                "THE SAME HOLDS FOR A LEAD-IN AND ITS LIST.",
                "7. STRIP MARKUP, KEEP THE LINE AND KEEP THE URL."]:
        if inv not in body:
            raise SystemExit(f"REFUSING TO WRITE -- lost: {inv[:60]}")
    print("  verified: schema + V1.1's two fixes + core rules all intact")

    block = HEADER + "\n" + body.strip() + "\n\n" + "=" * 40 + f"\nEND OF {NEW}\n"
    RZ_PROMPTS.write_text(raw.rstrip("\n") + "\n\n" + block, encoding="utf-8")

    out = RZ_PROMPTS.read_text(encoding="utf-8")
    for v in ["SYSTEM_PROMPT_RZ_DESC_V1", SOURCE]:
        extract_prompt(out, v)          # every earlier version still extractable
    if extract_prompt(out, SOURCE) != src:
        raise SystemExit("REFUSING -- V1.1 changed; it must stay byte-identical")
    print(f"\n  V1 and V1.1 still extractable and unchanged")
    print(f"  {NEW} round-trips: {len(extract_prompt(out, NEW)):,} chars")
    print(f"  file sha256 {before[:12]} -> "
          f"{hashlib.sha256(out.encode('utf-8')).hexdigest()[:12]}")
    print(f"\nwrote {NEW} -> {RZ_PROMPTS}")


if __name__ == "__main__":
    main()
