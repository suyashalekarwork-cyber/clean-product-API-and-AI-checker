"""
The anti-drift guard for the V5.3 reviewer.

Every one of the six previous checker prompts died the same way: someone
hand-copied the extractor's field definitions into a separate file, the
extractor moved on, and the checker went stale silently. judge_fields.py still
carries DESC_V2's definitions; qa_bot_v2/config.py pins DESC_V4_5.

This module never re-types the contract. It slices "THE COLUMNS:" ...
"ITINERARY LINE TEST" straight out of the live SYSTEM_PROMPT_FH_DESC_V5_3 body,
so the reviewer is held to the same bytes the extractor was given.

If the slice ever fails, the build STOPS. There is no fallback -- a checker
running on a guessed contract is worse than no checker.

    python review_contract.py        # self-check, prints the slice stats
"""
import re
import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
PROMPTS_FILE = ROOT / "config" / "fareharbor_prompts.txt"

EXTRACTOR_VERSION = "SYSTEM_PROMPT_FH_DESC_V5_3"

# Rollback is these two constants and nothing else -- every version stays
# extractable, so going back to V1 is a one-line edit. See REVIEW_PROMPT_LOG.md.
REVIEW_VERSION = "SYSTEM_PROMPT_FH_REVIEW_V3"
VERIFY_VERSION = "SYSTEM_PROMPT_FH_REVIEW_VERIFY_V3"

START_MARKER = "THE COLUMNS:"
END_MARKER = "ITINERARY LINE TEST"

# The 21 content columns the extractor is contracted to fill. redo_flags is the
# 22nd output key but is the model's own commentary, not a content column.
EXPECTED_KEYS = {
    "redo_desc_about",
    "redo_desc_important_info",
    "redo_desc_highlights",
    "redo_desc_what_included",
    "redo_desc_what_excluded",
    "redo_desc_extras",
    "redo_desc_itinerary",
    "redo_desc_what_to_bring",
    "redo_desc_duration_text",
    "redo_desc_cancellation",
    "redo_desc_check_in",
    "redo_desc_accessibility",
    "redo_desc_restrictions",
    "redo_desc_special_requirements",
    "redo_desc_faqs",
    "redo_desc_pricing",
    "redo_desc_disclaimers",
    "redo_meeting_point",
    "redo_group_size",
    "redo_min_age",
    "redo_max_age",
}
ALL_OUTPUT_KEYS = EXPECTED_KEYS | {"redo_flags"}

# Some responses spell this key the long way. Same column, different spelling.
KEY_ALIASES = {"redo_desc_group_size": "redo_group_size"}


class ContractError(RuntimeError):
    """The slice failed. Stop the build; never fall back to a hand-typed copy."""


def extract_prompt(raw, version):
    """Exact-version block extractor -- same contract as build_v5_3_*_batch.py."""
    v = re.escape(version)
    pattern = (
        r"PROMPT:\s*" + v + r"\s*\n"
        r".*?\n=+\n\n"
        r"(.*?)"
        r"\n\n=+\nEND OF " + v + r"\s*$"
    )
    m = re.search(pattern, raw, re.DOTALL | re.MULTILINE)
    if not m:
        raise ContractError("Could not extract prompt body for " + version)
    return m.group(1).strip()


def _prompts_raw():
    return PROMPTS_FILE.read_text(encoding="utf-8")


def column_contract():
    """The 21-column definition block, sliced verbatim out of the V5.3 prompt."""
    body = extract_prompt(_prompts_raw(), EXTRACTOR_VERSION)

    for marker in (START_MARKER, END_MARKER):
        n = body.count(marker)
        if n != 1:
            raise ContractError(
                "marker %r appears %d times in %s -- the slice is ambiguous"
                % (marker, n, EXTRACTOR_VERSION)
            )

    start = body.index(START_MARKER)
    end = body.index(END_MARKER)
    if end <= start:
        raise ContractError("markers out of order -- the prompt was restructured")

    slice_ = body[start:end].rstrip()

    found = set(re.findall(r"redo_[a-z_]+", slice_))
    missing = EXPECTED_KEYS - found
    extra = found - ALL_OUTPUT_KEYS
    if missing:
        raise ContractError("contract slice is missing columns: " + str(sorted(missing)))
    if extra:
        raise ContractError("contract slice names unknown columns: " + str(sorted(extra)))

    return slice_


def review_prompt():
    """Pass-1 system prompt with the live contract injected."""
    return _fill(extract_prompt(_prompts_raw(), REVIEW_VERSION))


def verify_prompt():
    """Pass-2 system prompt with the live contract injected."""
    return _fill(extract_prompt(_prompts_raw(), VERIFY_VERSION))


def _fill(template):
    if "{COLUMN_CONTRACT}" not in template:
        raise ContractError("prompt has no {COLUMN_CONTRACT} placeholder")
    filled = template.replace("{COLUMN_CONTRACT}", column_contract())
    for dead in ("redo_booking_", "redo_desc_requirements"):
        if dead in filled:
            raise ContractError("dead-schema marker present: " + dead)
    return filled


def normalise_keys(record):
    """Fold redo_desc_group_size onto redo_group_size. Never lose a value."""
    out = {}
    for k, v in record.items():
        k2 = KEY_ALIASES.get(k, k)
        if k2 in out and out[k2] and not v:
            continue
        out[k2] = v
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    contract = column_contract()
    keys = sorted(set(re.findall(r"redo_[a-z_]+", contract)))
    print("extractor block :", EXTRACTOR_VERSION)
    print("contract slice  :", len(contract), "chars")
    print("columns found   :", len(keys))
    for k in keys:
        print("   ", k)
    print("review prompt   :", len(review_prompt()), "chars (contract injected)")
    print("verify prompt   :", len(verify_prompt()), "chars (contract injected)")
    print("OK")


if __name__ == "__main__":
    main()
