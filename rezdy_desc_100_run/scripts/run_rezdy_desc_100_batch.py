"""Submit rezdy_desc_100_batch.jsonl and poll to done.

Same skeleton as run_booking_v5_4_500_batch.py, and the disciplines are the same
because each was paid for:

  * THE BATCH ID IS WRITTEN TO DISK BEFORE POLLING. A long batch does not
    survive a session restart, and without the id there is no way to recover a
    run already paid for.
  * RESUMABLE -- re-running reattaches to the saved id instead of paying twice.
  * A FAILED BATCH IS REPORTED LOUDLY, never grouped with completed. A runner
    that lumped `failed` in with `completed` once printed "ALL DONE" over a 63%
    failure rate.
  * THE KEY-SET CHECK STAYS. gpt-5.6-luna mangles a key name in 0.1-0.5% of
    responses (`redo_bookingwhat_excluded`, `redo_booking_meETING_POINT`). Every
    instance found so far was empty so nothing was lost -- but on a filled
    column the content would vanish silently, and this check is the only thing
    that sees it.
  * ALL THREE JSON REPAIRS are applied on load (stray comma, orphaned string,
    invalid escape -- the last strictly as a final resort, because applied
    unconditionally it breaks a response that parses fine on its own).
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

from booking_common import parse_booking_json          # noqa: E402
from build_rezdy_desc_prompt import COLUMNS            # noqa: E402

# TAG names the prompt lineage. The A/B keeps the PRODUCTS fixed and changes
# only the prompt, so every file this run touches is tag-suffixed and the two
# runs can never overwrite or be merged into each other.
TAG = os.environ.get("RZ_TAG", "rzd1")
_sfx = "" if TAG == "rzd1" else f"_{TAG}"
IN_JSONL = TEST_DIR / f"rezdy_desc_100_batch{_sfx or ''}.jsonl" if TAG == "rzd1" else TEST_DIR / f"rezdy_desc_100_batch_{TAG}.jsonl"
OUT_JSONL = TEST_DIR / f"rezdy_desc_100_output{_sfx}.jsonl"
ERR_JSONL = TEST_DIR / f"rezdy_desc_100_errors{_sfx}.jsonl"
ID_FILE = TEST_DIR / f"rezdy_desc_100_batch_id{_sfx}.json"
EXPECTED = 100
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
        "run": f"rezdy_desc_100_{TAG}", "prompt_tag": TAG,
    }, indent=1), encoding="utf-8")
    print(f"batch id: {batch.id}  -> saved to {ID_FILE.name}")
    return batch


def main():
    if OUT_JSONL.exists():
        print(f"{OUT_JSONL.name} already exists -- nothing to do.")
        return
    if not IN_JSONL.exists():
        raise SystemExit(f"missing {IN_JSONL} -- run build_rezdy_desc_100_batch.py")

    n_in = sum(1 for _ in IN_JSONL.open(encoding="utf-8"))
    if n_in != EXPECTED:
        raise SystemExit(f"expected {EXPECTED} requests, file has {n_in}")

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY not set -- check .env")
    client = OpenAI()

    batch = submit_or_reattach(client, n_in)
    started = time.time()
    last = None
    while batch.status not in ("completed", "failed", "expired", "cancelled"):
        if time.time() - started > TIMEOUT_SECONDS:
            raise SystemExit(f"timed out after {TIMEOUT_SECONDS/3600:.0f}h -- "
                             f"batch {batch.id} still {batch.status}")
        c = batch.request_counts
        line = f"{batch.status}  {c.completed}/{c.total} done, {c.failed} failed"
        if line != last:
            print(f"  [{time.strftime('%H:%M:%S')}] {line}")
            last = line
        time.sleep(POLL_INTERVAL)
        batch = client.batches.retrieve(batch.id)

    print(f"\nfinal status: {batch.status}")
    if batch.status != "completed":
        raise SystemExit(f"BATCH DID NOT COMPLETE ({batch.status}). "
                         f"errors: {batch.errors}")

    if batch.error_file_id:
        ERR_JSONL.write_bytes(client.files.content(batch.error_file_id).read())
        print(f"errors written to {ERR_JSONL.name} -- READ THIS")

    OUT_JSONL.write_bytes(client.files.content(batch.output_file_id).read())
    print(f"wrote {OUT_JSONL.name}")
    inspect()


def inspect():
    n = 0
    repairs, bad_keys, empty = Counter(), [], 0
    unparseable, truncated = [], []
    for line in OUT_JSONL.open(encoding="utf-8"):
        rec = json.loads(line)
        pid = rec["custom_id"].split("|")[0]
        n += 1
        body = rec.get("response", {}).get("body", {})
        choice = (body.get("choices") or [{}])[0]
        if choice.get("finish_reason") == "length":
            truncated.append(pid)
        fields, note = parse_booking_json(
            choice.get("message", {}).get("content", ""))
        if note:
            repairs[note] += 1
        if fields is None:
            unparseable.append(pid)
            continue
        missing = set(COLUMNS) - set(fields)
        extra = set(fields) - set(COLUMNS)
        if missing or extra:
            bad_keys.append((pid, sorted(missing), sorted(extra)))
        if not any((fields.get(c) or "").strip() for c in COLUMNS):
            empty += 1

    print(f"\nresponses          : {n}")
    print(f"unparseable        : {len(unparseable)}  {unparseable[:8]}")
    print(f"truncated (length) : {len(truncated)}  {truncated[:8]}")
    print(f"wrong key set      : {len(bad_keys)}  {bad_keys[:3]}")
    print(f"entirely empty     : {empty}")
    if repairs:
        print(f"json repairs       : {dict(repairs)}")


if __name__ == "__main__":
    main()
