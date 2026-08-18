"""
Submit booking_v5_4_1000_batch.jsonl and poll to done.

Same skeleton as run_booking_v5_3_500_batch.py -- batch id written to disk
BEFORE polling, resumable, and a failed batch reported loudly rather than
grouped with completed.

Writes booking_v5_4_1000_{batch_id.json,output.jsonl,errors.jsonl}.
"""
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv  # noqa: E402
from openai import OpenAI       # noqa: E402

TEST_DIR = Path(__file__).resolve().parent
load_dotenv(TEST_DIR / ".env")
sys.path.insert(0, str(TEST_DIR))

from run_booking_v5_3_batch import EXPECTED_KEYS, parse_content  # noqa: E402

IN_JSONL = TEST_DIR / "booking_v5_4_1000_batch.jsonl"
OUT_JSONL = TEST_DIR / "booking_v5_4_1000_output.jsonl"
ERR_JSONL = TEST_DIR / "booking_v5_4_1000_errors.jsonl"
ID_FILE = TEST_DIR / "booking_v5_4_1000_batch_id.json"
EXPECTED = 1000
POLL_INTERVAL = 30
TIMEOUT_SECONDS = 6 * 60 * 60


def submit_or_reattach(client, n_in):
    if ID_FILE.exists():
        rec = json.loads(ID_FILE.read_text(encoding="utf-8"))
        print(f"reattaching to {rec['batch_id']} (submitted {rec['submitted_at']})")
        return client.batches.retrieve(rec["batch_id"])
    print(f"uploading {IN_JSONL.name} ({n_in} requests) ...")
    upload = client.files.create(file=IN_JSONL.open("rb"), purpose="batch")
    batch = client.batches.create(
        input_file_id=upload.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    ID_FILE.write_text(json.dumps({
        "batch_id": batch.id, "input_file_id": upload.id, "n_requests": n_in,
        "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "run": "booking_v5_4_1000",
    }, indent=1), encoding="utf-8")
    print(f"batch id: {batch.id}  -> saved to {ID_FILE.name}")
    return batch


def main():
    if OUT_JSONL.exists():
        print(f"{OUT_JSONL.name} already exists -- nothing to do.")
        return
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    n_in = sum(1 for _ in IN_JSONL.open(encoding="utf-8"))
    if n_in != EXPECTED:
        raise SystemExit(f"expected {EXPECTED} requests, found {n_in}")

    batch = submit_or_reattach(client, n_in)
    start = time.time()
    while True:
        batch = client.batches.retrieve(batch.id)
        elapsed = int(time.time() - start)
        c = batch.request_counts
        print(f"  [{elapsed:>5}s] {batch.status}  "
              f"completed={c.completed}/{c.total} failed={c.failed}", flush=True)
        if batch.status in ("completed", "failed", "expired", "cancelled"):
            break
        if elapsed > TIMEOUT_SECONDS:
            print(f"\n!! still {batch.status} after {elapsed}s -- batch is live, "
                  f"re-run to reattach via {ID_FILE.name}")
            return
        time.sleep(POLL_INTERVAL)

    if batch.status != "completed":
        print(f"\n{'!' * 70}\nBATCH DID NOT COMPLETE -- status={batch.status}")
        if getattr(batch, "errors", None):
            print(f"errors: {batch.errors}")
        print(f"{'!' * 70}")

    if batch.output_file_id:
        OUT_JSONL.write_text(
            client.files.content(batch.output_file_id).text, encoding="utf-8")
        print(f"wrote {OUT_JSONL.name}")
    if batch.error_file_id:
        ERR_JSONL.write_text(
            client.files.content(batch.error_file_id).text, encoding="utf-8")
        print(f"wrote {ERR_JSONL.name}  <-- ERRORS PRESENT")

    if not OUT_JSONL.exists():
        return
    truncated = unparseable = ok = repaired = 0
    keyshapes = Counter()
    for line in OUT_JSONL.open(encoding="utf-8"):
        row = json.loads(line)
        choice = row["response"]["body"]["choices"][0]
        if choice.get("finish_reason") != "stop":
            truncated += 1
        fields, was_repaired = parse_content(choice["message"]["content"])
        if fields is None:
            unparseable += 1
            continue
        ok += 1
        repaired += was_repaired
        keyshapes[tuple(sorted(fields))] += 1
    print(f"\nparsed ok: {ok}   truncated: {truncated}   "
          f"unparseable: {unparseable}   json-repaired: {repaired}")
    for shape, n in keyshapes.most_common():
        s = set(shape)
        print(f"  {n:4d}  " + ("exactly the expected 25 keys" if s == EXPECTED_KEYS
              else f"MISMATCH missing={sorted(EXPECTED_KEYS-s)} extra={sorted(s-EXPECTED_KEYS)}"))


if __name__ == "__main__":
    main()
