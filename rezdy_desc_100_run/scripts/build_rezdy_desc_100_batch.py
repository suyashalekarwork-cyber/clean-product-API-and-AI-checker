"""Build the Round 1 batch: 100 hardest Rezdy descriptions x SYSTEM_PROMPT_RZ_DESC_V1.

PRE-FLIGHT CHECKS, all of which refuse to write rather than warn. Each one is a
failure that has already happened on this project:

  1. THE CONVERSION IS LOSSLESS for every product in the batch. The converter
     sits in front of the model, so anything it drops is gone before a person or
     a gate can see it -- and would then be scored as the model's loss.
  2. NO PROMPT CONTAMINATION IS POSSIBLE TO MISS. The prompt's worked examples
     use invented operators (Sample Marina, Acme Tours, example.test). If those
     strings appear in a supplier's raw text the assertion is useless for that
     product, so the builder checks and says so.
  3. UNIQUE custom_ids, tagged with model + prompt version, so two runs can
     never be silently merged.
  4. FILE SIZE under the Batch API's 200 MB limit.

The user message frames the text as the SOURCE OF TRUTH, same as both Fareharbor
lineages -- the phrase is load-bearing, not decoration: it is what the VERBATIM
and NO INVENTION rules point back at.

Writes rezdy_desc_100_batch.jsonl.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
sys.path.insert(0, str(TEST_DIR))

from rezdy_common import (RAW_DIR, conversion_losses,  # noqa: E402
                          html_to_markdown)
from build_rezdy_desc_prompt import COLUMNS, extract_prompt  # noqa: E402

PROMPTS = ROOT / "config" / "rezdy_prompts.txt"
PRODUCTS = TEST_DIR / "rezdy_desc_100_products.json"

# Which prompt version this batch runs. The A/B depends on the PRODUCTS being
# identical and ONLY the prompt changing, so both are named from one place.
NEW_VERSION = os.environ.get("RZ_PROMPT", "SYSTEM_PROMPT_RZ_DESC_V1")
TAG_ENV = os.environ.get("RZ_TAG", "rzd1")
OUT_JSONL = TEST_DIR / f"rezdy_desc_100_batch_{TAG_ENV}.jsonl"

MODEL = "gpt-5.6-luna"
MAX_COMPLETION_TOKENS = 8000
TAG = TAG_ENV                      # prompt lineage tag, in every custom_id
MAX_BYTES = 200 * 1024 * 1024

# The invented names in the prompt's worked examples. Their appearance in OUTPUT
# proves contamination -- unless a supplier genuinely wrote them, which is what
# check 2 rules out.
SENTINELS = ["Sample Marina", "Sample Charters", "Acme Tours", "example.test"]


def user_message(converted):
    return f"=== RAW DESCRIPTION (source of truth) ===\n{converted}"


def main():
    prompt = extract_prompt(PROMPTS.read_text(encoding="utf-8"), NEW_VERSION)
    print(f"{NEW_VERSION}: {len(prompt):,} chars")

    products = json.loads(PRODUCTS.read_text(encoding="utf-8"))
    print(f"products: {len(products)}")

    lines, seen, contaminated = [], set(), []
    for p in products:
        pid = p["product_id"]
        hits = list(RAW_DIR.glob(f"Rezdy-*-{pid}.json"))
        if len(hits) != 1:
            raise SystemExit(f"REFUSING TO WRITE -- {pid}: {len(hits)} raw files")
        raw = json.loads(hits[0].read_text(encoding="utf-8"))["product"].get(
            "description") or ""

        # CHECK 1 -- lossless conversion
        lost = conversion_losses(raw)
        if lost:
            raise SystemExit(
                f"REFUSING TO WRITE -- {pid}: conversion drops {len(lost)} "
                f"word(s) {lost[:8]}. The model would never see this text. Fix "
                f"the converter; do not lower the gate.")
        converted = html_to_markdown(raw)

        # CHECK 2 -- would a sentinel be ambiguous for this product?
        for s in SENTINELS:
            if s.lower() in converted.lower():
                contaminated.append((pid, s))

        # CHECK 3 -- unique, tagged custom_id
        cid = f"{pid}|{MODEL}|desc|{TAG}"
        if cid in seen:
            raise SystemExit(f"REFUSING TO WRITE -- duplicate custom_id {cid}")
        seen.add(cid)

        lines.append(json.dumps({
            "custom_id": cid,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_message(converted)},
                ],
                "max_completion_tokens": MAX_COMPLETION_TOKENS,
            },
        }, ensure_ascii=False))

    blob = "\n".join(lines) + "\n"
    size = len(blob.encode("utf-8"))
    if size > MAX_BYTES:
        raise SystemExit(f"REFUSING TO WRITE -- {size/1e6:.0f} MB exceeds the "
                         f"200 MB Batch API limit")

    OUT_JSONL.write_text(blob, encoding="utf-8")

    print(f"  check 1 lossless conversion : PASS (all {len(products)})")
    if contaminated:
        print(f"  check 2 sentinel names      : {len(contaminated)} product(s) "
              f"contain a sentinel in their RAW text -- the contamination "
              f"assertion cannot be trusted for these: {contaminated}")
    else:
        print(f"  check 2 sentinel names      : PASS (none appear in any raw text)")
    print(f"  check 3 unique custom_ids   : PASS ({len(seen)})")
    print(f"  check 4 file size           : PASS ({size/1e6:.1f} MB)")

    # Sizing, so the token cap is never a surprise at 3,000-product scale.
    est_tok = sum(len(l) for l in lines) // 4
    print(f"\nrequests      : {len(lines)}")
    print(f"file          : {size/1e6:.1f} MB")
    print(f"~tokens       : {est_tok:,} ({est_tok/len(lines):,.0f}/request)")
    print(f"expected keys : {len(COLUMNS)}")
    print(f"\nwrote {OUT_JSONL}")


if __name__ == "__main__":
    main()
