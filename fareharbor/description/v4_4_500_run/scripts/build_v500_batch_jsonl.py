"""
Isolated POC: build the 1,000-line (500 products x desc-v44 + booking-v44)
Batch API input JSONL. Raw-text-only user message, identical format to
run_50_sync.py (NO hints). Unchanged pipeline logic.

Usage:
    python build_v500_batch_jsonl.py
"""
import sys
import json
import glob
import re
from pathlib import Path
from html import unescape

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "Fareharbor"
PROMPT_PATH = PROJECT_ROOT / "config" / "fareharbor_prompts.txt"
TEST_DIR = Path(__file__).resolve().parent
SELECTION_CSV = TEST_DIR / "new_500_products_selection.csv"
OUT_PATH = TEST_DIR / "v500_batch.jsonl"

MODEL = "gpt-4o-mini"
TEMPERATURE = 0.1
MAX_TOKENS = 8000

BLOCK_TAG_RE = re.compile(r"</?(p|div|h[1-6]|ul|ol|li|br)\b[^>]*>", re.IGNORECASE)
ANY_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text):
    if not text:
        return ""
    text = BLOCK_TAG_RE.sub(" ", text)
    text = ANY_TAG_RE.sub("", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def extract_prompt(raw, version):
    v = re.escape(version)
    pattern = (
        r"PROMPT:\s*" + v + r"\b"
        r".*?\n=+\n\n"
        r"(.*?)"
        r"\n\n=+\nEND OF " + v + r"\s*$"
    )
    m = re.search(pattern, raw, re.DOTALL | re.MULTILINE)
    if not m:
        raise RuntimeError(f"Could not extract prompt body for {version}")
    return m.group(1).strip()


def find_raw_file(product_id):
    matches = glob.glob(str(RAW_DIR / f"Fareharbor-*-{product_id}.json"))
    if not matches:
        raise FileNotFoundError(f"No raw JSON found for product_id={product_id} in {RAW_DIR}")
    if len(matches) > 1:
        raise RuntimeError(f"Multiple raw JSON matches for product_id={product_id}: {matches}")
    return matches[0]


def build_desc_user_message(raw_description):
    content = raw_description if raw_description else "No content found in raw text for this field."
    return f"=== RAW DESCRIPTION (source of truth) ===\n{content}"


def build_booking_user_message(raw_booking_notes):
    content = raw_booking_notes if raw_booking_notes else "No content found in raw text for this field."
    return f"=== RAW BOOKING NOTES (source of truth) ===\n{content}"


def make_request(custom_id, system_prompt, user_message):
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        },
    }


def main():
    raw_prompts = PROMPT_PATH.read_text(encoding="utf-8")
    desc_prompt = extract_prompt(raw_prompts, "SYSTEM_PROMPT_FH_DESC_V4_4")
    booking_prompt = extract_prompt(raw_prompts, "SYSTEM_PROMPT_FH_BOOKING_V4_4")
    print(f"Extracted SYSTEM_PROMPT_FH_DESC_V4_4: {len(desc_prompt)} chars")
    print(f"Extracted SYSTEM_PROMPT_FH_BOOKING_V4_4: {len(booking_prompt)} chars")

    selection_df = pd.read_csv(SELECTION_CSV, dtype={"product_id": str})
    product_ids = selection_df["product_id"].tolist()
    print(f"Building batch for {len(product_ids)} products (x2 calls = {len(product_ids) * 2} lines)")

    lines_out = []
    for i, product_id in enumerate(product_ids):
        raw_path = find_raw_file(product_id)
        data = json.loads(Path(raw_path).read_text(encoding="utf-8"))
        item = data["item"]

        raw_description = strip_html(item.get("description") or "")
        raw_booking_notes = strip_html(item.get("booking_notes") or "")

        desc_req = make_request(f"{product_id}|Fareharbor|desc-v44", desc_prompt, build_desc_user_message(raw_description))
        lines_out.append(json.dumps(desc_req, ensure_ascii=False))

        booking_req = make_request(f"{product_id}|Fareharbor|booking-v44", booking_prompt, build_booking_user_message(raw_booking_notes))
        lines_out.append(json.dumps(booking_req, ensure_ascii=False))

        if (i + 1) % 100 == 0:
            print(f"  built {i + 1}/{len(product_ids)} products...")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for line in lines_out:
            f.write(line + "\n")

    assert len(lines_out) == len(product_ids) * 2, "Expected exactly 2 lines per product"
    print(f"\nWrote {len(lines_out)} lines to {OUT_PATH}")


if __name__ == "__main__":
    main()
