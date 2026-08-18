"""
Submit luna50_batch_input.jsonl to the OpenAI Batch API, wait, download results.

Standalone: needs only `openai` and an API key. Everything else -- the prompt,
the product text -- is already inside the batch file.

Safe to re-run. The batch ID is saved immediately after submission, so if this
script is interrupted (closed laptop, lost connection) the next run RESUMES the
same batch rather than submitting a second one. Submitting twice costs twice
and produces two sets of results.

Usage:
    pip install openai
    set OPENAI_API_KEY=sk-...        (Windows)
    export OPENAI_API_KEY=sk-...     (Mac/Linux)
    python run_luna50.py
"""
import os
import sys
import json
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    raise SystemExit("openai package not installed. Run:  pip install openai")

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
BATCH_INPUT = HERE / "luna50_batch_input.jsonl"
BATCH_ID_FILE = HERE / "luna50_batch_id.json"
OUTPUT = HERE / "luna50_output.jsonl"
ERRORS = HERE / "luna50_errors.jsonl"

POLL_SECONDS = 30
TIMEOUT_SECONDS = 24 * 60 * 60      # the Batch API's own completion window


def get_client():
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "OPENAI_API_KEY is not set.\n"
            "  Windows : set OPENAI_API_KEY=sk-...\n"
            "  Mac/Linux: export OPENAI_API_KEY=sk-...")
    if key.startswith("your") or key == "sk-...":
        raise SystemExit("OPENAI_API_KEY looks like a placeholder, not a real key.")
    return OpenAI(api_key=key)


def submit(client):
    if not BATCH_INPUT.exists():
        raise SystemExit(f"{BATCH_INPUT.name} not found -- run this script from "
                         f"inside the luna50_run folder.")
    n = sum(1 for line in open(BATCH_INPUT, encoding="utf-8") if line.strip())
    print(f"Uploading {BATCH_INPUT.name} ({n} requests, "
          f"{BATCH_INPUT.stat().st_size // 1024} KB)...")
    upload = client.files.create(file=open(BATCH_INPUT, "rb"), purpose="batch")
    batch = client.batches.create(
        input_file_id=upload.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": "luna50 V4.7 extraction test"})
    BATCH_ID_FILE.write_text(json.dumps({"batch_id": batch.id}, indent=2),
                             encoding="utf-8")
    print(f"Submitted. Batch ID: {batch.id}")
    print(f"Saved to {BATCH_ID_FILE.name} -- re-running this script resumes "
          f"this batch instead of submitting a new one.")
    return batch.id


def main():
    client = get_client()

    if BATCH_ID_FILE.exists():
        batch_id = json.loads(BATCH_ID_FILE.read_text(encoding="utf-8"))["batch_id"]
        print(f"Resuming existing batch {batch_id}")
        print(f"(Delete {BATCH_ID_FILE.name} if you truly want to submit a new one.)")
    else:
        batch_id = submit(client)

    print("\nWaiting for completion. Typically 3-15 minutes; the API allows up "
          "to 24 hours.")
    print("Safe to press Ctrl+C -- re-run this script later to pick up where "
          "it left off.\n")

    started = time.time()
    while True:
        batch = client.batches.retrieve(batch_id)
        rc = batch.request_counts
        elapsed = int(time.time() - started)
        print(f"  [{elapsed:>5}s] {batch.status:<12} "
              f"{rc.completed}/{rc.total} done, {rc.failed} failed")

        if batch.status == "completed":
            break
        if batch.status in ("failed", "expired", "cancelled"):
            print(f"\nBatch ended with status: {batch.status}")
            if batch.error_file_id:
                errs = client.files.content(batch.error_file_id).text
                ERRORS.write_text(errs, encoding="utf-8")
                print(f"Errors written to {ERRORS.name}")
            raise SystemExit(1)
        if time.time() - started > TIMEOUT_SECONDS:
            raise SystemExit("Timed out. Re-run to resume.")
        time.sleep(POLL_SECONDS)

    text = client.files.content(batch.output_file_id).text
    OUTPUT.write_text(text, encoding="utf-8")
    n = sum(1 for line in text.splitlines() if line.strip())
    print(f"\nDone. {n} responses written to {OUTPUT.name}")

    if batch.error_file_id:
        errs = client.files.content(batch.error_file_id).text
        ERRORS.write_text(errs, encoding="utf-8")
        print(f"Some requests errored -- see {ERRORS.name}")

    print("\nNext step:  python check_luna50.py")


if __name__ == "__main__":
    main()
