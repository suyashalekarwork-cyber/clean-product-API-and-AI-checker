"""
Build SYSTEM_PROMPT_FH_BOOKING_V5_4.

ONE CHANGE ONLY: RULE 8 gains the two image-carrying markdown shapes.

    ![alt](url)              a plain image
    [![alt](img)](dest)      an image INSIDE a link -- TWO urls

V5.3's RULE 8 covers `[text](url)` and nothing else, so both shapes were
dropped whole. Measured on the 500-product run: 31 URLs lost across 22
products, of which 19 were real destination links (skydive.co.nz/mt-cook and
similar), not decoration. Product 232220 lost 8 URLs from a single line of four
clickable partner logos.

WHY KEEP THE IMAGE URL TOO, rather than keeping only the destination:
measured, only 12 destinations in 500 products sit behind an image, while
keeping everything costs a median of ONE extra url on the 20% of products that
have image markdown. So the tidier "drop the decoration" rule buys almost
nothing and costs a judgement about meaning -- the thing V5 exists to remove.
RULE 11 already says every URL survives, character for character. V5.4 makes
RULE 8 agree with it.

NOT CHANGED HERE, deliberately, one change per version:
  RULE 9 (required-item markers) is the confirmed cause of the "(required)"
  insertions found in the 500 run -- 215424, 271911, 712977. It tells the model
  to append the literal word "(required)" wherever the raw uses bold, and it
  cannot tell bold-as-emphasis from bold-as-required-marker. That is V5.5.

METHOD: the V5.3 body is read back OUT of the prompts file and edited
surgically, rather than re-rendered from a 28 KB literal. That way "nothing
else changed" is proved by diff, not assumed. The build refuses to write unless
exactly one region differs.
"""
import argparse
import difflib
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
PROMPTS = ROOT / "config" / "fareharbor_prompts.txt"
BACKUP = ROOT / "config" / "fareharbor_prompts.txt.bak_before_booking_v5_4"

BASE_VERSION = "SYSTEM_PROMPT_FH_BOOKING_V5_3"
NEW_VERSION = "SYSTEM_PROMPT_FH_BOOKING_V5_4"
RULE = "=" * 40

# The exact V5.3 text the insert goes after. If this drifts, the build fails
# rather than inserting in the wrong place.
ANCHOR = """   Emitting "See here for full Terms and Conditions" DESTROYS the link and is a
   content-loss defect: "see here" with no "here" is useless.
"""

INSERT = """   AN IMAGE ALSO CARRIES A URL, AND SO DOES AN IMAGE INSIDE A LINK. Two more
   shapes appear in booking notes and BOTH must survive:
       "![Jetty at low tide](https://example.test/img/jetty.jpg)"
       -> "Jetty at low tide (https://example.test/img/jetty.jpg)"
       "[![logo](https://example.test/img/logo.png)](https://example.test/tours)"
       -> "logo (https://example.test/img/logo.png) (https://example.test/tours)"
   The second shape carries TWO urls -- the image and the destination it links
   to. KEEP BOTH. Dropping either one because it "looks decorative" is a
   judgement about meaning, and RULE 11 admits no exception: every URL in the
   raw appears in the output.
   The alt text inside ![...] is the SUPPLIER'S text. Keep it exactly as
   written, including when it is a generic placeholder like "Description of
   image". Do not improve it, replace it, or describe the picture yourself.
"""

HEADER = f"""PROMPT: {NEW_VERSION}
VERSION: 5.4-booking
CREATED: 2026-08-13
AUTHOR: Claude Code
PURPOSE: {BASE_VERSION} with ONE change: RULE 8 now covers image markdown.
         V5.3's RULE 8 handled [text](url) only, so ![alt](url) and the nested
         [![alt](img)](dest) shape were dropped whole. Measured on the 500-
         product run: 31 URLs lost across 22 products, 19 of them real
         destination links. Product 232220 lost 8 from one line of clickable
         partner logos.
         Also states that ![...] alt text is the supplier's own words and must
         be copied as written -- "Description of image" is Fareharbor's default
         alt text, present 148 times in 500 products, and is NOT to be
         rewritten.
         Everything else is byte-identical to {BASE_VERSION}, asserted by diff.
         NOT fixed here (next version): RULE 9 required-item markers, the
         confirmed cause of the "(required)" insertions in 215424/271911/712977.
"""


def probe(raw, version):
    v = re.escape(version)
    return re.search(
        r"PROMPT:\s*" + v + r"\b.*?\n=+\n\n(.*?)\n\n=+\nEND OF " + v + r"\s*$",
        raw, re.S | re.M)


