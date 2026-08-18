"""
Build, submit and download the 100-product gpt-5.6-luna batch (V4.7 prompt).

One script rather than three, because this is a single job on a single model --
the multi-model orchestration in run_hard30_batches.py is not needed here.

The batch ID is written to disk immediately after submission so an interrupted
run resumes the same job instead of submitting, and paying for, a second one.

Parameter set is read from model_compatibility_final.json, never hardcoded:
gpt-5 family takes max_completion_tokens ONLY and rejects max_tokens and
temperature. The wrong set fails the entire batch, not one request.

Usage:
    python run_luna100.py            # build + submit + wait + download
    python run_luna100.py --build    # build the JSONL only, no API calls
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_model_comparison_batches import (
    PROMPT_PATH, extract_prompt,
    build_desc_user_message, build_booking_user_message,
)

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
PRODUCTS = TEST_DIR / "luna100_products.json"
STATE = TEST_DIR / "v500_post_fix_state.json"
COMPAT = TEST_DIR / "model_compatibility_final.json"

BATCH_INPUT = TEST_DIR / "luna100_batch_input.jsonl"
BATCH_ID_FILE = TEST_DIR / "luna100_batch_id.json"
OUTPUT = TEST_DIR / "luna100_output.jsonl"
ERRORS = TEST_DIR / "luna100_errors.jsonl"

MODEL = "gpt-5.6-luna"
DESC_VERSION = "SYSTEM_PROMPT_FH_DESC_V4_7"
BOOKING_VERSION = "SYSTEM_PROMPT_FH_BOOKING_V4_7"
MAX_COMPLETION_TOKENS = 8000
POLL_SECONDS = 30
TIMEOUT_SECONDS = 90 * 60


def build():
    raw_prompts = PROMPT_PATH.read_text(encoding="utf-8")
    desc_prompt = extract_prompt(raw_prompts, DESC_VERSION)
    booking_prompt = extract_prompt(raw_prompts, BOOKING_VERSION)
    for rule in ("NO DUPLICATION RULE:", "NO INVENTION RULE:"):
        for name, body in (("desc", desc_prompt), ("booking", booking_prompt)):
            if rule not in body:
                raise SystemExit(f"{rule!r} missing from the {name} prompt")

    compat = json.loads(COMPAT.read_text(encoding="utf-8")).get(MODEL)
    if not compat or compat.get("batch_supported") is not True:
        raise SystemExit(f"{MODEL} is not Batch-compatible per {COMPAT.name}")
    if compat["param_set"] != "max_completion_tokens":
        raise SystemExit(f"unexpected param_set {compat['param_set']!r} for {MODEL}")

    meta = json.loads(PRODUCTS.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))

    lines, skipped = [], 0
    for pid in meta["product_ids"]:
        rec = state[pid]
        for side, prompt, builder, text in (
            ("desc", desc_prompt, build_desc_user_message, rec.get("raw_desc") or ""),
            ("booking", booking_prompt, build_booking_user_message,
             rec.get("raw_booking") or ""),
        ):
            if not text.strip():
                skipped += 1
                continue
            lines.append(json.dumps({
                "custom_id": f"{pid}|{MODEL}|{side}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": builder(text)},
                    ],
                    "max_completion_tokens": MAX_COMPLETION_TOKENS,
                },
            }, ensure_ascii=False))

    # LF endings: git's autocrlf rewrote a previous batch file such that the
    # stored blob no longer parsed as JSON
    BATCH_INPUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    assert len(lines) == meta["n_requests"], \
        f"built {len(lines)} requests, expected {meta['n_requests']}"
    print(f"Built {BATCH_INPUT.name}: {len(lines)} requests "
          f"({BATCH_INPUT.stat().st_size // 1024} KB), {skipped} empty sides skipped")
    return len(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="build only, no API calls")
    args = ap.parse_args()

    expected = build()
    if args.build:
        return

    load_dotenv(TEST_DIR / ".env")
    key = os.environ.get("OPENAI_API_KEY")
    if not key or key == "your_key_here":
        raise SystemExit("OPENAI_API_KEY not set")
    client = OpenAI(api_key=key)

    if BATCH_ID_FILE.exists():
        batch_id = json.loads(BATCH_ID_FILE.read_text(encoding="utf-8"))["batch_id"]
        print(f"Resuming existing batch {batch_id}")
    else:
        upload = client.files.create(file=open(BATCH_INPUT, "rb"), purpose="batch")
        batch = client.batches.create(
            input_file_id=upload.id, endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"description": "luna100 V4.7 representative sample"})
        batch_id = batch.id
        BATCH_ID_FILE.write_text(json.dumps({"batch_id": batch_id}, indent=2),
                                 encoding="utf-8")
        print(f"Submitted. Batch ID: {batch_id}")

    started = time.time()
    while True:
        batch = client.batches.retrieve(batch_id)
        rc = batch.request_counts
        print(f"  [{int(time.time() - started):>5}s] {batch.status:<12} "
              f"{rc.completed}/{rc.total} failed={rc.failed}")
        if batch.status == "completed":
            break
        if batch.status in ("failed", "expired", "cancelled"):
            if batch.error_file_id:
                ERRORS.write_text(client.files.content(batch.error_file_id).text,
                                  encoding="utf-8")
                print(f"  errors -> {ERRORS.name}")
            raise SystemExit(f"batch ended: {batch.status}")
        if time.time() - started > TIMEOUT_SECONDS:
            raise SystemExit("timed out -- re-run to resume")
        time.sleep(POLL_SECONDS)

    text = client.files.content(batch.output_file_id).text
    OUTPUT.write_text(text, encoding="utf-8", newline="\n")
    n = sum(1 for line in text.splitlines() if line.strip())
    print(f"\nDone. {n}/{expected} responses -> {OUTPUT.name}")
    if batch.error_file_id:
        ERRORS.write_text(client.files.content(batch.error_file_id).text,
                          encoding="utf-8")
        print(f"Some requests errored -- see {ERRORS.name}")


if __name__ == "__main__":
    main()
