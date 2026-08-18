"""
Build the Batch API input for SYSTEM_PROMPT_FH_BOOKING_V5_4 on the 1000 NEW
random products.

Same selection file, same raw text, same model, same settings. The ONLY thing
that differs from booking_v5_3_500_batch.jsonl is the system prompt. That is
what makes the two runs a clean A/B: any difference in the output is caused by
the 13-line RULE 8 change or by run-to-run noise, and nothing else.

Run-to-run noise is REAL and measured on this project: re-running identical
products on an identical prompt made 4 of 6 defects vanish. So the fix must be
judged on whether THE SPECIFIC 31 LOST URLS come back, not on whether an
aggregate count moved.

Writes booking_v5_4_1000_batch.jsonl. Do NOT commit it.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import make_request        # noqa: E402
from booking_common import load_raw                            # noqa: E402
from build_booking_v5_3_batch import (                         # noqa: E402
    EXPECTED_KEYS, MODEL, extract_prompt, load_model_cfg,
    build_booking_user_message,
)

PROMPT_VERSION = "SYSTEM_PROMPT_FH_BOOKING_V5_4"
TAG = "bv54"
PROMPTS_FILE = ROOT / "config" / "fareharbor_prompts.txt"
SELECTION = TEST_DIR / "booking1000_products.json"
OUT_JSONL = TEST_DIR / "booking_v5_4_1000_batch.jsonl"
MAX_FILE_MB = 200


def main():
    system_prompt = extract_prompt(
        PROMPTS_FILE.read_text(encoding="utf-8"), PROMPT_VERSION)

    leaked = sorted(set(re.findall(r"redo_desc_\w+", system_prompt)))
    if leaked:
        raise SystemExit(f"desc field names leaked: {leaked}")
    for k in EXPECTED_KEYS:
        if f'"{k}": ""' not in system_prompt:
            raise SystemExit(f"prompt schema line is missing {k}")

    # The V5.4-specific content must actually be in there -- otherwise this is
    # silently a second V5.3 run and the comparison would show "no change".
    for label, needle in [
        ("plain image shape", "![Jetty at low tide]"),
        ("image inside link", "[![logo]"),
        ("alt text is the supplier's", "Do not improve it, replace it, or describe"),
    ]:
        if needle not in system_prompt:
            raise SystemExit(f"V5.4 change missing from the prompt: {label}")
    print(f"prompt {PROMPT_VERSION}: {len(system_prompt)} chars, 25 keys, "
          "V5.4 image rules present")

    cfg = load_model_cfg(MODEL)
    ids = json.loads(SELECTION.read_text(encoding="utf-8"))["product_ids"]

    requests, skipped, total_chars = [], [], 0
    for pid in ids:
        try:
            _, raw_bn = load_raw(pid)
        except RuntimeError as exc:
            skipped.append((pid, str(exc)))
            continue
        if not raw_bn.strip():
            skipped.append((pid, "empty booking notes"))
            continue
        total_chars += len(raw_bn)
        requests.append(make_request(
            custom_id=f"{pid}|{MODEL}|booking|{TAG}",
            model=MODEL,
            model_cfg=cfg,
            system_prompt=system_prompt,
            user_message=build_booking_user_message(raw_bn),
        ))

    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for r in requests:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    size_mb = OUT_JSONL.stat().st_size / 1e6
    print(f"requests built: {len(requests)}   raw chars: {total_chars:,}")
    print(f"wrote {OUT_JSONL.name} ({size_mb:.1f} MB -- do not commit)")
    if size_mb > MAX_FILE_MB:
        raise SystemExit(f"{size_mb:.0f} MB over the {MAX_FILE_MB} MB limit")

    # NO A/B CHECK HERE. The 500 had a V5.3 counterpart to diff against;
    # this 1000 has no prior run, so there is nothing to compare and the
    # check is removed rather than pointed at an unrelated file.

    cids = [json.loads(l)["custom_id"] for l in OUT_JSONL.open(encoding="utf-8")]
    assert len(set(cids)) == len(cids), "duplicate custom_id"
    assert all(c.endswith(f"|booking|{TAG}") for c in cids), "untagged custom_id"
    print(f"custom_id check: {len(cids)} unique, all tagged |booking|{TAG}")


if __name__ == "__main__":
    main()
