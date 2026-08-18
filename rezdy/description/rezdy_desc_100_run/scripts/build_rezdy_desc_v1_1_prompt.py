"""Build SYSTEM_PROMPT_RZ_DESC_V1_1 = V1 plus exactly TWO changes.

Both fix the same root cause, measured on the Round 1 run of 100 products:
THE ITINERARY LINE TEST JUDGES LINES, BUT SUPPLIERS WRITE ITINERARIES IN BLOCKS.

  CHANGE 1 -- a Day/Step heading licenses everything beneath it (41 products).
    PWLAK8's supplier wrote `## Full Itinerary` > `**Day 1: Sydney**` > Included
    Activities / Included Meals / Accommodation. The line test ejected the meals
    and accommodation to About because those lines carry no clock time of their
    own -- and the model correctly reported doing so. The rule also contradicts
    STEP 1E, which says the outer heading wins; STEP 3 runs last, so STEP 3 won.
    Consequence: About fills with orphaned fragments (34 products; PPCW71 has 30,
    P1YNVU 27). Retention cannot see this -- every word survives, so the product
    scores 98%+ while being unreadable.

  CHANGE 2 -- a lead-in line and its list move together (3 products).
    PMUZZL: "...breakfast with fresh-brewed coffee or tea, while observing:"
    stayed in itinerary while "- Jabiru - Magpie geese - Jacanas" went to About.
    The itinerary promises a list it no longer contains, and About holds bird
    names attached to nothing. Same principle as RULE 6 FAQ PAIRING, which
    already forbids separating a question from its answer.

NOTHING ELSE CHANGES, and the builder proves it: it diffs V1 against V1.1 and
refuses to write if more than the two intended regions differ. That is the
discipline V5.4 used on the booking side -- one change, proved by diff -- and it
is what makes "nothing else moved" a fact rather than a claim.
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
SOURCE = "SYSTEM_PROMPT_RZ_DESC_V1"
NEW = "SYSTEM_PROMPT_RZ_DESC_V1_1"

# ---------------------------------------------------------------------------
# CHANGE 1 -- replaces the ITINERARY LINE TEST wholesale.
# ---------------------------------------------------------------------------
OLD_ITIN = """ITINERARY LINE TEST
  A line qualifies only if it carries a structural signal:
    - a clock time            "9:30 AM", "2:00 PM"
    - day or step numbering   "Day 1", "Stop 3"
    - a named stop in order   "Circular Quay -> Manly"
  Ordering words alone ("then", "before", "first") are NOT enough.
  Amenity notes, booking instructions and general prose sitting under an
  Itinerary heading FAIL this test and go to redo_desc_about."""

NEW_ITIN = """ITINERARY LINE TEST

  FIRST, ASK WHETHER A DAY OR STEP BLOCK IS OPEN.

  A heading naming a day or a step -- "Day 1", "DAY 2 - Wetlands & Hot Springs",
  "Stop 3", "Morning" -- OPENS A BLOCK. Everything from that heading until the
  NEXT day or step heading belongs to redo_desc_itinerary, whole: the prose, the
  lists, the meals, the accommodation, the sub-headings and their content.

  DO NOT TEST THOSE LINES INDIVIDUALLY. The day heading already carries the
  structural signal for its whole block, and asking each line beneath it to prove
  a day number again is asking twice. A supplier who writes

      Day 1: Sydney
      We start in Australia's Harbour City...
      Included Meals
      - Welcome Dinner
      Accommodation - Sample Hotel

  has written an itinerary. Moving the meals and the hotel out of it because
  those lines carry no clock time of their own SPLITS ONE DAY ACROSS TWO FIELDS
  and leaves the reader unable to tell which night is which hotel.

  THE LINE TEST BELOW APPLIES ONLY WHERE NO DAY OR STEP BLOCK IS OPEN --
  a bare list under an Itinerary heading with no day structure at all.

    A line qualifies only if it carries a structural signal:
      - a clock time            "9:30 AM", "2:00 PM"
      - day or step numbering   "Day 1", "Stop 3"
      - a named stop in order   "Circular Quay -> Manly"
    Ordering words alone ("then", "before", "first") are NOT enough.
    Amenity notes, booking instructions and general prose sitting under such an
    Itinerary heading FAIL this test and go to redo_desc_about."""

# ---------------------------------------------------------------------------
# CHANGE 2 -- appended to RULE 6, which already forbids separating a question
# from its answer. A lead-in and its list are the same relationship.
# ---------------------------------------------------------------------------
OLD_RULE6_TAIL = """   If you place a sentence that answers a question, you MUST place the question
   with it, in the same field, question first. Never extract an answer while
   leaving its question behind."""

NEW_RULE6_TAIL = """   If you place a sentence that answers a question, you MUST place the question
   with it, in the same field, question first. Never extract an answer while
   leaving its question behind.

   THE SAME HOLDS FOR A LEAD-IN AND ITS LIST. A line that ends in ":" introduces
   the lines beneath it, and the two are ONE unit. They move together, into the
   same field, lead-in first.
       "Enjoy a continental breakfast, while observing:"
       - Jabiru
       - Magpie geese
   Placing the lead-in in one field and the list in another leaves a sentence
   promising a list it does not contain, and a list of bare items attached to
   nothing. Both halves become useless. If the list qualifies for a field, the
   lead-in goes with it; if it does not, both stay in redo_desc_about."""

HEADER = f"""
PROMPT: {NEW}
VERSION: 1.1-rezdy-desc
CREATED: 2026-08-17
AUTHOR: Claude Code
SOURCE: {SOURCE} with EXACTLY TWO changes, proved by diff in
        build_rezdy_desc_v1_1_prompt.py -- it refuses to write if any third
        region differs.
