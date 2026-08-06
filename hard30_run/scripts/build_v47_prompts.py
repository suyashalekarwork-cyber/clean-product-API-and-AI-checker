"""
Append SYSTEM_PROMPT_FH_DESC_V4_7 and SYSTEM_PROMPT_FH_BOOKING_V4_7 to
config/fareharbor_prompts.txt.

V4.7 = V4.4 verbatim + two new rules, inserted immediately after the VERBATIM
RULE block on each side. Nothing in V4.4 is removed or reworded.

WHY THESE TWO RULES, and why they are worded the way they are:

  Measured on 10 products, 98-99 filled fields per model:

    model            untraceable fields    sentences appearing in 2+ fields
    gpt-5.4-nano             0                          70
    gpt-5.6-terra            4                           6
    gpt-5.6-luna             1                           6

  So gpt-5.4-nano's 1.32x word inflation is NOT invention -- every field
  traces back to the raw text. It is duplication: the same real sentence
  copied into two or three fields.

  V4.4 already forbids rewording (VERBATIM RULE) and forbids populating
  highlights from other fields (NO CROSS-FIELD BORROWING). What it never says
  is that extracting text into a child field REMOVES it from the parent. That
  single missing sentence is what licenses the 70 duplicates.

  Rule A (NO DUPLICATION) closes it, worded as a move rather than a copy.
  Rule B (NO INVENTION) is a guard, not a fix -- invention is currently near
  zero and must stay there. Rules that reduce duplication can push a model
  toward inventing connective text instead, so the guard ships alongside.

DELIBERATELY NOT DONE: V4.6's approach of adding narrowing rules caused a
regression -- coverage fell 87.23% -> 85.95% because the model started
DROPPING content it could not classify instead of routing it to a catch-all.
So both rules below state explicitly where text goes instead, and neither ever
licenses deleting content.

Usage:
    python build_v47_prompts.py           # dry run, prints what would change
    python build_v47_prompts.py --write   # append the blocks
"""
import sys
import re
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROMPTS = Path(__file__).resolve().parent.parent.parent / "config" / "fareharbor_prompts.txt"

PAIRS = [
    ("SYSTEM_PROMPT_FH_DESC_V4_4", "SYSTEM_PROMPT_FH_DESC_V4_7", "redo_desc_about"),
    ("SYSTEM_PROMPT_FH_BOOKING_V4_4", "SYSTEM_PROMPT_FH_BOOKING_V4_7", "redo_booking_other"),
]

# The anchor after which the new rules are inserted. VERBATIM RULE is chosen
# because the new rules are about the same thing -- fidelity to the source --
# so they read as one coherent section rather than an appendix.
ANCHOR = "VERBATIM RULE:"


def new_rules(parent_field):
    return f"""NO DUPLICATION RULE:
Every sentence of the raw text belongs in EXACTLY ONE output field. Extracting is MOVING text, not copying it.
When you place a sentence into a specific field, that sentence must NOT also appear in {parent_field} or in any other field. Remove it from everywhere else.
Test yourself before answering: pick any sentence in your output and search for it in your other fields. If it appears twice, you have duplicated it -- delete every copy except the single best-fitting one.
Example of a VIOLATION: the raw text has one rates block. You put it in the correct field AND leave the same words in {parent_field}. The portal then renders that block twice on the same page. Keep it in one field only.
This rule NEVER licenses deleting content. If a sentence fits no specific field, it stays in {parent_field} -- once. Removing a duplicate means removing the extra copy, never the last copy.

NO INVENTION RULE:
Every word you output must already exist in the raw text. Do not add framing, transitions, headings, summaries, or connective phrases of your own.
Do not write placeholder prose such as "No content found in raw text for this field." If a field has no content, return an empty string "".
Do not restate a fact in your own words to make a field look complete. An empty field is correct and expected when the raw text does not cover it.
Test yourself: if a phrase in your output cannot be found in the raw text by searching for it, you invented it. Remove it.

"""


def extract_block(raw, version):
    """Return the full PROMPT:...END OF... block text for one version."""
    v = re.escape(version)
    m = re.search(r"(PROMPT:\s*" + v + r"\b.*?\n=+\nEND OF " + v + r"\s*$)",
                  raw, re.S | re.M)
    if not m:
        raise SystemExit(f"could not locate block for {version}")
    return m.group(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    raw = PROMPTS.read_text(encoding="utf-8")
    additions = []

    for src_version, new_version, parent in PAIRS:
        if f"PROMPT: {new_version}" in raw:
            print(f"  SKIP {new_version} -- already present")
            continue

        block = extract_block(raw, src_version)
        if ANCHOR not in block:
            raise SystemExit(f"{src_version}: anchor {ANCHOR!r} not found")

        # rename the version markers, then insert the two rules before VERBATIM
        out = block.replace(src_version, new_version)
        out = out.replace(ANCHOR, new_rules(parent) + ANCHOR, 1)

        # the new block must still parse under the project's exact-version regex
        probe = re.search(
            r"PROMPT:\s*" + re.escape(new_version) + r"\b.*?\n=+\n\n(.*?)"
            r"\n\n=+\nEND OF " + re.escape(new_version) + r"\s*$",
            out, re.S | re.M)
        if not probe:
            raise SystemExit(f"{new_version}: generated block fails the "
                             f"extract_prompt() regex -- would break the pipeline")

        body = probe.group(1)
        for must in ("NO DUPLICATION RULE:", "NO INVENTION RULE:", "VERBATIM RULE:",
                     "NO CONTENT LOSS RULE:"):
            if must not in body:
                raise SystemExit(f"{new_version}: lost {must!r}")

        src_body = re.search(
            r"PROMPT:\s*" + re.escape(src_version) + r"\b.*?\n=+\n\n(.*?)"
            r"\n\n=+\nEND OF " + re.escape(src_version) + r"\s*$",
            block, re.S | re.M).group(1)
        added = len(body.splitlines()) - len(src_body.splitlines())
        print(f"  {new_version}: {len(src_body.splitlines())} -> "
              f"{len(body.splitlines())} lines (+{added})")
        additions.append(out)

    if not additions:
        print("\nNothing to add.")
        return

    if not args.write:
        print("\nDRY RUN -- re-run with --write to append.")
        print("\n" + "=" * 74)
        print(new_rules("redo_desc_about"))
        return

    with open(PROMPTS, "a", encoding="utf-8") as f:
        for block in additions:
            f.write("\n\n" + block + "\n")
    print(f"\nAppended {len(additions)} block(s) to {PROMPTS.name}")


if __name__ == "__main__":
    main()