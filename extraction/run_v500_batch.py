"""
Submit the 1,000-request v500_batch.jsonl as ONE Batch API job, poll every
60s, download output. On completion or partial failure, extract every
failed custom_id (error response or missing response) into v500_failures.csv
with the reason. Skip-and-continue: never halts, just records failures.

Usage:
    python run_v500_batch.py
"""
import sys
import json
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
import os

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ENV_PATH = TEST_DIR / ".env"
INPUT_JSONL = TEST_DIR / "v500_batch.jsonl"
OUTPUT_JSONL = TEST_DIR / "v500_output.jsonl"
FAILURES_CSV = TEST_DIR / "v500_failures.csv"

POLL_INTERVAL_SECONDS = 60

load_dotenv(ENV_PATH)
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key or api_key == "your_key_here":
    print(f"OPENAI_API_KEY is missing in {ENV_PATH}.")
    sys.exit(1)

from openai import OpenAI

client = OpenAI(api_key=api_key)

print("=" * 80)
print("STEP 1 — UPLOAD INPUT FILE")
print("=" * 80)
with open(INPUT_JSONL, "rb") as f:
    uploaded = client.files.create(file=f, purpose="batch")
print(f"Uploaded file id: {uploaded.id}")

print("\n" + "=" * 80)
print("STEP 2 — CREATE BATCH JOB")
print("=" * 80)
batch = client.batches.create(
    input_file_id=uploaded.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
)
print(f"Batch created: {batch.id}")
print(f"Status: {batch.status}")

print("\n" + "=" * 80)
print("STEP 3 — POLL BATCH STATUS (every 60s)")
print("=" * 80)
TERMINAL_STATUSES = {"completed", "failed", "expired", "cancelled"}
status = batch.status
start_time = time.time()
while status not in TERMINAL_STATUSES:
    time.sleep(POLL_INTERVAL_SECONDS)
    batch = client.batches.retrieve(batch.id)
    status = batch.status
    counts = batch.request_counts
    elapsed = round(time.time() - start_time)
    print(f"[{elapsed}s] Status: {status} | completed={counts.completed}/{counts.total} failed={counts.failed}")

total_elapsed = round(time.time() - start_time)
print(f"\nFinal status: {status} (wall-clock: {total_elapsed}s)")

print("\n" + "=" * 80)
print("STEP 4 — DOWNLOAD RESULTS")
print("=" * 80)

failure_rows = []
n_success = 0

if batch.output_file_id:
    content = client.files.content(batch.output_file_id)
    content.write_to_file(OUTPUT_JSONL)
    print(f"Downloaded output to: {OUTPUT_JSONL}")

    with open(OUTPUT_JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            custom_id = rec.get("custom_id", "")
            error = rec.get("error")
            response = rec.get("response")
            if error is not None:
                failure_rows.append({"custom_id": custom_id, "reason": f"batch error: {error}"})
                continue
            if response is None:
                failure_rows.append({"custom_id": custom_id, "reason": "no response object"})
                continue
            status_code = response.get("status_code")
            if status_code != 200:
                failure_rows.append({"custom_id": custom_id, "reason": f"HTTP {status_code}: {response.get('body')}"})
                continue
            try:
                content_str = response["body"]["choices"][0]["message"]["content"]
                json.loads(content_str)  # verify parseable
                n_success += 1
            except (KeyError, IndexError, json.JSONDecodeError, TypeError) as e:
                failure_rows.append({"custom_id": custom_id, "reason": f"unparseable content: {e}"})
else:
    print("No output_file_id on the batch — nothing downloaded.")

if batch.error_file_id:
    error_content = client.files.content(batch.error_file_id)
    error_text = error_content.text
    print("\nBatch has a separate error file:")
    print(error_text[:2000])
    for line in error_text.strip().split("\n"):
        if not line.strip():
            continue
        try:
            err_rec = json.loads(line)
            failure_rows.append({"custom_id": err_rec.get("custom_id", "unknown"), "reason": f"error file: {err_rec}"})
        except json.JSONDecodeError:
            pass

failures_df = pd.DataFrame(failure_rows)
failures_df.to_csv(FAILURES_CSV, index=False)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total requests: {batch.request_counts.total}")
print(f"Successful calls (parseable): {n_success}")
print(f"Failed/unparseable calls: {len(failure_rows)}")
print(f"Wall-clock time: {total_elapsed}s")
print(f"Wrote {len(failure_rows)} failure rows to {FAILURES_CSV}")
print("\nDONE")