PURPOSE: Fix the two defects found by hand-reading the Round 1 run of the 100
         hardest products. Both come from one root cause: the itinerary line
         test judges LINES, but suppliers write itineraries in BLOCKS.
CHANGES FROM {SOURCE}:
  1. ITINERARY LINE TEST -- a Day or Step heading now licenses everything
     beneath it until the next Day/Step heading, and the line test applies only
     where no such block is open. MEASURED: 41 of 100 products had itinerary
     content ejected to About by the old rule, and 34 ended up with orphaned
     fragments in About (PPCW71 30 of them, P1YNVU 27). The old rule also
     contradicted STEP 1E -- the outer heading was supposed to win, and STEP 3,
     running later, overrode it.
  2. RULE 6 -- a lead-in line ending in ":" now moves with its list, the same
     way a question moves with its answer. MEASURED: 3 products (PMUZZL,
     PTW3FE, PFYJ8P) left a colon dangling in one field and its list stranded
     in another.
NOT CHANGED, though flagged in Round 1: 5 lost URLs across 2 products (RULE 7
         already forbids this -- it is disobedience, not an absent rule), and 3
         mid-sentence starts (RULE 10 covers it and mostly holds). Both are too
         low-volume to write a rule from; re-measure at 1,000.
EVIDENCE: reports/rezdy_desc_v1_issues.md
========================================
""".lstrip("\n")


def main():
    raw = RZ_PROMPTS.read_text(encoding="utf-8")
    before_sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    v1 = extract_prompt(raw, SOURCE)
    print(f"{SOURCE}: {len(v1):,} chars")

    if f"PROMPT: {NEW}" in raw:
        raise SystemExit(f"REFUSING TO WRITE -- {NEW} already exists. Prompts "
                         f"are APPEND-ONLY; bump the version instead.")

    body = v1
    for old, new, label in [(OLD_ITIN, NEW_ITIN, "itinerary block rule"),
                            (OLD_RULE6_TAIL, NEW_RULE6_TAIL, "lead-in + list")]:
        if body.count(old) != 1:
            raise SystemExit(
                f"REFUSING TO WRITE -- '{label}' matched {body.count(old)} "
                f"times, expected 1")
        body = body.replace(old, new, 1)
        print(f"  applied: {label}")

    # THE PROOF: exactly two changed regions, both insertions/replacements.
    sm = difflib.SequenceMatcher(None, v1.split("\n"), body.split("\n"),
                                 autojunk=False)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    print(f"\n  diff regions: {len(ops)}")
    for tag, i1, i2, j1, j2 in ops:
        print(f"    {tag:8s} V1 lines {i1}-{i2}  ->  V1.1 lines {j1}-{j2}")
    if len(ops) != 2:
        raise SystemExit(f"REFUSING TO WRITE -- expected exactly 2 changed "
                         f"regions, found {len(ops)}. Something else moved.")

    verify(v1, body)

    block = HEADER + "\n" + body.strip() + "\n\n" + "=" * 40 + f"\nEND OF {NEW}\n"
    RZ_PROMPTS.write_text(raw.rstrip("\n") + "\n\n" + block, encoding="utf-8")

    out = RZ_PROMPTS.read_text(encoding="utf-8")
    if extract_prompt(out, SOURCE) != v1:
        raise SystemExit("REFUSING -- V1 changed. It must stay byte-identical "
                         "so rollback is one constant.")
    check = extract_prompt(out, NEW)
    print(f"\n  V1 still byte-identical      : yes")
    print(f"  V1.1 round-trips             : {len(check):,} chars")
    print(f"  file sha256 {before_sha[:12]} -> "
          f"{hashlib.sha256(out.encode('utf-8')).hexdigest()[:12]}")
    print(f"\nwrote {NEW} -> {RZ_PROMPTS}")


def verify(v1, body):
    schema = re.search(r'^\{"redo_desc_about".*\}$', body, re.M)
    if list(json.loads(schema.group(0)).keys()) != COLUMNS:
        raise SystemExit("REFUSING TO WRITE -- schema keys changed")
    if len(re.findall(r'^\{"redo_desc_about".*\}$', body, re.M)) != \
            len(re.findall(r'^\{"redo_desc_about".*\}$', v1, re.M)):
        raise SystemExit("REFUSING TO WRITE -- an example was added or lost")
    for inv in ["Extract content into a field ONLY when the supplier wrote a "
                "HEADING for it",
                "STEP 1E -- NESTED HEADINGS: THE OUTER HEADING WINS",
                "7. STRIP MARKUP, KEEP THE LINE AND KEEP THE URL.",
                "10. A SENTENCE IS THE SMALLEST MOVABLE UNIT.",
                "WHAT_INCLUDED LINE TEST"]:
        if inv not in body:
            raise SystemExit(f"REFUSING TO WRITE -- lost: {inv[:60]}")
    # The what_included line test must be UNTOUCHED -- only itinerary changed.
    a = re.search(r"WHAT_INCLUDED LINE TEST.*?(?=\n\nRULES)", v1, re.S).group(0)
    b = re.search(r"WHAT_INCLUDED LINE TEST.*?(?=\n\nRULES)", body, re.S).group(0)
    if a != b:
        raise SystemExit("REFUSING TO WRITE -- the what_included line test moved")
    print("  verified: schema, examples, core rules, what_included test all intact")


if __name__ == "__main__":
    main()
