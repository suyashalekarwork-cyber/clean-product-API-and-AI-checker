"""
Submit the full-catalogue description chunks -- ONE AT A TIME.

WHY SEQUENTIAL. The first attempt submitted all four chunks together and two
were rejected instantly with:

    token_limit_exceeded -- Enqueued token limit reached for gpt-5.6-luna.
    Limit: 40,000,000 enqueued tokens.

Each 3,500-product chunk is ~26M enqueued tokens, so two of them exceed the cap.
Nothing was charged for the rejected chunks -- they failed before processing a
request -- but 7,000 products silently did not run. So: submit a chunk, wait for
it to finish, then submit the next.

A `failed` batch is now reported loudly rather than counted as done. The first
version treated failed/expired/cancelled the same as completed, which is how two
rejected chunks slipped past unnoticed.

Resumable: batch ids are written to v5_3_full_batch_ids.json as soon as each is
accepted, and any chunk that already has an output file on disk is skipped. Safe
to re-run after a session restart -- it will not resubmit work already paid for.
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

IDS_FILE = TEST_DIR / "v5_3_full_batch_ids.json"
POLL = 30
TIMEOUT_PER_CHUNK = 6 * 3600


def out_path(chunk_name):
    return TEST_DIR / chunk_name.replace("batch", "output")


def wait_for(client, bid, label):
    start = time.time()
    while True:
        b = client.batches.retrieve(bid)
        c = b.request_counts
        el = int(time.time() - start)
        print(f"   [{el // 60:>3}m] {label} {b.status:<11} "
              f"{c.completed}/{c.total} failed={c.failed}")
        if b.status == "completed":
            return b
        if b.status in ("failed", "expired", "cancelled"):
            print(f"   !! {label} {b.status.upper()}")
            if b.errors:
                d = b.errors.model_dump() if hasattr(b.errors, "model_dump") else b.errors
                for e in (d.get("data") or []):
                    print(f"      {e.get('code')}: {e.get('message')}")
            return b
        if el > TIMEOUT_PER_CHUNK:
            print(f"   !! {label} timed out after {el}s -- id saved, re-run to resume")
            return None
        time.sleep(POLL)


def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    chunks = sorted(TEST_DIR.glob("v5_3_full_batch_*.jsonl"))
    if not chunks:
        raise SystemExit("no chunk files -- run build_v5_3_full_batch.py first")

    state = json.loads(IDS_FILE.read_text(encoding="utf-8")) if IDS_FILE.exists() else {}
    ok, bad = [], []

    for path in chunks:
        name = path.name
        if out_path(name).exists():
            n = sum(1 for _ in out_path(name).open(encoding="utf-8"))
            print(f"{name}: already downloaded ({n} responses) -- skipping")
            ok.append(name)
            continue

        # A recorded id may belong to a batch that FAILED; only reuse a live one.
        bid = state.get(name)
        if bid:
            b = client.batches.retrieve(bid)
            if b.status in ("failed", "expired", "cancelled"):
                print(f"{name}: previous batch {b.status} -- resubmitting")
                bid = None

        if not bid:
            n = sum(1 for _ in path.open(encoding="utf-8"))
            print(f"\n{name}: uploading ({n} requests, "
                  f"{path.stat().st_size / 1e6:.0f} MB) ...")
            up = client.files.create(file=path.open("rb"), purpose="batch")
            b = client.batches.create(input_file_id=up.id,
                                      endpoint="/v1/chat/completions",
                                      completion_window="24h")
            bid = b.id
            state[name] = bid
            IDS_FILE.write_text(json.dumps(state, indent=1), encoding="utf-8")
            print(f"   submitted {bid}")

        b = wait_for(client, bid, name[-8:-6])
        if b is None:
            bad.append(name)
            break
        if b.output_file_id:
            out_path(name).write_text(
                client.files.content(b.output_file_id).text, encoding="utf-8")
            print(f"   wrote {out_path(name).name}")
            ok.append(name)
        else:
            bad.append(name)
        if b.error_file_id:
            err = TEST_DIR / name.replace("batch", "errors")
            err.write_text(client.files.content(b.error_file_id).text,
                           encoding="utf-8")
            print(f"   wrote {err.name}  <-- ERRORS PRESENT")

    total = parsed = unparsed = 0
    for name in ok:
        p = out_path(name)
        if not p.exists():
            continue
        for line in p.open(encoding="utf-8"):
            total += 1
            try:
                json.loads(json.loads(line)["response"]["body"]["choices"][0]
                           ["message"]["content"])
                parsed += 1
            except Exception:                                      # noqa: BLE001
                unparsed += 1

    print(f"\n{'=' * 60}")
    print(f"chunks completed : {len(ok)}/{len(chunks)}")
    if bad:
        print(f"chunks NOT done  : {bad}   <-- re-run this script to retry")
    print(f"responses        : {total:,}   parsed {parsed:,}   unparseable {unparsed}")


if __name__ == "__main__":
    main()