def block_names(raw):
    return re.findall(r"^PROMPT:\s*(\S+)", raw, re.M)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    raw = PROMPTS.read_text(encoding="utf-8")
    before_names = block_names(raw)
    m = probe(raw, BASE_VERSION)
    if not m:
        raise SystemExit(f"could not extract {BASE_VERSION}")
    base = m.group(1)
    print(f"base {BASE_VERSION}: {len(base)} chars, "
          f"{len(before_names)} blocks in file")

    ok = True
    if base.count(ANCHOR) != 1:
        raise SystemExit(f"anchor found {base.count(ANCHOR)} times, expected 1 "
                         "-- RULE 8 text has drifted; fix the anchor")
    body = base.replace(ANCHOR, ANCHOR + INSERT)

    # ---- the assertion this file exists for: EXACTLY one region changed ----
    a, b = base.split("\n"), body.split("\n")
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    print(f"\n  diff regions: {len(ops)}")
    for tag, i1, i2, j1, j2 in ops:
        print(f"    {tag}: base[{i1}:{i2}] -> new[{j1}:{j2}] "
              f"({j2 - j1 - (i2 - i1):+d} lines)")
    if len(ops) != 1 or ops[0][0] != "insert":
        raise SystemExit("expected exactly ONE insert and nothing else -- refusing")
    added = b[ops[0][3]:ops[0][4]]
    if "\n".join(added) + "\n" != INSERT:
        raise SystemExit("the inserted lines are not exactly INSERT -- refusing")
    print(f"  [OK ] exactly one insert of {len(added)} lines, nothing else touched")

    # every other line byte-identical
    removed = [l for l in a if l not in b]
    print(f"  [{'OK ' if not removed else 'FAIL'}] no line removed from V5.3"
          + (f" -- {removed[:3]}" if removed else ""))
    ok &= not removed

    checks = [
        ("markdown link rule still present", "A MARKDOWN LINK KEEPS ITS TARGET."),
        ("never alter a url still present", "NEVER shorten, expand or otherwise alter a URL."),
        ("url self-check still present", "Every URL in the raw appears in the output"),
        ("outer heading rule still present", "STEP 1E -- NESTED HEADINGS: THE OUTER HEADING WINS"),
        ("no-copy-from-examples still present", "NEVER COPY TEXT FROM THE EXAMPLES IN THIS PROMPT."),
        ("new: plain image shape", "![Jetty at low tide]"),
        ("new: image inside link shape", "[![logo]"),
        ("new: alt text is the supplier's", "Do not improve it, replace it, or describe"),
    ]
    for label, needle in checks:
        hit = needle in body
        print(f"  [{'OK ' if hit else 'FAIL'}] {label}")
        ok &= hit

    leaks = sorted(set(re.findall(r"redo_desc_\w+", body)))
    print(f"  [{'OK ' if not leaks else 'FAIL'}] no redo_desc_* leaked (F1 guard)")
    ok &= not leaks

    n_keys = len(re.findall(r'"redo_booking_\w+": ""', body))
    print(f"  [{'OK ' if n_keys >= 25 else 'FAIL'}] schema line still carries "
          f"25 keys (found {n_keys})")
    ok &= n_keys >= 25

    # the worked examples must stay synthetic -- real strings appearing in
    # output are what PROVES contamination
    for name in ("example.test", "Acme", "Sample"):
        print(f"  [{'OK ' if name in body else 'FAIL'}] synthetic example name "
              f"kept: {name}")
        ok &= name in body

    if not ok:
        raise SystemExit("checks failed -- refusing to write")

    block = HEADER + "\n" + RULE + "\n\n" + body + "\n\n" + RULE + "\nEND OF " + NEW_VERSION
    if NEW_VERSION in before_names:
        raise SystemExit(f"{NEW_VERSION} already present -- append-only, refusing")
    new_raw = raw.rstrip("\n") + "\n\n" + block + "\n"

    m2 = probe(new_raw, NEW_VERSION)
    if not m2:
        raise SystemExit("appended block does not re-extract")
    if m2.group(1).strip() != body.strip():
        raise SystemExit("round-trip mismatch")
    print(f"\n  [OK ] re-extracts and round-trips ({len(m2.group(1))} chars)")

    after = block_names(new_raw)
    if after[:len(before_names)] != before_names or after[-1] != NEW_VERSION:
        raise SystemExit("existing blocks disturbed -- refusing")
    survived = sum(1 for v in before_names if probe(new_raw, v))
    print(f"  [OK ] all {len(before_names)} pre-existing blocks intact "
          f"({survived} re-extract)")

    if not args.write:
        print("\nDRY RUN -- pass --write to append")
        return

    shutil.copy2(PROMPTS, BACKUP)
    PROMPTS.write_text(new_raw, encoding="utf-8")
    print(f"\nbacked up -> {BACKUP.name}")
    print(f"appended {NEW_VERSION} ({len(block)} chars)")
    check = PROMPTS.read_text(encoding="utf-8")
    if not probe(check, NEW_VERSION):
        raise SystemExit("POST-WRITE: does not extract -- restore the backup")
    print(f"verified on disk: {len(block_names(check))} blocks")


if __name__ == "__main__":
    main()
