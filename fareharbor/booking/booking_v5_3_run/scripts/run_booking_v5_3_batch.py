"""
Submit booking_v5_3_100_batch.jsonl to the OpenAI Batch API and poll until done.

Writes:
  booking_v5_3_100_output.jsonl  -- successful responses
  booking_v5_3_100_errors.jsonl  -- errors, if any

Same skeleton as run_v5_3_hard100_batch.py. One addition: the post-run tally
also counts responses whose key set is not the expected 15, because this is the
first run of a new schema and a silently-renamed key would otherwise only
surface much later. (The description side hit exactly this -- 51 of 1,000
responses emitted redo_desc_group_size instead of redo_group_size.)
"""
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv  # noqa: E402
from openai import OpenAI  # noqa: E402

TEST_DIR = Path(__file__).resolve().parent
load_dotenv(TEST_DIR / ".env")

IN_JSONL = TEST_DIR / "booking_v5_3_100_batch.jsonl"
OUT_JSONL = TEST_DIR / "booking_v5_3_100_output.jsonl"
ERR_JSONL = TEST_DIR / "booking_v5_3_100_errors.jsonl"
EXPECTED = 100
POLL_INTERVAL = 20
TIMEOUT_SECONDS = 90 * 60

EXPECTED_KEYS = {
    "redo_booking_notes",
    "redo_booking_highlights",
    "redo_booking_what_to_bring",
    "redo_booking_what_not_to_bring",
    "redo_booking_what_included",
    "redo_booking_what_excluded",
    "redo_booking_extras",
    "redo_booking_meeting_point",
    "redo_booking_check_in",
    "redo_booking_before_arrival",
    "redo_booking_departure_info",
    "redo_booking_itinerary",
    "redo_booking_duration_text",
    "redo_booking_important_info",
    "redo_booking_health_safety",
    "redo_booking_restrictions",
    "redo_booking_special_requirements",
    "redo_booking_accessibility",
    "redo_booking_group_size",
    "redo_booking_cancellation",
    "redo_booking_disclaimers",
    "redo_booking_pricing",
    "redo_booking_faqs",
    "redo_booking_contact",
    "redo_booking_flags",
}


# gpt-5.6-luna intermittently closes its JSON with a stray `,"` before the brace
# -- 1-2 products per run, different ones each time. Unrepaired they are silently
# dropped and read as "empty".
STRAY_COMMA = re.compile(r',\s*"\s*\}\s*$')
FENCE = re.compile(r"^```(?:json)?\s*|\s*```$")


def parse_content(text):
    t = FENCE.sub("", text.strip())
    try:
        return json.loads(t), False
    except json.JSONDecodeError:
        try:
            return json.loads(STRAY_COMMA.sub("}", t)), True
        except json.JSONDecodeError:
            return None, False


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

    print("\nkey-set check (new schema -- watch for renamed keys):")
    for shape, n in keyshapes.most_common():
        s = set(shape)
        if s == EXPECTED_KEYS:
            print(f"  {n:4d}  exactly the expected 25 keys")
        else:
            print(f"  {n:4d}  MISMATCH  missing={sorted(EXPECTED_KEYS - s)}  "
                  f"extra={sorted(s - EXPECTED_KEYS)}")


if __name__ == "__main__":
    main()
