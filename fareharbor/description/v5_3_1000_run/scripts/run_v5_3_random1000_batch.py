"""
Submit v5_3_random1000_batch.jsonl to the OpenAI Batch API and poll until done.

Writes:
  v5_3_random1000_output.jsonl  -- successful responses
  v5_3_random1000_errors.jsonl  -- errors, if any
"""
import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv  # noqa: E402
from openai import OpenAI  # noqa: E402

TEST_DIR = Path(__file__).resolve().parent
load_dotenv(TEST_DIR / ".env")

IN_JSONL = TEST_DIR / "v5_3_random1000_batch.jsonl"
OUT_JSONL = TEST_DIR / "v5_3_random1000_output.jsonl"
ERR_JSONL = TEST_DIR / "v5_3_random1000_errors.jsonl"
EXPECTED = 1000
POLL_INTERVAL = 20
TIMEOUT_SECONDS = 300 * 60


def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    n_in = sum(1 for _ in IN_JSONL.open(encoding="utf-8"))
    if n_in != EXPECTED:
        raise SystemExit(f"expected {EXPECTED} requests, found {n_in}")
    print(f"uploading {IN_JSONL.name} ({n_in} requests) ...")

    upload = client.files.create(file=IN_JSONL.open("rb"), purpose="batch")
    batch = client.batches.create(
        input_file_id=upload.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    print(f"batch id: {batch.id}")

    start = time.time()
    while True:
        batch = client.batches.retrieve(batch.id)
        elapsed = int(time.time() - start)
        counts = batch.request_counts
        print(
            f"  [{elapsed:>4}s] {batch.status}  "
            f"completed={counts.completed}/{counts.total} failed={counts.failed}"
        )
        if batch.status in ("completed", "failed", "expired", "cancelled"):
            break
        if elapsed > TIMEOUT_SECONDS:
            raise SystemExit(f"timed out after {elapsed}s (status={batch.status})")
        time.sleep(POLL_INTERVAL)

    if batch.output_file_id:
        text = client.files.content(batch.output_file_id).text
        OUT_JSONL.write_text(text, encoding="utf-8")
        print(f"wrote {OUT_JSONL.name}")

    if batch.error_file_id:
        text = client.files.content(batch.error_file_id).text
        ERR_JSONL.write_text(text, encoding="utf-8")
        print(f"wrote {ERR_JSONL.name}  <-- ERRORS PRESENT")

    # Report truncation / unparseable separately -- they are different failures.
    if OUT_JSONL.exists():
        truncated = unparseable = ok = 0
        for line in OUT_JSONL.open(encoding="utf-8"):
            row = json.loads(line)
            choice = row["response"]["body"]["choices"][0]
            if choice.get("finish_reason") != "stop":
                truncated += 1
            try:
                json.loads(choice["message"]["content"])
                ok += 1
            except Exception:
                unparseable += 1
        print(f"\nparsed ok: {ok}   truncated: {truncated}   unparseable: {unparseable}")


if __name__ == "__main__":
    main()
